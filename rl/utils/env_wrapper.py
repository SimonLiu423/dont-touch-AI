import numpy as np


class EnvWrapper:
    def __init__(self, map_length=200, quantize_factor=5, action_bins=5):
        self.map_length = map_length
        self.quantize_factor = quantize_factor
        self.interval = map_length / quantize_factor
        self.visited = np.zeros(self.quantize_factor ** 2)
        self.state_shape = (37,)
        self.action_bins = action_bins
        self.n_actions = action_bins * action_bins
        self.MAX_SPEED = 255
        self.speed = np.linspace(-self.MAX_SPEED, self.MAX_SPEED, action_bins)

        self.scene_info = None
        self.state = None
        self.reward = 0
        self.new_section = False

    def update(self, new_scene, action):
        new_scene["section"] = self.pos_section(new_scene)
        new_scene["visited"] = (self.visited[new_scene["section"]] == 1)

        frame = new_scene["frame"]
        x = new_scene["x"]
        y = new_scene["y"]
        # angle = new_scene["angle"]
        r_s = new_scene["R_sensor"]
        l_s = new_scene["L_sensor"]
        f_s = new_scene["F_sensor"]
        lt_s = new_scene["L_T_sensor"]
        rl_s = new_scene["R_T_sensor"]
        end_x = new_scene["end_x"]
        end_y = new_scene["end_y"]
        crash_cnt = new_scene["crash_count"]
        section = new_scene["section"]

        self.new_section = False
        if self.scene_info is not None and section != self.scene_info["section"]:
            if self.visited[section] == 0:
                self.new_section = True
                self.visited[section] = -1
            prev_section = self.scene_info["section"]
            self.visited[prev_section] = 1
        elif self.scene_info is None:
            self.visited[section] = -1

        self.update_reward(self.scene_info, action, new_scene)

        self.scene_info = new_scene
        self.state = np.array([frame, x, y, r_s, l_s, f_s, lt_s, rl_s, end_x, end_y, crash_cnt, section])
        self.state = np.concatenate([self.state, self.visited])
        assert(self.state.shape == self.state_shape)

    def update_reward(self, scene, action, next_scene):
        if scene is None or action is None:
            self.reward = 0
            return

        if scene["status"] == "GAME_PASS":
            self.reward = 5
            return

        speed = self.convert_action(action)
        r_sensor = scene["R_sensor"]
        l_sensor = scene["L_sensor"]
        f_sensor = scene["F_sensor"]
        rt_sensor = scene["R_T_sensor"]
        lt_sensor = scene["L_T_sensor"]
        vis = scene["visited"]

        touched = (scene["crash_count"] + 1 == next_scene["crash_count"])

        self.reward = 0

        if touched:
            self.reward -= 10
            return

        if vis:
            self.reward -= 0.2

        if speed["left_PWM"] > 0 and speed["right_PWM"] > 0:
            if not vis and f_sensor == max(f_sensor, l_sensor, r_sensor, lt_sensor, rt_sensor):
                self.reward += 0.5
        elif speed["left_PWM"] < 0 and speed["right_PWM"] < 0:
            self.reward -= 0.05
        elif lt_sensor > f_sensor:
            if speed["right_PWM"] > speed["left_PWM"] >= 0:
                self.reward += 0.2
        elif rt_sensor > f_sensor:
            if speed["left_PWM"] > speed["right_PWM"] >= 0:
                self.reward += 0.2

        if self.new_section:
            self.reward += 1

    def convert_action(self, action):
        left_action = action // self.action_bins
        right_action = action % self.action_bins
        return {"left_PWM": self.speed[left_action], "right_PWM": self.speed[right_action]}

    def pos_section(self, scene_info):
        row = scene_info["y"] // self.interval
        col = scene_info["x"] // self.interval
        return int(row * self.quantize_factor + col)

    def reset(self):
        self.__init__()
