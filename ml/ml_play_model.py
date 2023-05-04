import os
import pickle


class MLPlay:
    def __init__(self, *args, **kwargs):
        with open(
            os.path.join(os.path.dirname(__file__), "save", "model2.pickle"), "rb"
        ) as f:
            self.model = pickle.load(f)

    def update(self, scene_info, *args, **kwargs):
        if scene_info["frame"] < 2:
            return {"left_PWM": 0, "right_PWM": 0}

        TURN_THRESHOLD = 5
        MAX_SPEED = 255
        TURN_SPEED = 255
        left_speed = 0
        right_speed = 0

        state = [
            [
                scene_info["F_sensor"],
                scene_info["L_sensor"],
                scene_info["R_sensor"],
                scene_info["L_T_sensor"],
                scene_info["R_T_sensor"],
                scene_info["x"],
                scene_info["y"],
                # scene_info["end_x"],
                # scene_info["end_y"],
                scene_info["angle"],
            ]
        ]
        action = self.model.predict(state)
        left_speed = action[0][0]
        right_speed = action[0][1]

        return {"left_PWM": left_speed, "right_PWM": right_speed}

    def reset(self):
        pass