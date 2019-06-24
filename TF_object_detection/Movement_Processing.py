import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QSlider, QHBoxLayout, QPushButton, \
    QVBoxLayout, QAction, QFileDialog, QApplication, QLabel
import sys
from tkinter import *
import multiprocessing
import threading
import time
import logging

class Movement_processing:
    def __init__(self):
        self.rotation_dir = 0
        self.velocity = 0
        self.x_avg = 0
        self.y_avg = 0
        self.box_size = 0
        self.pitch = 0
        self.value = 0
    def get_rotation(self):
        return self.rotation_dir
    def get_velocity(self):
        return self.velocity
    def get_box_size(self):
        return self.box_size


    def compute(self, ymin,  xmin, ymax, xmax):
        self.y_avg = (ymin+ymax)/2
        self.x_avg = (xmin+xmax)/2
        self.box_size = abs((ymax-ymin)*(xmax-xmin))*3
        # print("box bounds:", ymin, ymax, xmin, xmax)
        #print("size:", self.box_size)
        # print("yaw:", self.rotation_dir)
        # print("pitch:", self.velocity)
        y = ((ymin+ymax)/2 - 0.5)*40
        x = ((xmax+xmin)/2 - 0.5)*40
        self.rotation_dir = x
        self.velocity = y
        self.set_distance(self.value)
    def set_distance(self, value):
        self.value = value
        if(self.box_size > 0):
            if(abs(self.box_size-value)*(-30)<=10):
                self.pitch = self.box_size-value*-30
            else:
                self.pitch = 0 
        else:
            self.pitch = 0

    def get_pitch(self):
        return self.pitch

class Move_drone(threading.Thread):
    def __init__(self, bebop, process):
        """
        :param user_function: user code to run (presumably flies the drone)
        :param user_args: optional arguments to the user function
        """
        threading.Thread.__init__(self)
        self.bebop = bebop
        self.process = process
        self.distance = 0.5 # the area of the screen that should be taken up by the box
        self.killed = False
        self.velocity = 0
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.vertical_movement = 0
        self.value = 0

    # def __del__(self):
    #     self.wait()

    def get_yaw(self):
        return self.yaw

    def get_pitch(self):
        return self.pitch

    def land(self):
        self.bebop.land()
    def get_value(self):
        return self.value

    def kill(self):
        self.killed = True
        print("Drone Killed")
        self.bebop.emergency_land()


    def run(self):
        self.bebop.safe_takeoff(5)
        #self.bebop.fly_direct(roll=0, yaw=0, pitch=0, vertical_movement=10, duration=3)
        while self.killed == False:
            self.yaw = self.process.get_rotation()
            self.pitch = self.process.get_pitch()
            self.bebop.fly_direct(roll=0, yaw=self.yaw, pitch=self.pitch, vertical_movement=0, duration=0.1)
