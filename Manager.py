import time

from Drone_Net import Drone_Net
from Drone_Net_Test import Drone_Net_Test
from Movement_Processing import Move_drone
from Movement_Processing import Movement_processing
from pyparrot_modified.pyparrot.Bebop import Bebop
from pyparrot_modified.pyparrot.DroneVisionGUI import DroneVisionGUI

while True:
    test_mode = input("Would you like to use the test mode? (Y/N): ").capitalize()
    if(test_mode == "Y"):
        test_mode = True
        break

    elif(test_mode == "N"):
        test_mode = False
        break
    else:
        print("Invalid input, enter either 'Y' or 'N'")


# this object computes the motion and then feeds it to
# 'Move_drone' which then actually moves the drone accordingly

process = Movement_processing()

# creates the bebop object and connects to it
bebop = Bebop()
success = bebop.connect(5)

# creates the object that moves the drone
move = Move_drone(bebop, process, success)

# creates the GUI that will initiate the video stream
# if testing is true video is streamed from the webcam (this has to be used
# in combination with Drone_Net_Test as the network
vision = DroneVisionGUI(bebop, move=move, process=process, is_bebop=True,
                        user_args=(bebop,), testing=test_mode)

# initialises neural net
if(test_mode):
    net = Drone_Net_Test(vision=vision, process=process)
else:
    net = Drone_Net(vision=vision, process=process)

vision.feed_net(net)
move.feed_net(net)

# starts the thread in which the network starts the
# the object detection
net.start()

# waits for the network to start up before starting the vision stream
print("sleeping for 10 seconds")
time.sleep(10)

# starting the vision stream
print("Starting Vision")
vision.start()

move.start()
print('move started')

# starts feeding movement information to the drone once everything else
# is up and running
