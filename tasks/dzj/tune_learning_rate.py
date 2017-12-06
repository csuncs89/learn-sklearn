import argparse
import os
import sys

import keras
import tensorflow as tf
from keras import models
from keras import layers

from tasks.dzj import dzj_model


def parse_args():
    parser = argparse.ArgumentParser(
        description='Tune regularizer'
    )
    parser.add_argument(
        'dir_dataset',
        help='Directory to the dataset',
    )

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    return args


class DzjRecognizerBaseline(dzj_model.DzjRecognizer):

    def _configure(self):
        self.w_img = 28
        self.h_img = 28
        self.invert_img = True
        self.num_classes = 200
        self.batch_size = 64
        self.version_recognizer = 'baseline'
        self.local_debug = False
        self.normalize_img_mean0 = False
        self.percent_validation = 0.1
        self.dir_base = os.path.abspath(__file__)[:-3]

    def _compile(self):
        optimizer = keras.optimizers.Adadelta()
        self._model.compile(loss=keras.losses.categorical_crossentropy,
                            optimizer=keras.optimizers.Adadelta(),
                            metrics=['accuracy'])

    def _create_model(self):
        """
        3x3x32 3x3x64 2x2 3x3x64 2x2 500 500 200
        """
        input_shape = (self.h_img, self.w_img, 1)

        model = models.Sequential()

        model.add(layers.Conv2D(32, (3, 3), input_shape=input_shape))
        model.add(layers.Activation('relu'))

        model.add(layers.Conv2D(64, (3, 3)))
        model.add(layers.Activation('relu'))

        model.add(layers.MaxPool2D(pool_size=(2, 2)))

        model.add(layers.Conv2D(64, (3, 3)))
        model.add(layers.Activation('relu'))

        model.add(layers.MaxPool2D(pool_size=(2, 2)))

        model.add(layers.Flatten())

        model.add(layers.Dense(500))
        model.add(layers.Activation('relu'))

        model.add(layers.Dense(500))
        model.add(layers.Activation('relu'))

        model.add(layers.Dense(self.num_classes))
        model.add(layers.Activation('softmax'))

        self._model = model
        self._compile()


class DzjRecognizerFast(DzjRecognizerBaseline):

    def _configure(self):
        super(DzjRecognizerFast, self)._configure()
        self.version_recognizer = 'fast'

    def _compile(self):
        optimizer = keras.optimizers.Adadelta(lr=3.0)
        self._model.compile(loss=keras.losses.categorical_crossentropy,
                            optimizer=keras.optimizers.Adadelta(),
                            metrics=['accuracy'])


class DzjRecognizerSlow(DzjRecognizerBaseline):

    def _configure(self):
        super(DzjRecognizerSlow, self)._configure()
        self.version_recognizer = 'slow'

    def _compile(self):
        optimizer = keras.optimizers.Adadelta(lr=0.3)
        self._model.compile(loss=keras.losses.categorical_crossentropy,
                            optimizer=keras.optimizers.Adadelta(),
                            metrics=['accuracy'])


def main():
    args = parse_args()

    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True
    sess = tf.Session(config=tfconfig)

    for k, c in globals().items():
        if k.startswith('DzjRecognizer'):
            recognizer = c()
            recognizer.run(args.dir_dataset, epochs=100)


if __name__ == '__main__':
    main()
