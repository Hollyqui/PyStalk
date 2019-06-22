import numpy as np

class Movement_processing:
    def __init__(self):
        self.rotation_dir = 0

    def get_rotation(self):
        return self.rotation_dir
    def compute(self, ymin,  xmin, ymax, xmax):
        y = ((ymin+ymax)/2 - 0.5)*100
        x = ((xmax+xmin)/2 - 0.5)*100
        self.rotation_dir = x

        return x ,y



