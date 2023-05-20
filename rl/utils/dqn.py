import os
import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F


class DeepQNet:
    def __init__(
            self,
            obs_shape,
            n_actions,
            qnet,
            replace_target_iter=1000,
            memory_size=10000,
            learning_rate=2e-4,
            reward_decay=0.99,
            batch_size=32,
            device='cpu',
    ):
        self.obs_shape = obs_shape
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = reward_decay
        self.batch_size = batch_size
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.memory = None
        self.init_memory()
        self.memory_counter = 0
        self.learn_step_counter = 0
        self.device = device

        self.eval_net = qnet(self.obs_shape, n_actions).to(device)
        self.target_net = qnet(self.obs_shape, n_actions).to(device)
        self.target_net.eval()
        self.optimizer = optim.RMSprop(params=self.eval_net.parameters(), lr=self.lr)

    def choose_action(self, state, epsilon):
        if np.random.random() < epsilon:
            action = np.random.randint(0, self.n_actions)
        else:
            # add batch dim (4, 84, 84) => (1, 4, 84, 84) and predict
            predict_q = self.eval_net(torch.FloatTensor(state).unsqueeze(0).to(self.device))
            action = torch.argmax(predict_q, 1).cpu().numpy()[0]
        assert type(action) in [int, np.int64], 'action type = {}, shape = {}'.format(action.dtype, action.shape)
        return action

    def learn(self):
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())

        if self.memory_counter < self.memory_size:
            sample_index = np.random.choice(self.memory_counter, self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_size, self.batch_size)

        b_s = torch.FloatTensor(self.memory["s"][sample_index]).to(self.device)
        b_a = torch.LongTensor(self.memory["a"][sample_index]).to(self.device)
        b_r = torch.FloatTensor(self.memory["r"][sample_index]).to(self.device)
        b_s_ = torch.FloatTensor(self.memory["s_"][sample_index]).to(self.device)
        b_d = torch.FloatTensor(self.memory["done"][sample_index]).to(self.device)

        predict_q = self.eval_net(b_s).gather(1, b_a)
        target_next_q = self.target_net(b_s_).max(1)[0].view(-1, 1)
        target_q = b_r + (1 - b_d) * self.gamma * target_next_q

        loss = F.smooth_l1_loss(predict_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.learn_step_counter += 1
        return loss.item()

    def init_memory(self):
        self.memory = {
            "s": np.zeros((self.memory_size, *self.obs_shape)),
            "a": np.zeros((self.memory_size, 1)),
            "r": np.zeros((self.memory_size, 1)),
            "s_": np.zeros((self.memory_size, *self.obs_shape)),
            "done": np.zeros((self.memory_size, 1)),
        }

    def save_load_model(self, op, file_name='qnet.pt', save_dir='save'):
        path = os.path.dirname(__file__)
        path = os.path.join(path, save_dir)
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, file_name)
        if op == 'save':
            torch.save(self.eval_net.state_dict(), path)
        elif op == 'load':
            self.eval_net.load_state_dict(torch.load(path))
            self.target_net.load_state_dict(torch.load(path))

    def save_transition(self, s, a, r, s_, done):
        index = self.memory_counter % self.memory_size
        self.memory["s"][index] = s
        self.memory["a"][index] = a
        self.memory["r"][index] = r
        self.memory["s_"][index] = s_
        self.memory["done"][index] = done
        self.memory_counter += 1
