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


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
