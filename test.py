import random
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QBasicTimer
import glob
from time import time

class App(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.image_files = glob.glob('data/images/*.png')

        self.setGeometry(100, 100, 900, 700)

        self.timer_dict = {"top_left": time(),
                           "top_right": time(),
                           "bottom_left": time(),
                           "bottom_right": time()}

        # create all labels
        self.createLabels()

        # initiate slideshow
        self.timer = QBasicTimer()
        self.step = 0
        self.delay = 500  # milliseconds

        self.slideshow()

    def createLabels(self):
        screen_resolution = self.geometry()
        height = screen_resolution.height()
        width = screen_resolution.width()

        print(height, width)
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


    def slideshow(self):
        # if self.step >= len(self.image_files):
        #     self.timer.stop()
        #     self.button.setText('Slide Show Finished')
        #     return
        # self.timer.start(self.delay, self)
        while True:
            for key, value in self.timer_dict.items():
                if value < time():

                    file = self.image_files[random.randrange(len(self.image_files))]
                    image_duration = (float(file[-7:-4]) * 1000) * 3
                    self.timer_dict[key] = image_duration

                # self.timer.start(image_duration * 3, self)

                    self.pixmap = QPixmap(file)
                # scale = 2

                # size = self.pixmap.size()

                    # scaled_pixmap = self.pixmap.scaled(scale * size)
                    if key == "top_left":
                        self.top_left_label.setPixmap(self.pixmap)
                    elif key == "top_rightt":
                        self.top_right_label.setPixmap(self.pixmap)
                    elif key == "bottom_left":
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

