import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import threading

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from Movement_Processing import Movement_processing


class Drone_Net(threading.Thread):
    def __init__(self, vision, process):
        self.process = process
        threading.Thread.__init__(self)
        # Define the video stream
        self.cap = cv2.VideoCapture(0)  # Change only if you have more than one webcams
        self.vision = vision
        # What model to download.
        # Models can bee found here: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
        MODEL_NAME = 'ssd_inception_v2_coco_2018_01_28'
        MODEL_FILE = MODEL_NAME + '.tar.gz'
        DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

        # List of the strings that is used to add correct label for each box.
        PATH_TO_LABELS = os.path.join('object_detection/data', 'mscoco_label_map.pbtxt')

        # Number of classes to detect
        NUM_CLASSES = 90

        # Download Model
        opener = urllib.request.URLopener()

        already_downloaded = input("Enter 'Y' if the network is already downloaded; 'N' if it isn't: ")
        if (already_downloaded == "N"):
            opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
        tar_file = tarfile.open(MODEL_FILE)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd())

        # Load a (frozen) Tensorflow model into memory.

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # Loading label map
        # Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    # Helper code
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

    def run(self):

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph, config=config) as sess:
                while True:
                    # Read frame from camera
                    image_np = self.vision.get_latest_valid_picture()
                    # print(image_np)
                    # ret, image_np = self.cap.read()
                    if (image_np is not None):
                        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                        image_np_expanded = np.expand_dims(image_np, axis=0)
                        # Extract image tensor
                        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                        # Extract detection boxes
                        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                        # Extract detection scores
                        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                        # Extract detection classes
                        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                        # Extract number of detectionsd
                        num_detections = self.detection_graph.get_tensor_by_name(
                            'num_detections:0')
                        # Actual detection.
                        (boxes, scores, classes, num_detections) = sess.run(
                            [boxes, scores, classes, num_detections],
                            feed_dict={image_tensor: image_np_expanded})
                        # Visualization of the results of a detection.
                        # vis_util.visualize_boxes_and_labels_on_image_array(
                        #     image_np,
                        #     np.squeeze(boxes),
                        #     np.squeeze(classes).astype(np.int32),
                        #     np.squeeze(scores),
                        #     self.category_index,
                        #     use_normalized_coordinates=True,
                        #     line_thickness=8,
                        #     only_get=1)
                        box = vis_util.get_box_coordinates(image_np,
                                                           np.squeeze(boxes),
                                                           np.squeeze(classes).astype(np.int32),
                                                           np.squeeze(scores),
                                                           self.category_index,
                                                           use_normalized_coordinates=True,
                                                           line_thickness=8,
                                                           only_get=1)
                        #print("box:", box)
                        box = np.array(box)
                        if(not box.sum() == 0):
                            box = box[0]
                         #   print(box)
                            self.process.compute(box[0], box[1], box[2], box[3])
                            #print("something")
                    # cv2.imshow('object detection', cv2.resize(image_np, (800, 600)))
                    #
                    # if cv2.waitKey(10) & 0xFF == ord('q'):
                    #     cv2.destroyAllWindows()
                    #     break

    # get the box dimensions