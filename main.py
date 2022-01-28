# import python modules
import glob
from threading import Timer
from time import sleep, time
from random import randrange
import sys

# import PyQt5 modules (universal with PySide2)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton

# import project modules
from score import ScoreDev
from audioEngine import Audio_engine


class MainApplication(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        # is unity running the notation png's?
        self.unity_score = True

        # set vars and params
        self.running = True

        self.score_dict = {"top_left": {"time": time(), "image": None},
                           "top_right": {"time": time(), "image": None},
                           "bottom_left": {"time": time(), "image": None},
                           "bottom_right": {"time": time(), "image": None}}

        self.score_dict_list = ["top_left",
                                "top_right",
                                "bottom_left",
                                "bottom_right"]

        # generate the ML score images
        # todo - find better solution for changing global font colour
        # todo - current solution was to change color in brown/core/stem.py
        #  and brown/constants.py
        score = ScoreDev()

        # start the audio listener thread
        self.audiobot = Audio_engine()

        # UI setup and off we go
        self.title = 'Nautilus'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create all labels
        if self.unity_score:
            # create a start button
            self.start_button = QPushButton("START", self)
            self.start_button.setCheckable(True)
            self.start_button.toggle()
            self.start_button.move(100, 70)

            # adding action to the button
            self.start_button.clicked.connect(self.start_score)

            # and off we go
            self.show()

        else:
            # owns the images that were produced by the scorebot
            self.image_files = glob.glob('data/images/*.png')

            # create labels
            self.createLabels()

            # and off we go
            self.gui_thread = None
            self.update_gui()

    @Slot()
    def start_score(self):
        if not self.start_button.isChecked():
            print("Starting")
            self.start_button.setText("STOP")
            self.audiobot.go_bang = True
        else:
            print("Stopping")
            self.audiobot.go_bang = False
            self.audiobot.running = False
            self.start_button.setText("START")
            # todo - close down all other funcs & threads
            sleep(1)
            print("bye bye")
            self.running = False

    # update the GUI and check the quad images
    def update_gui(self):
        # print("-------- updating gui")
        while self.running:
            self.update()
            self.updateImage()
            self.gui_thread = Timer(0.1, self.update_gui)
            self.gui_thread.start()

    def createLabels(self):
        screen_resolution = self.geometry()
        height = screen_resolution.height()
        width = screen_resolution.width()

        # widget params
        self.setGeometry(100, 100, 900, 700)

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

    def updateImage(self):
    # check the status of each quad
        for quad in self.score_dict_list:
            t = self.score_dict[quad]["time"]

            # for key, value in self.score_dict.items():
            # if times up then change image in quadrant
            if t < time():
                file = self.image_files[randrange(len(self.image_files))]
                image_duration = t + (float(file[-7:-4]) * (randrange(2, 20)))
                # self.score_dict[key] = image_duration
                self.score_dict[quad]["time"] = image_duration
                # print("here", quad)

                # set the new image to a pixmap and put into quad
                self.pixmap = QPixmap(file)
                if quad == "top_left":
                    self.top_left_label.setPixmap(self.pixmap)
                elif quad == "top_right":
                    self.top_right_label.setPixmap(self.pixmap)
                elif quad == "bottom_left":
                    self.bottom_left_label.setPixmap(self.pixmap)
                else:
                    self.bottom_right_label.setPixmap(self.pixmap)

"""this is here for access from elsewhere
and is written into the note-tokeniser file"""
class NoteTokenizer:
    def __init__(self):
        self.notes_to_index = {}
        self.index_to_notes = {}
        self.num_of_word = 0
        self.unique_word = 0
        self.notes_freq = {}

    def transform(self, list_array):
        """ Transform a list of note in string into index.

        Parameters
        ==========
        list_array : list
          list of note in string format

        Returns
        =======
        The transformed list in numpy array.

        """
        transformed_list = []
        for instance in list_array:
            transformed_list.append([self.notes_to_index[note] for note in instance])
        return np.array(transformed_list, dtype=np.int32)

    def partial_fit(self, notes):
        """ Partial fit on the dictionary of the tokenizer

        Parameters
        ==========
        notes : list of notes

        """
        for note in notes:
            note_str = ','.join(str(a) for a in note)
            if note_str in self.notes_freq:
                self.notes_freq[note_str] += 1
                self.num_of_word += 1
            else:
                self.notes_freq[note_str] = 1
                self.unique_word += 1
                self.num_of_word += 1
                self.notes_to_index[note_str], self.index_to_notes[self.unique_word] = self.unique_word, note_str

    def add_new_note(self, note):
        """ Add a new note into the dictionary

        Parameters
        ==========
        note : str
          a new note who is not in dictionary.

        """
        assert note not in self.notes_to_index
        self.unique_word += 1
        self.notes_to_index[note], self.index_to_notes[self.unique_word] = self.unique_word, note

if __name__ == "__main__":
    app = QApplication(sys.argv)
    image_viewer = MainApplication()
    # image_viewer.showFullScreen()
    # image_viewer.show()
    sys.exit(app.exec_())
