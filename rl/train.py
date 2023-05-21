import os

import torch
import torch.nn
import numpy as np
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
from rl.utils.qnet import QNet
from rl.utils.dqn import DeepQNet
from rl.utils.env_wrapper import EnvWrapper
from src.Dont_touch import Dont_touch
from mlgame.game.generic import quit_or_esc


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        self.writer = SummaryWriter()
        self.env = EnvWrapper()
        self.agent = DeepQNet(self.env.state_shape, self.env.n_actions, QNet, device='cuda')
        self.agent.save_load_model(op='load', save_dir=os.path.dirname(__file__))
        self.episodes = 0
        self.steps = 0
        self.total_steps = 0
        self.total_rewards = 0
        self.total_rewards_hist = []
        self.best_mean_reward = None
        self.loss = None
        self.eps = None

        self.prev_state = None
        self.action = None

    def update(self, scene_info, keyboard=[], *args, **kwargs):
        self.env.update(scene_info, self.action)
        self.eps = self.calc_epsilon(self.total_steps)
        self.writer.add_scalar('Epsilon/train/step', self.eps, self.total_steps)

        reward = self.env.reward
        done = scene_info["status"] in ["GAME_PASS", "GAME_OVER"]

        self.total_rewards += reward

        if self.prev_state is not None:
            self.agent.save_transition(self.prev_state, self.action, reward, self.env.state, done)
        if self.agent.memory_counter >= 4 * self.agent.batch_size:
            self.loss = self.agent.learn()
            self.writer.add_scalar('Loss/train/step', self.loss, self.total_steps)

        self.prev_state = self.env.state
        self.action = self.agent.choose_action(self.env.state, epsilon=self.eps)
        self.steps += 1
        self.total_steps += 1

        if self.steps % 100 == 0:
            print('\rStep: {} | Reward: {}/{}'.format(self.steps, reward, self.total_rewards), end="")

        return self.env.convert_action(self.action)

    def calc_epsilon(self, step, epsilon_max=1, min_epsilon=0.05, epsilon_decay=500000):
        return min_epsilon + (epsilon_max - min_epsilon) * np.exp(-step / epsilon_decay)

    def reset(self):
        """
        Reset the status
        """
        self.writer.add_scalar("Reward/train/step", self.total_rewards, self.total_steps)
        self.writer.add_scalar("Reward/train/episode", self.total_rewards, self.episodes)
        self.total_rewards_hist.append(self.total_rewards)
        if len(self.total_rewards_hist) == 31:
            self.total_rewards_hist.pop(0)
            mean_reward = np.mean(self.total_rewards_hist)
            if self.best_mean_reward is None or mean_reward > self.best_mean_reward:
                self.best_mean_reward = mean_reward
                self.agent.save_load_model(op='save', save_dir=os.path.dirname(__file__))
        print('\rEpisode: {:3d} | Steps: {}/{} | Reward: {} | Loss : {} | Epsilon: {}'.format(
            self.episodes, self.steps, self.total_steps, self.total_rewards, self.loss, self.eps
        ))
        self.auto_save()
        self.env.reset()
        self.prev_state = None
        self.action = None
        self.episodes += 1
        self.steps = 0
        self.total_rewards = 0
        pass

    def auto_save(self):
        if self.episodes % 10 == 0:
            now = datetime.now()
            fname = 'Episode_{}_{}{}_{}{}.pt'.format(str(self.episodes).zfill(4), str(now.month).zfill(2),
                                                     str(now.day).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2))
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autosave', fname)
            torch.save(self.agent.target_net.state_dict(), model_path)


