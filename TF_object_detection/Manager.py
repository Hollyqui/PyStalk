import time

from Drone_Net import Drone_Net
from Movement_Processing import Move_drone
from Movement_Processing import Movement_processing
from pyparrot_modified.pyparrot.Bebop import Bebop
from pyparrot_modified.pyparrot.DroneVisionGUI import DroneVisionGUI

# this object computes the motion and then feeds it to
# 'Move_drone' which then actually moves the drone accordinly
process = Movement_processing()

# creates the bebop object and connects to it
bebop = Bebop()
bebop.connect(5)

# creates the object that moves the drone
move = Move_drone(bebop, process)

# creates the GUI that will initiate the video stream
vision = DroneVisionGUI(bebop, move=move, process=process, is_bebop=True,
                        user_args=(bebop,))

# initialises neural net
net = Drone_Net(vision=vision, process=process)

# starts the thread in which the network starts the
# the object detection
net.start()

# waits for the network to start up before starting the vision stream
print("sleeping for 10 seconds")
time.sleep(10)

# starting the vision stream
print("Starting Vision")
vision.start()

# starts feeding movement information to the drone once everything else
# is up and running
move.start()
