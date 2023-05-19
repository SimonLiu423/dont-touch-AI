import torch.nn as nn


class QNet(nn.Module):
    def __init__(self, input_shape, output_shape):
        super(QNet, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_shape[0], 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_shape),
        )

    def forward(self, x):
        return self.fc(x)

