import random
import math
import os
import time
import pickle


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.frame = 0
        self.crash = 0
        self.FRONT_SENSOR_THRESHOLD = 11
        self.front_sensor = 0
        self.left_sensor = 0
        self.right_sensor = 0
        self.right_front_sensor = 0
        self.left_front_sensor = 0
        self._game_progress = {
            "scene_info": [],
            "action": []
        }

    def update(self, scene_info, keyboard=[], *args, **kwargs):
        # Define some constants
        MAX_SPEED = 255
        MIN_SPEED = -255
        ACCELERATION = 10
        TURN_SPEED = 40
        WALL_DISTANCE_THRESHOLD = 30
        TURN_SPEED_FACTOR = 3
        ANGLE_RECORD_INTERVAL = 30
        ANGLE_THRESHOLD = 10

        # Retrieve sensor values from the scene_info dictionary using the updated keys
        self.frame = scene_info["frame"]
        self.crash = scene_info["crash_count"]
        self.front_sensor = scene_info["F_sensor"]
        self.right_sensor = scene_info["R_sensor"]
        self.left_sensor = scene_info["L_sensor"]
        self.left_front_sensor = scene_info["L_T_sensor"]
        self.right_front_sensor = scene_info["R_T_sensor"]

        # Calculate the desired speed for each wheel based on the sensor values
        left_speed = 0
        right_speed = 0

        # if self.right_sensor > WALL_DISTANCE_THRESHOLD and not self.is_angle_between(scene_info["angle"], self.angle,
        #                                                                         ANGLE_THRESHOLD):
        if self.right_front_sensor > 30:
            # A path is detected on the right, turn right
            print("Path detected on the right, turning right")
            left_speed = MAX_SPEED
            right_speed = TURN_SPEED
            if self.stuck():
                left_speed = -50
                right_speed = -MAX_SPEED
        elif self.left_front_sensor < self.FRONT_SENSOR_THRESHOLD:
            # A wall is detected on the left front, turn slightly right
            print("Wall on the left front, turning slightly right")
            left_speed = MAX_SPEED
            right_speed = TURN_SPEED // 4
            if self.stuck():
                # If a wall is detected in front, go backward
                left_speed = -50
                right_speed = -MAX_SPEED
        elif self.right_front_sensor < self.FRONT_SENSOR_THRESHOLD:
            # A wall is detected on the right front, turn slightly left
            print("Wall on the right front, turning slightly left")
            left_speed = TURN_SPEED // 4
            right_speed = MAX_SPEED
            if self.stuck():
                # If a wall is detected in front, go backward
                left_speed = -MAX_SPEED
                right_speed = -50
        elif self.front_sensor < self.left_front_sensor:
            # Turn slightly left
            print("Turning slightly left")
            turn_speed = TURN_SPEED_FACTOR * (self.left_front_sensor - self.front_sensor)
            left_speed = min(MAX_SPEED, max(-MAX_SPEED, TURN_SPEED - turn_speed))
            right_speed = MAX_SPEED
            if self.front_sensor < self.FRONT_SENSOR_THRESHOLD / 2:
                left_speed = -MAX_SPEED
                right_speed = -50
        elif self.front_sensor < self.right_front_sensor:
            # Turn slightly right
            print("Turning slightly right")
            turn_speed = TURN_SPEED_FACTOR * (self.right_front_sensor - self.front_sensor)
            left_speed = MAX_SPEED
            right_speed = min(MAX_SPEED, max(-MAX_SPEED, TURN_SPEED - turn_speed))
            if self.front_sensor < self.FRONT_SENSOR_THRESHOLD / 2:
                left_speed = -50
                right_speed = -MAX_SPEED
        else:
            # No obstacle, go forward randomly
            direction = random.choices(["LEFT", "RIGHT", "FRONT"], weights=[1, 1, 2], k=1)[0]
            print(direction)
            if direction == "LEFT":
                left_speed = TURN_SPEED // 2
                right_speed = MAX_SPEED
            elif direction == "RIGHT":
                left_speed = MAX_SPEED
                right_speed = TURN_SPEED // 2
            else:
                left_speed = MAX_SPEED
                right_speed = MAX_SPEED

        control_list = {"left_PWM": left_speed, "right_PWM": right_speed}
        self.record(scene_info, control_list)
        # Return the speed of both left and right wheel as a dictionary
        return control_list

    def stuck(self, turn_right=False):
        if turn_right:
            if self.front_sensor < self.FRONT_SENSOR_THRESHOLD:
                return True
        else:
            if self.front_sensor < self.FRONT_SENSOR_THRESHOLD / 2:
                return True
        if self.left_sensor < self.FRONT_SENSOR_THRESHOLD / 4 and self.left_front_sensor < self.FRONT_SENSOR_THRESHOLD / 4:
            return True
        if self.right_sensor < self.FRONT_SENSOR_THRESHOLD / 4 and self.right_front_sensor < self.FRONT_SENSOR_THRESHOLD / 4:
            return True
        return False

    def record(self, scene_info, control_list):
        self._game_progress["scene_info"].append(scene_info)
        self._game_progress["action"].append(control_list)

    def reset(self):
        """
        Reset the status
        """
        self.flush_to_file('6', self.crash, self.frame)
        pass

    def flush_to_file(self, map_name, crash_cnt, frame_used):
        """
        Flush the stored objects to the file
        """
        filename = "{}_{}_{}_".format(map_name, crash_cnt, frame_used) + time.strftime("%m%d_%H-%M-%S") + ".pickle"
        if not os.path.exists(os.path.dirname(__file__) + "/log"):
            os.makedirs(os.path.dirname(__file__) + "/log")
        filepath = os.path.join(os.path.dirname(__file__), "./log/" + filename)
        # Write pickle file
        with open(filepath, "wb") as f:
            pickle.dump(self._game_progress, f)

        # Clear list
        self._game_progress["scene_info"].clear()
        self._game_progress["action"].clear()
