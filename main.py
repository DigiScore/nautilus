# import python modules
import threading
import glob
import tkinter as tk
from time import sleep, time
from random import randrange
import atexit
from threading import Thread
from queue import Queue

# import project modules
from score import ScoreDev
from audioEngine import Audio_engine


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.window = parent
        self.running = True
        self.UPDATE_RATE = 0.1

        # generate the ML score images
        score = ScoreDev()

        # owns the images that were produced by the scorebot
        self.images = glob.glob('data/images/*.png')

        # start the audio listener thread
        audiobot = Audio_engine()

        # create canvass
        self.canvas_one = tk.Canvas(self.window, width=1024, height=600, bg='white')
        self.canvas_one.pack()

        # get first image
        self.time_on_screen = time()
        self.get_image()

        # kickstart thread
        # start a thread to wait for commands to write
        self.incoming_commands_queue = Queue()
        self.gui_thread = None
        self.update_gui()

        # # start a thread to wait for commands to write
        # self.incoming_commands_queue = Queue()

        # listeningThread = Thread(target=self.update_image, args=(self.incoming_commands_queue,), daemon=True)
        # listeningThread.start()

        # atexit.register(self.close_sequence)

    def update_image(self):
        """check to see if anything is in the queue"""
        while self.running:
            if self.incoming_commands_queue.qsize() > 0:
                input_image = self.incoming_commands_queue.get()
                # print("input_str = {}".format(input_str))

                # score1_large = score1.zoom(2, 2)  # zoom 2x
                mypart1 = self.canvas_one.create_image(512, 300, image=input_image)  # put in middle of canvas

            # # pause to let other threads work
            # sleep(0.01)


    def update_gui(self):
        # print("-------- updating gui")

        # check if anything in the queue?
        self.update_image()

        ## update window
        self.window.update()

        # self.gui_thread = threading.Timer(0.1, self.update_gui)
        # self.gui_thread.start()
        self.after(self.UPDATE_RATE, self.update_gui)



    def get_image(self):
        """randomly decide on an image to show on screen,
        determine how long on screen and add to queue"""
        if time() > self.time_on_screen:
            # how long on screen? 3 - 12 seconds
            rnd_time = randrange(3, 12)
            self.time_on_screen += rnd_time

            # which image?
            rnd_image = randrange(len(self.images))
            score_to_show = self.images[rnd_image]
            score = tk.PhotoImage(file=score_to_show)

            # put this into the Queue
            self.incoming_commands_queue.put(score)

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
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
