#!/usr/bin/env python3

import tensorflow as tf
import pretty_midi
from tqdm import tqdm
from numpy.random import choice
import pickle
import numpy as np
import csv
import glob
from time import sleep
import random
import os
from pydub import AudioSegment
from pydub.playback import play
from time import sleep
from datetime import datetime
# from pynput import keyboard
from data.nautilusTraining import SeqSelfAttention
from data.nautilusTraining import NoteTokenizer
from mido import MidiFile, MidiTrack
from threading import Thread
import pyaudio
from music21 import stream, converter, clef, meter
from tkinter import Tk, Canvas, PhotoImage

# import project modules
from score import ScoreDev
from audio import AudioBot

class MissionControl():
    peak = 0

    def __init__(self):
        print ('Mission control is online!')
        self.running = True

        # then we generate the score, save it to disk as .mid, then open it in MuseScore or sim.
        score = ScoreDev()  # initiates a score bot to create the unique score
        # carla_start_note = score.carla_rnd()  # generates a start note from Carla's improv transcipt
        # file_to_open = score.generatng_score(carla_start_note)  # asks score-bot to generate a score for performance
        # open_score = score.open_score(file_to_open)  # score bot  or sim to open the generated .Mid file

        self.images = glob.glob('data/images/*.png')

    def terminate(self):
        self.running = False

    # def keyboard(self):
    #     """listens out for keyboard control - SPACE bar to end composition"""
    #     while self.running:
    #         with keyboard.Listener(on_press=self.on_press) as listener:
    #             # break if keyboard is pressed for various reasons SPACE = ends prog
    #             listener.join()
    #         break

    # def on_press(self, key):
    #     if key == keyboard.Key.space:
    #         print('end pressed. Just going to finish this sound :)')
    #         self.terminate()
    #         return False

    def snd_listen(self):
        CHUNK = 2 ** 11
        RATE = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        while self.running:
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            self.peak = np.average(np.abs(data)) * 2
            # bars = "#" * int(50 * self.peak / 2 ** 16)
            # print("%05d %s" % (self.peak, bars))
        stream.stop_stream()
        stream.close()
        p.terminate()

    def audio_wrangler(self):
        audio_bot = AudioBot()
        while self.running:
            if self.peak > 4000: # am listening for sound level above a certain threshold
                chance_make = random.randrange(100)
                if chance_make > 20: # 80% chance of playing if you activate me
                    print ('react to sound')
                    audio_bot.audio_comp()
            else:
                chance_me = random.randrange(100)
                #print (chance_me)
                if chance_me > 90: # will make a sound on my own 10% of the time
                    print(f'{chance_me}   =  on my own')
                    audio_bot.audio_comp()
            sleep(0.1) # slowing things down to a human level

    def show_score(self):
        # make windows
        window1 = Tk()

        # create canvass
        canvas_one = Canvas(window1, width=1024, height=600, bg='white')
        canvas_one.pack()

        # create image from each PNG and put in position on canvas
        for img in self.images:
            score = PhotoImage(file=img)
        # score1_large = score1.zoom(2, 2)  # zoom 2x
            mypart1 = canvas_one.create_image(512, 300, image=score)  # put in middle of canvas

            window1.update()

            sleep(10)

        if not self.running:
            window1.destroy()

"""
------------------------------------------------
--------- main programme starts here -----------
------------------------------------------------
"""

if __name__ == '__main__':
    # # first we need to build model from trained files
    # model = tf.keras.models.load_model('data/epochs4-long-model_ep4.h5' , custom_objects=SeqSelfAttention.get_custom_objects())
    # note_tokenizer = pickle.load(open("data/epochs4-long-tokenizer.p", "rb"))


    # #then we generate the score, save it to disk as .mid, then open it in MuseScore or sim.
    # score = ScoreDev() # initiates a score bot to create the unique score
    # carla_start_note = score.carla_rnd() # generates a start note from Carla's improv transcipt
    # file_to_open = score.generatng_score(carla_start_note) # asks score-bot to generate a score for performance
    # open_score = score.open_score(file_to_open) # score bot  or sim to open the generated .Mid file

    # todo  replace with TK in control
    # start threading. This is where the program starts
    mc = MissionControl() # initiates a bot to control the threading (multiple operations) in this program

    # t1 = Thread(target=mc.keyboard) # listens to the keyboard for exit/ stop key (= space)
    t2 = Thread(target=mc.snd_listen, daemon=True) # starts the process of listening to the computer mic
    t3 = Thread(target=mc.audio_wrangler, daemon=True) # starts the process of randomly generating the sonic accompniment
    t4 = Thread(target=mc.show_score, daemon=True)

    # here we go ... start your engines
    # t1.start()
    t2.start()
    t3.start()
    t4.start()

    # when finished join all threads and close mission control
    # t1.join()
    t2.join()
    t3.join()
    t4.join()
