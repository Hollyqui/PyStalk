import threading
from  pyparrot_modified.pyparrot.Bebop import Bebop


class Movement_processing:
    def __init__(self):
        self.rotation_dir = 0
        self.velocity = 0
        self.x_avg = 0
        self.y_avg = 0
        self.box_size = 0
        self.pitch = 0
        self.value = 0
        self.max_box_size = 0.25
        self.min_box_size = 0.2
        self.tilt = 0


    def compute(self, ymin, xmin, ymax, xmax):
        self.y_avg = (ymin + ymax) / 2
        self.x_avg = (xmin + xmax) / 2
        self.box_size = abs((ymax - ymin) * (xmax - xmin))
        y = ((ymin + ymax) / 2 - 0.5) * 40
        x = ((xmax + xmin) / 2 - 0.5) * 30
        self.rotation_dir = x
        self.tilt = y * (-1)
        self.set_distance()

    # getters:
    def get_tilt(self):
        return self.tilt

    def get_pitch(self):
        return self.pitch

    def get_rotation(self):
        return self.rotation_dir

    def get_min_box_size(self):
        return self.min_box_size

    def get_max_box_size(self):
        return self.max_box_size

    # setters:
    def set_tilt(self, tilt):
        self.tilt = tilt
    def set_pitch(self, pitch):
        self.pitch = pitch
    def set_rotation(self, rotation):
        self.rotation_dir = rotation


    def set_distance(self):

        if (self.box_size > 0):
            if self.box_size > self.max_box_size:
                if(self.max_box_size == 0):
                    self.max_box_size = 0.05
                self.pitch = (self.box_size/self.max_box_size) * -3
            elif self.box_size < self.min_box_size:
                self.pitch = (self.min_box_size/self.box_size) * 3
            else:
                self.pitch = 0
            # self.pitch = (self.box_size-((self.min_box_size+self.max_box_size)/2))*(-30)

        else:
            self.pitch = 0

    def set_max_box_size(self, max):
        self.max_box_size = max

    def set_min_box_size(self, min):
        self.min_box_size = min


class Move_drone(threading.Thread):
    def __init__(self, bebop, process):
        """
        :param user_function: user code to run (presumably flies the drone)
        :param user_args: optional arguments to the user function
        """
        threading.Thread.__init__(self)
        self.net = None
        self.bebop = bebop
        self.process = process
        self.distance = 0.5  # the area of the screen that should be taken up by the box
        self.killed = False
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.vertical_movement = 0
        self.value = 0
        self.tilt = 0
        self.camera_angle = 0
        self.hovering = True
        self.rotate = False

    def feed_net(self, net):
        self.net = net

    #makes the drone rotate
    def discombobulation(self):
        if(self.killed == False):
            self.bebop.fly_direct(roll=0 , yaw=10, pitch=0, vertical_movement=0, duration=0.1)

    # kills the drone and prevents any further movement from being passed on
    def kill(self):
        self.killed = True
        print("Drone Killed")
        self.bebop.emergency_land()

    def raise_drone(self):
        if(self.killed == False):
            print("Drone is rising")
            self.bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=10, duration=1)

    def lower_drone(self):
        if(self.killed == False):
            print("Drone is lowering")
            self.bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=-10, duration=1)

    def drone_left(self):
        if(self.killed == False):
            print("Drone is going left")
            self.bebop.fly_direct(roll=-10, pitch=0, yaw=0, vertical_movement=0, duration=1)

    def drone_right(self):
        if(self.killed == False):
            print("Drone is going right")
            self.bebop.fly_direct(roll=10, pitch=0, yaw=0, vertical_movement=0, duration=1)

    def drone_forward(self):
        if(self.killed == False):
            print("Drone is going forward")
            self.bebop.fly_direct(roll=-0, pitch=10, yaw=0, vertical_movement=0, duration=1)

    def drone_backward(self):
        if(self.killed == False):
            print("Drone is going backward")
            self.bebop.fly_direct(roll=-0, pitch=-10, yaw=0, vertical_movement=0, duration=1)

    def rotate_true(self):
        print("Drone is now tracking with variable rotation")
        self.rotate = True

    def rotate_false(self):
        print("Drone is now tracking with fixed rotation")
        self.rotate = False

    def restart(self):
        self.killed = False
        self.bebop.safe_takeoff(5)

    def drone_hover(self):
        if (self.killed == False and self.hovering == False):
                print("Drone is hovering")
                self.hovering = True
                self.yaw = 0
                self.pitch = 0
                self.roll = 0
                self.vertical_movement = 0
                self.bebop.fly_direct(roll=-0, pitch=0, yaw=0, vertical_movement=0, duration=1)
        if (self.killed == False and self.hovering == True):
            print("Drone is tracking")
            self.hovering = False

    # the function that feeds the movement; runs as a separate thread
    def run(self):
        # self.bebop.safe_takeoff(5)
        self.bebop.set_video_resolutions('rec1080_stream420')
        self.bebop.set_video_recording('time')
        self.bebop.set_video_stream_mode('low_latency')
        #makes the drone patroll if no target is detected


        # moves the drone as long as it wasn't killed
        while(self.killed == False):
            if((not self.camera_angle ==-60 or not self.camera_angle ==  60) and self.hovering == False):
                self.yaw = self.process.get_rotation()
                self.tilt = self.process.get_tilt()
                self.pitch = self.process.get_pitch()
                # if(self.net.get_adjusted_box() is None):
                #     self.discombobulation()
                #     print("Drone Discombobulated")
                # # rotates to track object's left/right movement
                # else:
                if(self.rotate == True):
                    self.bebop.fly_direct(roll=0, yaw=self.yaw, pitch=self.pitch, vertical_movement=0, duration=0.1)
                # moves left/right itself to track object's left/right movement
                elif(self.rotate == False):
                    self.bebop.fly_direct(roll=self.yaw, yaw=0, pitch=self.pitch, vertical_movement=0, duration=0.1)
                # if 60 >= self.camera_angle >= -60:
                self.bebop.pan_tilt_camera_velocity(tilt_velocity=self.tilt, pan_velocity=0, duration=0.1)
                self.camera_angle += self.tilt*0.1

    # all the getter functions:
    def get_pitch(self):
        return self.pitch

    def get_tilt(self):
        return self.tilt

    def get_vertical_movement(self):
        return self.vertical_movement

    def get_roll(self):
        return self.roll

    def get_yaw(self):
        return self.yaw

    def get_pitch(self):
        return self.pitch

    def land(self):
        self.bebop.land()

    # the value variable determines how much of the screen the object should cover
    def get_value(self):
        return self.value
