import threading


class Movement_processing:
    def __init__(self):
        self.rotation_dir = 0
        self.velocity = 0
        self.x_avg = 0
        self.y_avg = 0
        self.box_size = 0
        self.pitch = 0
        self.value = 0
        self.max_distance = 0
        self.min_distance = 0

    def get_rotation(self):
        return self.rotation_dir

    def get_velocity(self):
        return self.velocity

    def get_box_size(self):
        return self.box_size

    def compute(self, ymin, xmin, ymax, xmax):
        self.y_avg = (ymin + ymax) / 2
        self.x_avg = (xmin + xmax) / 2
        self.box_size = abs((ymax - ymin) * (xmax - xmin))
        y = ((ymin + ymax) / 2 - 0.5) * 40
        x = ((xmax + xmin) / 2 - 0.5) * 40
        self.rotation_dir = x
        self.velocity = y
        self.set_distance()

    def set_distance(self):

        if (self.box_size > 0):
            if self.box_size > self.max_distance:
                self.pitch = (self.box_size - self.max_distance) * -30
            elif self.box_size < self.min_distance:
                self.pitch = (self.box_size - self.min_distance) * -30
            else:
                self.pitch = 0

        else:
            self.pitch = 0

    def get_pitch(self):
        return self.pitch
    def set_max_distance(self, max):
        self.max_distance = max

    def set_min_distance(self, min):
        self.min_distance = min


class Move_drone(threading.Thread):
    def __init__(self, bebop, process):
        """
        :param user_function: user code to run (presumably flies the drone)
        :param user_args: optional arguments to the user function
        """
        threading.Thread.__init__(self)
        self.bebop = bebop
        self.process = process
        self.distance = 0.5  # the area of the screen that should be taken up by the box
        self.killed = False
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.vertical_movement = 0
        self.value = 0

    # kills the drone and prevents any further movement from being passed on.
    def kill(self):
        self.killed = True
        print("Drone Killed")
        self.bebop.emergency_land()

    # the function that feeds the movement; runs as a separate thread
    def run(self):
        #self.bebop.safe_takeoff(5)

        # moves the drone as long as it wasn't killed
        while self.killed == False:
            self.yaw = self.process.get_rotation()
            self.pitch = self.process.get_pitch()
            #self.bebop.fly_direct(roll=0, yaw=self.yaw, pitch=self.pitch, vertical_movement=0, duration=0.1)

    # all the getter functions:
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
