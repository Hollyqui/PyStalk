import threading
from Drone_Net import Drone_Net
from pyparrot_modified.pyparrot.DroneVisionGUI import DroneVisionGUI
from pyparrot_modified.pyparrot.Bebop import Bebop
from Movement_Processing import Movement_processing
from Movement_Processing import Move_drone
import time


class testThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print("x")

process = Movement_processing()


# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)


move = Move_drone(bebop, process)
print("GUI created")

vision = DroneVisionGUI(bebop, move=move, process=process, is_bebop=True,
                        user_args=(bebop,))

#GUI.run()
print("initialising neural net")
net = Drone_Net(vision=vision, process=process)
print("Initialising Vision Stream")

# vision = DroneVision(bebop, is_bebop=True)
print("starting detection")
net.start()

print("sleeping for 10 seconds")
time.sleep(10)
# for i in range(10):
#     print(10-i, " seconds left until vision starts!")
#     time.sleep(1)
print("woke up")

print("Starting Vision")
vision.start()
move.start()