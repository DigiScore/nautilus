"""
--------------------------------------
----- produce performance score ------
--------------------------------------
"""

import tensorflow as tf
import pickle
import pretty_midi
from tqdm import tqdm
from numpy.random import choice
import numpy as np
import csv
import random
from datetime import datetime
from music21 import stream, converter, clef, meter
from data.nautilusTraining import SeqSelfAttention
from data.nautilusTraining import NoteTokenizer

from renderScore import ImageGen

class ScoreDev():
    """
    THANK YOU https://github.com/haryoa/note_music_generator/blob/master/Music%20Generator.ipynb
    All the training code was recycled from this notebook

    """

    def __init__(self):
        # first we need to build model from trained files
        self.model = tf.keras.models.load_model('data/epochs4-long-model_ep4.h5',
                                           custom_objects=SeqSelfAttention.get_custom_objects())

        with open("data/epochs4-long-tokenizer.p", "rb") as t:
            self.note_tokenizer = pickle.load(t)

        # then generate midi files
        self.max_generate = 100
        self.unique_notes = self.note_tokenizer.unique_word
        self.seq_len = 50
        self.brown_score = ImageGen()
        self.delta_change = 2

        # generate individual notations for piece
        carla_start_note = self.carla_rnd()  # generates a start note from Carla's improv transcipt
        file_to_open = self.generatng_score(carla_start_note)
        self.open_score(file_to_open)


    # # expand durations on generated score and open as LilyPond png
    # def delta_change(self, midi_file_name):
    #     self.delta_factor = 4
    #     original_in = converter.parseFile(midi_file_name) # original primer
    #     output_midi = stream.Stream() # new stream
    #     new_part = original_in.augmentOrDiminish(delta_factor) # augments note length to factor of delta_factor
    #     output_midi.insert(0, new_part)
    #     print('output_midi.show')
    #     output_midi.show('text')
    #     output_midi.write('midi', fp=midi_file_name)
    #     print(f'saving bit = {midi_file_name}')

    def generatng_score(self, carla_note):
        #  generation from a single Carla DNA note
        starting_note = "".join(carla_note)
        generate = self.generate_from_one_note(self.note_tokenizer, starting_note)
        print('generate 1 = ', generate)
        # create the midi file for visual notation
        generate = self.generate_notes(generate, self.model, self.unique_notes, self.max_generate, self.seq_len)
        print('generate 2 = ', generate)

        now = datetime.now()
        self.current_time = now.strftime("%d-%m-%Y-%H-%M-%S")
        midi_file_name = "data/output/nautilus" + self.current_time + ".mid"
        print(midi_file_name)
        self.write_midi_file_from_generated(generate, midi_file_name, start_index=self.seq_len - 1, fs=8, max_generated=self.max_generate)
        return midi_file_name

    def open_score(self, midi_file_to_open):
        # open midifile after manipulating duration data
        # self.delta_change(midi_file_to_open)
        # print("\n\n\nNow I'm going to print you the score\n\n\n")
        # convert to lily.png
        note_list = []
        parts_stream = stream.Stream()
        parts_stream.insert(0, clef.TrebleClef())
        # parts_stream.insert(0, meter.TimeSignature('8/4'))
        score_in = converter.parseFile(midi_file_to_open)  # converts to a music21.stream.score

        # seperates out notes from rest of stream and makes notes_list for shuffle
        for n in score_in.recurse().notes:

            # if note length is not 0 then make longer and print out as individual png
            if n.duration.quarterLength != 0:
                new_duration = n.duration.quarterLength * self.delta_change
                print(f'Note: {n.pitch.name}, {n.pitch.octave}, {new_duration}')
                # note_list.append(n)

                # make dict and send for rendering
                note_dict = {"pitch": n.pitch.name,
                             "octave": n.pitch.octave,
                             "duration": n.duration.quarterLength}
                self.brown_score.make_image(note_dict)

        # for i, nt in enumerate(note_list):
        #     note_pop = note_list[i]
        #     parts_stream.append(note_pop)

        # png_fp = 'data/output/png-' + self.current_time
        # parts_stream.write('lily.png', fp=png_fp)

        # return str(png_fp+'.png')


    # randomly generates the seed note from Carla's list of notes, to seed the NN process
    def carla_rnd(self):
        with open('data/carlaDNA-v9.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile))
            length = len(data)
            rnd = random.randrange(length)
            starting_note = data[rnd]
            print('seed note == ', starting_note)
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
        for i in tqdm(range(max_generated), desc='generating'):
            test_input = np.array([generate])[:,i:i+seq_len]
            predicted_note = model.predict(test_input)
            random_note_pred = choice(unique_notes+1, 1, replace=False, p=predicted_note[0])
            generate.append(random_note_pred[0])
        return generate

    def write_midi_file_from_generated(self, generate, midi_file_name = "result.mid", start_index=49, fs=8, max_generated=1000):
        note_string = [self.note_tokenizer.index_to_notes[ind_note] for ind_note in generate]
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
