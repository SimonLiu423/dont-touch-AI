import os
from rl.utils.qnet import QNet
from rl.utils.dqn import DeepQNet
from rl.utils.env_wrapper import EnvWrapper


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.env = EnvWrapper()
        self.agent = DeepQNet(self.env.state_shape, self.env.n_actions, QNet, device='cuda')

        self.agent.save_load_model(op='load', save_dir=os.path.dirname(__file__))
        self.agent.eval_net.eval()
        self.agent.target_net.eval()

        self.total_reward = 0
        self.action = None

    def update(self, scene_info, keyboard=[], *args, **kwargs):
        self.env.update(scene_info, self.action)

        self.total_reward = self.env.reward

        self.action = self.agent.choose_action(self.env.state, epsilon=0)

        return self.env.convert_action(self.action)

    def reset(self):
        """
        Reset the status
        """
        print("Reward: {}".format(self.total_reward))
        self.env.reset()
        pass

