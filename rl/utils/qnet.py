import torch.nn as nn


class QNet(nn.Module):
    def __init__(self, input_shape, output_shape):
        super(QNet, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_shape[0], 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, output_shape),
        )

    def forward(self, x):
        return self.fc(x)

