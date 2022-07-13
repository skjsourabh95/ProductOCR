import warnings
warnings.filterwarnings("ignore",category=FutureWarning)

import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)

from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten,Activation,Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing import image

import numpy as np

def predit_type(img_path):
    
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=(150,150,3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(2))
    model.add(Activation('sigmoid'))
    model.load_weights("infant-3.h5")

    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])


    img = image.load_img(img_path, target_size=(150,150,1), grayscale=False)
    img = image.img_to_array(img)
    img = img/255
    new_X = np.array(img).reshape(1,150,150,3)

    pred = model.predict_classes(new_X)
    return pred[0]