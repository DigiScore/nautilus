# import python moduels
import sys
import threading
import platform
import glob
import tkinter as tk
from time import sleep

# import project modules
from score import ScoreDev
from audioEngine import Audio_engine


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.window = parent

        # generate the ML score images
        score = ScoreDev()

        # owns the images that were produced by the scorebot
        self.images = glob.glob('data/images/*.png')

        # start the audio listener thread
        audiobot = Audio_engine()

        # create canvass
        canvas_one = tk.Canvas(self.window, width=1024, height=600, bg='white')
        canvas_one.pack()

        def update_gui(self):
            # print("-------- updating gui")
            self.update()
            self.gui_thread = threading.Timer(0.1, self.update_gui)
            self.gui_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
