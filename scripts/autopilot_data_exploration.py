

from PyQt6 import QtWidgets
from data_collector import DataCollectionUI

import random

"""
This file is provided as an example of what a simplistic controller could be done.
It simply uses the DataCollectionUI interface zo receive sensing_messages and send controls.

/!\ Be warned that if the processing time of NNMsgProcessor.process_message is superior to the message reception period, a lag between the images processed and commands sent.
One might want to only process the last sensing_message received, etc. 
Be warned that this could also cause crash on the client side if socket sending buffer overflows

/!\ Do not work directly in this file (make a copy and rename it) to prevent future pull from erasing what you write here.
"""


class ExampleNNMsgProcessor:
    def __init__(self):
        self.always_forward = True

    def nn_infer(self, message):
        print("=== Sensor Data_Analysis ===")
        print(f"Raycast distances: {message.raycast_distances}")
        print(f"Car speed: {message.car_speed}")
        print(f"Car angle: {message.car_angle}")
        print(f"Car position: {message.car_position}")
        print(f"Current controls: {message.current_controls}")
        print(f"Image shape: {message.image.shape if message.image is not None else 'No image'}")
        print("=" * 40)

        commands = [("forward", True)]

        # 10% chance to turn
        if random.random() < 0.1:
            turn = random.choice(["left", "right"])
            commands.append((turn, True))
        else:
            # Release both turn keys when not turning
            commands.append(("left", False))
            commands.append(("right", False))

        return commands

    def process_message(self, message, data_collector):

        commands = self.nn_infer(message)

        for command, start in commands:
            data_collector.onCarControlled(command, start)

if  __name__ == "__main__":
    import sys
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook

    app = QtWidgets.QApplication(sys.argv)

    nn_brain = ExampleNNMsgProcessor()
    data_window = DataCollectionUI(nn_brain.process_message)
    data_window.show()

    app.exec()