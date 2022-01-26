import random
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtCore import pyqtSlot as Slot

import glob
from time import time
from threading import Timer
from queue import Queue

class App(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.image_files = glob.glob('data/images/*.png')

        self.setGeometry(100, 100, 900, 700)

        self.score_dict = {"top_left": {"time": time(), "image": None},
                           "top_right": {"time": time(), "image": None},
                           "bottom_left": {"time": time(), "image": None},
                           "bottom_right": {"time": time(), "image": None}}

        self.score_dict_list = ["top_left",
                                "top_right",
                                "bottom_left",
                                "bottom_right"]

        self.score_signal = Queue()
        # self.score_signal.add_to_queue(self.score_dict)

        # create all labels
        self.createLabels()

        # initiate slideshow
        self.timer = QBasicTimer()
        self.step = 0
        self.delay = 500  # milliseconds

        # self.slideshow()
        self.gui_thread = None
        self.update_gui()

    def createLabels(self):
        screen_resolution = self.geometry()
        height = screen_resolution.height()
        width = screen_resolution.width()

        # print(height, width)
        # setting  the geometry of window
        # self.setGeometry(0, 0, 400, 300)

        # creating a label widget
        self.top_left_label = QLabel(self)

        # moving position
        self.top_left_label.move(0, 0)

        # setting up border
        self.top_left_label.setStyleSheet("border: 1px solid black;")

        # resizing the widget
        self.top_left_label.resize(width / 2, height / 2)

        # creating a label widget
        self.top_right_label = QLabel(self)

        # moving position
        self.top_right_label.move(width / 2, 0)

        # setting up border
        self.top_right_label.setStyleSheet("border: 1px solid black;")

        # resizing the widget
        self.top_right_label.resize(width / 2, height / 2)

        # creating a label widget
        self.bottom_left_label = QLabel(self)

        # moving position
        self.bottom_left_label.move(0, height / 2)

        # setting up border
        self.bottom_left_label.setStyleSheet("border: 1px solid black;")

        # resizing the widget
        self.bottom_left_label.resize(width / 2, height / 2)

        # creating a label widget
        self.bottom_right_label = QLabel(self)

        # moving position
        self.bottom_right_label.move(width / 2, height / 2)

        # setting up border
        self.bottom_right_label.setStyleSheet("border: 1px solid black;")

        # resizing the widget
        self.bottom_right_label.resize(width / 2, height / 2)


    def update_gui(self):
        # print("-------- updating gui")
        self.update()
        self.slideshow()
        self.gui_thread = Timer(0.1, self.update_gui)
        self.gui_thread.start()

    # @Slot(object)
    # def got_osc_signal(self, osc_msg):


    def slideshow(self):
        # if self.step >= len(self.image_files):
        #     self.timer.stop()
        #     self.button.setText('Slide Show Finished')
        #     return
        # self.timer.start(self.delay, self)
        # while True:
        for quad in self.score_dict_list:
            t = self.score_dict[quad]["time"]
            # print(quad, t)

        # for key, value in self.score_dict.items():
            if t < time():
                file = self.image_files[random.randrange(len(self.image_files))]
                image_duration = t + (float(file[-7:-4]) * (random.randrange(5, 30)))
                # self.score_dict[key] = image_duration
                self.score_dict[quad]["time"] = image_duration
                print("here", quad)

            # self.timer.start(image_duration * 3, self)

                self.pixmap = QPixmap(file)
            # scale = 2

            # size = self.pixmap.size()

                # scaled_pixmap = self.pixmap.scaled(scale * size)
                if quad == "top_left":
                    self.top_left_label.setPixmap(self.pixmap)
                elif quad == "top_right":
                    self.top_right_label.setPixmap(self.pixmap)
                elif quad == "bottom_left":
                    self.bottom_left_label.setPixmap(self.pixmap)
                else:
                    self.bottom_right_label.setPixmap(self.pixmap)
                # self.setWindowTitle("{} --> {}".format(str(self.step), file))
            # self.step += 1



    # self.label.setPixmap(scaled_pixmap)


# pick image files you have in the working folder
# or give full path name
# self.image_files = glob.glob('data/images/*.png')

# app = QApplication([])
# w = Slides(image_files)
# setGeometry(x, y, w, h)  x,y = upper left corner coordinates
# w.setGeometry(100, 100, 700, 500)
# w.show()
# app.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_viewer = App()
    image_viewer.show()
    sys.exit(app.exec_())

