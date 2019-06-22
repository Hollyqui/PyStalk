import threading
from Drone_Net import Drone_Net
from pyparrot_modified.pyparrot.DroneVisionGUI import DroneVisionGUI
from pyparrot_modified.pyparrot.DroneVision import DroneVision
from pyparrot_modified.pyparrot.Bebop import Bebop
from Movement_Processing import Movement_processing
import time


class testThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)


    def run(self):
        while True:
            print("x")


move = Movement_processing()
def demo_user_code_after_vision_opened(args):
    bebop = args[0]

    print("Vision successfully started!")
    # removed the user call to this function (it now happens in open_video())
    # bebopVision.start_video_buffering()

    # takeoff
    bebop.safe_takeoff(5)

    move.get_rotation()


# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)

vision = DroneVisionGUI(bebop, move=move, is_bebop=True, user_code_to_run=demo_user_code_after_vision_opened,
                        user_args=(bebop,))

print("initialising neural net")
net = Drone_Net(vision, move)
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
