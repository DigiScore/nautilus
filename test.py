import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QBasicTimer
import glob

class App(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.image_files = glob.glob('data/images/*.png')
        self.setGeometry(100, 100, 900, 700)
        # s = '<>'*300
        self.label = QLabel(self)
        # self.label.setGeometry(10, 30, 640, 480)
        self.label.setGeometry(0, 0, 900, 700)



        # self.button = QPushButton("Start Slide Show",self)
        # self.button.setGeometry(10, 10, 140, 30)
        # self.button.clicked.connect(self.timerEvent)
        # self.timerEvzent()


        self.timer = QBasicTimer()
        self.step = 0
        self.delay = 500  # milliseconds


        # sf = "Slides are shown {} seconds apart"
        # self.setWindowTitle(sf.format(self.delay/1000.0))

        self.timerEvent()


    def timerEvent(self, e=None):
        if self.step >= len(self.image_files):
            self.timer.stop()
            self.button.setText('Slide Show Finished')
            return
        # self.timer.start(self.delay, self)
        file = self.image_files[self.step]
        image_duration = float(file[-7:-4]) * 1000

        self.timer.start(image_duration * 3, self)

        self.pixmap = QPixmap(file)
        scale = 2

        size = self.pixmap.size()

        scaled_pixmap = self.pixmap.scaled(scale * size)
        self.label.setPixmap(scaled_pixmap)
        self.setWindowTitle("{} --> {}".format(str(self.step), file))
        self.step += 1



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



# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
# from PyQt5.QtGui import QIcon, QPixmap
#
# import glob
# from time import sleep
#
#
# class App(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         print('1')
#         self.images = glob.glob('data/images/*.png')
#         self.title = 'PyQt5 image - pythonspot.com'
#         self.left = 10
#         self.top = 10
#         self.width = 640
#         self.height = 480
#         self.initUI()
#
#     def initUI(self):
#         print('2')
#         # self.acceptDrops()
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#         # self.setStyleSheet('transparent')
#         self.setAutoFillBackground(True)
#
#         # Create widget
#         label = QLabel(self)
#
#         # pixmap = QPixmap('data/images/nautilus-1643040124.741466-d-0.5.png')
#         # # pixmap.setDevicePixelRatio(2)
#         #
#         # label.setPixmap(pixmap)
#         #
#         # # self.resize(pixmap.width(), pixmap.height())
#         #
#         # print('3')
#         # self.show()
#
#
#         for img in self.images:
#             print(img)
#             pixmap = QPixmap(img)
#             label.setPixmap(pixmap)
#             self.resize(pixmap.width(), pixmap.height())
#             # self.show()
#             print('3')
#             self.update()
#             sleep(2)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = App()
#     sys.exit(app.exec_())