# IMPORTS

# TensorFlow and tf.keras (to build the neural network)
import tensorflow as tf
from tensorflow import keras
# Helper libraries (for visualisation [and not here, but we'll need it for
# feeding the input too])
import numpy as np
import matplotlib.pyplot as plt

# LOAD AND PROCESS DATASET

# load
mnist = tf.keras.datasets.mnist

# don't worry about this function, no syntax that you'll ever have to use
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

#important part

train_images = train_images / 255.0
test_images = test_images / 255.0

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(28, 28)),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(10, activation=tf.nn.softmax)
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_images, train_labels, epochs=5)