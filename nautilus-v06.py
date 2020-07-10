#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tensorflow as tf
import pretty_midi
from tqdm import tqdm
from numpy.random import choice
import pickle
import numpy as np
import csv
import glob
import random
import os
from pydub import AudioSegment
from pydub.playback import play
from time import sleep
from datetime import datetime
from pynput import keyboard
from data.nautilusTraining import SeqSelfAttention
from data.nautilusTraining import NoteTokenizer
from mido import MidiFile, MidiTrack
from threading import Thread
import pyaudio
from music21 import stream, converter, clef, meter
from tkinter import Tk, Canvas, PhotoImage


print ('=============================== \n\n'
       'Here we go ... '
       'just have to instantiate a neural net or two '
       'and then will get you your unique score \n\n\n '
       '================================')



"""
--------------------------------------
----- produce performance score ------
--------------------------------------
"""
class ScoreDev():
    """
    THANK YOU https://github.com/haryoa/note_music_generator/blob/master/Music%20Generator.ipynb
    All the training code was recycled from this notebook

    """

    def __init__(self):
        # then generate midi files
        self.max_generate = 100
        self.unique_notes = note_tokenizer.unique_word
        self.seq_len = 50

    # expand durations on generated score and open as LilyPond png
    def delta_change(self, midi_file_name):
        delta_factor = 4
        original_in = converter.parseFile(midi_file_name) # original primer
        output_midi = stream.Stream() # new stream
        new_part = original_in.augmentOrDiminish(delta_factor) # augments note length to factor of delta_factor
        output_midi.insert(0, new_part)
        print('output_midi.show')
        output_midi.show('text')
        output_midi.write('midi', fp=midi_file_name)
        print(f'saving bit = {midi_file_name}')

    def generatng_score(self, carla_note):
        #  generation from a single Carla DNA note
        starting_note = "".join(carla_note)
        generate = self.generate_from_one_note(note_tokenizer, starting_note)

        # create the midi file for visual notation
        generate = self.generate_notes(generate, model, self.unique_notes, self.max_generate, self.seq_len)
        now = datetime.now()
        self.current_time = now.strftime("%d-%m-%Y-%H-%M-%S")
        midi_file_name = "data/output/nautilus" + self.current_time + ".mid"
        print(midi_file_name)
        self.write_midi_file_from_generated(generate, midi_file_name, start_index=self.seq_len - 1, fs=8, max_generated=self.max_generate)
        return midi_file_name

    def open_score(self, midi_file_to_open):
        # open midifile after manipulating duration data
        self.delta_change(midi_file_to_open)
        print("\n\n\nNow I'm going to print you the score\n\n\n")
        # convert to lily.png
        note_list = []
        parts_stream = stream.Stream()
        parts_stream.insert(0, clef.TrebleClef())
        # parts_stream.insert(0, meter.TimeSignature('8/4'))
        score_in = converter.parseFile(midi_file_to_open)  # converts to a music21.stream.score

        # seperates out notes from rest of stream and makes notes_list for shuffle
        for n in score_in.recurse().notes:

            # print (f'Note: {n.pitch.name}, {n.pitch.octave}. {n.duration.quarterLength}')
            if n.duration.quarterLength != 0:  # if note length is not 0 then add to list of notes
                note_list.append(n)

        for i, nt in enumerate(note_list):
            note_pop = note_list[i]
            parts_stream.append(note_pop)

        png_fp = 'data/output/png-' + self.current_time
        parts_stream.write('lily.png', fp=png_fp)

        return str(png_fp+'.png')


    # randomly generates the seed note from Carla's list of notes, to seed the NN process
    def carla_rnd(self):
        with open('data/carlaDNA-v9.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile))
            length = len(data)
            rnd = random.randrange(length)
            starting_note = data[rnd]
            print(starting_note)
            return starting_note

    # define all functions
    def piano_roll_to_pretty_midi(self, piano_roll, fs=100, program=0): # copied from haryoa/note_music_generator (see abpove link)
        '''Convert a Piano Roll array into a PrettyMidi object'''

        notes, frames = piano_roll.shape
        pm = pretty_midi.PrettyMIDI(initial_tempo=20)
        instrument = pretty_midi.Instrument(program=program)

        # pad 1 column of zeros so we can acknowledge inital and ending events
        piano_roll = np.pad(piano_roll, [(0, 0), (1, 1)], 'constant')

        # use changes in velocities to find note on / note off events
        velocity_changes = np.nonzero(np.diff(piano_roll).T)

        # keep track on velocities and note on times
        prev_velocities = np.zeros(notes, dtype=int)
        note_on_time = np.zeros(notes)

        for time, note in zip(*velocity_changes):
            # use time + 1 because of padding above
            velocity = piano_roll[note, time + 1]
            time = time / fs
            if velocity > 0:
                if prev_velocities[note] == 0:
                    note_on_time[note] = time
                    prev_velocities[note] = velocity
            else:
                pm_note = pretty_midi.Note(
                    velocity=prev_velocities[note],
                    pitch=note,
                    start=note_on_time[note] * 12,
                    end=time * 12)
                instrument.notes.append(pm_note)
                prev_velocities[note] = 0
        pm.instruments.append(instrument)
        return pm

    def generate_from_random(self, unique_notes, seq_len=50):
        generate = np.random.randint(0, unique_notes, seq_len).tolist()
        return generate

    def generate_from_one_note(self, note_tokenizer, new_notes='35'):
        generate = [note_tokenizer.notes_to_index['e'] for i in range(49)]
        generate += [note_tokenizer.notes_to_index[new_notes]]
        return generate

    def generate_notes(self, generate, model, unique_notes, max_generated=1000, seq_len=50):
        for i in tqdm(range(max_generated), desc='genrt'):
            test_input = np.array([generate])[:,i:i+seq_len]
            predicted_note = model.predict(test_input)
            random_note_pred = choice(unique_notes+1, 1, replace=False, p=predicted_note[0])
            generate.append(random_note_pred[0])
        return generate

    def write_midi_file_from_generated(self, generate, midi_file_name = "result.mid", start_index=49, fs=8, max_generated=1000):
        note_string = [note_tokenizer.index_to_notes[ind_note] for ind_note in generate]
        array_piano_roll = np.zeros((128, max_generated+1), dtype=np.int16)
        for index, note in enumerate(note_string[start_index:]):
            if note == 'e':
                pass
            else:
                splitted_note = note.split(',')
            for j in splitted_note:
                array_piano_roll[int(j),index] = 1
                generate_to_midi = self.piano_roll_to_pretty_midi(array_piano_roll, fs=fs)
                # print("Tempo {}".format(generate_to_midi.estimate_tempo()))
            for note in generate_to_midi.instruments[0].notes:
                note.velocity = 100
                generate_to_midi.write(midi_file_name)


"""
------------------------------------
----- audio file manipulation ------
------------------------------------
"""


class AudioBot():
    # class variables
    list_all_audio = glob.glob('data/audio/*.wav')
    num = len(list_all_audio)
    seed_rnd = random.randrange(num)
    random.seed(seed_rnd)
    random.shuffle(list_all_audio)

    def __init__(self):
        print ('Audio bot is now working')
        self.go_bang = True

    def audio_comp(self):
        snd = self.random_design()  # select file from random list
        play(snd)

    def speed_change(self, sound, vol):
        # randomly generate playback speed 0.3-0.5
        rnd_speed = random.randrange(3, 5)
        speed = rnd_speed / 10
        print('change of speed = ', speed)
        print('change of gain = ', vol)
        # Manually override the frame_rate. This tells the computer how many
        # samples to play per second
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        })
        # change gain
        sound_with_altered_frame_rate_and_gain = sound_with_altered_frame_rate.apply_gain(vol)
        # convert the sound with altered frame rate to a standard frame rate
        # so that regular playback programs will work right. They often only
        # know how to play audio at standard frame rate (like 44.1k)
        return sound_with_altered_frame_rate_and_gain.set_frame_rate(sound.frame_rate)

    def random_design(self):
        rnd_file = random.randrange(self.num)
        sound_file = self.list_all_audio[rnd_file]
        print('sound file = ', sound_file)
        sound = AudioSegment.from_wav(sound_file)
        # gain structure?
        gain_rnd = random.randrange(1)
        gain = 1 # gain_rnd + 0.5
        # play (sound)
        new_sound = self.speed_change(sound, gain)
        length = new_sound.duration_seconds
        print('length = ', length)
        fade_sound = new_sound.fade_in(1000).fade_out(500)
        #play(fade_sound)
        return (fade_sound)


"""
--------------------------
-----mission control------
--------------------------
"""
class MissionControl():
    peak = 0

    def __init__(self):
        print ('Mission control is online!')
        self.running = True

    def terminate(self):
        self.running = False

    def keyboard(self):
        """listens out for keyboard control - SPACE bar to end composition"""
        while self.running:
            with keyboard.Listener(on_press=self.on_press) as listener:
                # break if keyboard is pressed for various reasons SPACE = ends prog
                listener.join()
            break

    def on_press(self, key):
        if key == keyboard.Key.space:
            print('end pressed. Just going to finish this sound :)')
            self.terminate()
            return False

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
        canvas_one = Canvas(window1, width=1200, height=800, bg='white')
        canvas_one.pack()

        # create image from PNG and put in position on canvas
        score1 = PhotoImage(file=score_to_show)
        # score1_large = score1.zoom(2, 2)  # zoom 2x
        mypart1 = canvas_one.create_image(600, 400, image=score1)  # put in middle of canvas

        window1.update()

        if not self.running:
            window1.destroy()

"""
------------------------------------------------
--------- main programme starts here -----------
------------------------------------------------
"""

if __name__ == '__main__':
    # first we need to build model from trained files
    model = tf.keras.models.load_model('data/epochs4-long-model_ep4.h5' , custom_objects=SeqSelfAttention.get_custom_objects())
    note_tokenizer  = pickle.load(open("data/epochs4-long-tokenizer.p", "rb"))

    #then we generate the score, save it to disk as .mid, then open it in MuseScore or sim.
    score = ScoreDev() # initiates a score bot to create the unique score
    carla_start_note = score.carla_rnd() # generates a start note from Carla's improv transcipt
    file_to_open = score.generatng_score(carla_start_note) # asks score-bot to generate a score for performance
    score_to_show = score.open_score(file_to_open) # score bot asks MuseScore or sim to open the generated .Mid file

    # start threading. This is where the program starts
    mc = MissionControl() # initiates a bot to control the threading (multiple operations) in this program

    t1 = Thread(target=mc.keyboard) # listens to the keyboard for exit/ stop key (= space)
    t2 = Thread(target=mc.snd_listen, daemon=True) # starts the process of listening to the computer mic
    t3 = Thread(target=mc.audio_wrangler, daemon=True) # starts the process of randomly generating the sonic accompniment
    t4 = Thread(target=mc.show_score, daemon=True)

    # here we go ... start your engines
    t1.start()
    t2.start()
    t3.start()
    t4.start()

    # when finished join all threads and close mission control
    t1.join()
    t2.join()
    t3.join()
    t4.join()
