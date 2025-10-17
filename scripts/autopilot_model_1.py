import torch
import torch.nn as nn
import numpy as np
from PyQt6 import QtWidgets
from data_collector import DataCollectionUI

class DrivingNN(nn.Module):
    def __init__(self):
        super(DrivingNN, self).__init__()
        self.layer1 = nn.Linear(16, 32)
        self.layer2 = nn.Linear(32, 4)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        x = self.sigmoid(x)
        return x

class NNMsgProcessor:
    def __init__(self):
        self.model = DrivingNN()
        self.model.load_state_dict(torch.load('Data_Analysis/driving_model.pth'))
        self.model.eval()

    def nn_infer(self, message):
        raycasts = list(message.raycast_distances)
        speed = message.car_speed

        input_data = raycasts + [speed]
        input_tensor = torch.FloatTensor(input_data).unsqueeze(0)

        with torch.no_grad():
            output = self.model(input_tensor)

        predictions = output[0].numpy()

        # DEBUG: Print predictions
        print(f"Predictions: Forward={predictions[0]:.3f}, Back={predictions[1]:.3f}, Left={predictions[2]:.3f}, Right={predictions[3]:.3f}")

        commands = []
        control_names = ["forward", "back", "left", "right"]

        for i, control in enumerate(control_names):
            threshold = 0.2 if control == "forward" else 0.5
            if predictions[i] > threshold:
                commands.append((control, True))
            else:
                commands.append((control, False))

        return commands

    def process_message(self, message, data_collector):
        commands = self.nn_infer(message)

        for command, start in commands:
            data_collector.onCarControlled(command, start)

if __name__ == "__main__":
    import sys
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook

    app = QtWidgets.QApplication(sys.argv)

    nn_brain = NNMsgProcessor()
    data_window = DataCollectionUI(nn_brain.process_message)
    data_window.show()

    app.exec()