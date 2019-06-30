import os
import tarfile
import threading

import cv2
import numpy as np
import six.moves.urllib as urllib
import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


class Drone_Net_Test(threading.Thread):
    def __init__(self, vision, process):
        self.storage = []
        self.last_box = None
        self.process = process
        self.img = None
        self.boxes = None
        self.coordinates = None
        threading.Thread.__init__(self)
        # Define the video stream
        self.cap = cv2.VideoCapture(0)  # Change only if you have more than one webcams
        self.vision = vision
        # What model to download.
        # Models can bee found here:
        # https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
       # MODEL_NAME = 'ssd_inception_v2_coco_2018_01_28'
        MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
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
        # Label maps map indices to category names, so that when our convolution network predicts `5`,
        # we know that this corresponds to `airplane`.  Here we use internal utility functions,
        # but anything that returns a dictionary mapping integers to appropriate string labels would be fine
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    # Helper code
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

    # runs the neural net detection algorithm as a thread
    def run(self):

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph, config=config) as sess:
                while True:
                    # Read frame from camera
                    # print(image_np)
                    ret, image_np = self.cap.read()
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
                        # returns all box coordinates as a double array ([[ymin, xmin, ymax, xmax]]_
                        self.boxes = vis_util.get_box_coordinates(image_np,
                                                           np.squeeze(boxes),
                                                           np.squeeze(classes).astype(np.int32),
                                                           np.squeeze(scores),
                                                           self.category_index,
                                                           use_normalized_coordinates=True,
                                                           line_thickness=8,
                                                           only_get=1)

                        box = self.compute_boxes(self.boxes)



                        self.img = cv2.resize(image_np, (800, 600))

                        if (box is not None):
                            self.process.compute(box[0], box[1], box[2], box[3])
                        else:
                            self.process.set_pitch(0)
                            self.process.set_rotation(0)
                            self.process.set_tilt(0)

    def compute_boxes(self, coordinates):
        coordinates = np.array(coordinates)
        if (not coordinates.sum() == 0):
            coordinates = self.select_box(coordinates)
            self.storage.append(coordinates)
        if ((len(self.storage) > 30 or coordinates.sum() == 0) and len(self.storage) > 0):
            self.storage.pop(0)
        coordinates = np.array(self.storage, ndmin=2)
        final_coordinates = []
        if (coordinates.sum() == 0):
            return None
        else:
            for i in range(len(coordinates[0])):
                mean = 0
                values = 0
                for j in range(len(coordinates)):
                    mean += coordinates[j][i] * (j ** 5 + 1)  # (j+1) weighs the input so last frame is worth more
                    values += (j ** 5 + 1)
                final_coordinates.append(mean / values)
        final_coordinates = np.array(final_coordinates)
        self.last_box = final_coordinates
        return final_coordinates

    def select_box(self, boxes):
        if (self.last_box is None):
            self.last_box = boxes[0]  # select box with highest certainty
        else:
            min = 99999999
            min_index = 0
            for i in range(len(boxes)):
                if (abs(((boxes[i] - self.last_box) ** 2).sum()) < min):
                    min = abs(((boxes[i] - self.last_box) ** 2).sum())
                    min_index = i
                #print("Tracking box: ", i, "difference:", min)
            self.last_box = boxes[min_index]
        return self.last_box

    def get_boxes(self):
        if self.boxes is None:
            return None
        else:
            return np.array(self.boxes)

    def get_adjusted_box(self):
        if(len(self.storage)== 0):
            return None
        else:
            return self.last_box

    def get_image(self):
        return self.img

# drone = Drone_Net()
# drone.start()