"""
THANK YOU https://github.com/haryoa/note_music_generator/blob/master/Music%20Generator.ipynb
All the training code was recycled from this notebook

"""

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
from nautilusTraining import SeqSelfAttention
from nautilusTraining import NoteTokenizer
from mido import MidiFile, MidiTrack
from threading import Thread


# define all functions
def piano_roll_to_pretty_midi(piano_roll, fs=100, program=0): # copied from haryoa/note_music_generator (see abpove link)
    '''Convert a Piano Roll array into a PrettyMidi object
     with a single instrument.
    Parameters
    ----------
    piano_roll : np.ndarray, shape=(128,frames), dtype=int
        Piano roll of one instrument
    fs : int
        Sampling frequency of the columns, i.e. each column is spaced apart
        by ``1./fs`` seconds.
    program : int
        The program number of the instrument.
    Returns
    -------
    midi_object : pretty_midi.PrettyMIDI
        A pretty_midi.PrettyMIDI class instance describing
        the piano roll.
    '''
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

def generate_from_random(unique_notes, seq_len=50):
    generate = np.random.randint(0, unique_notes, seq_len).tolist()
    return generate


def generate_from_one_note(note_tokenizer, new_notes='35'):
    generate = [note_tokenizer.notes_to_index['e'] for i in range(49)]
    generate += [note_tokenizer.notes_to_index[new_notes]]
    return generate


def generate_notes(generate, model, unique_notes, max_generated=1000, seq_len=50):
  for i in tqdm(range(max_generated), desc='genrt'):
    test_input = np.array([generate])[:,i:i+seq_len]
    predicted_note = model.predict(test_input)
    random_note_pred = choice(unique_notes+1, 1, replace=False, p=predicted_note[0])
    generate.append(random_note_pred[0])
  return generate


def write_midi_file_from_generated(generate, midi_file_name = "result.mid", start_index=49, fs=8, max_generated=1000):
  note_string = [note_tokenizer.index_to_notes[ind_note] for ind_note in generate]
  array_piano_roll = np.zeros((128,max_generated+1), dtype=np.int16)
  for index, note in enumerate(note_string[start_index:]):
    if note == 'e':
      pass
    else:
      splitted_note = note.split(',')
      for j in splitted_note:
        array_piano_roll[int(j),index] = 1
  generate_to_midi = piano_roll_to_pretty_midi(array_piano_roll, fs=fs)
  print("Tempo {}".format(generate_to_midi.estimate_tempo()))
  for note in generate_to_midi.instruments[0].notes:
    note.velocity = 100
  generate_to_midi.write(midi_file_name)





"""
--------------------------
----- audio listener ------
--------------------------
"""
class AudioListener():
    def __init__(self):
    pass



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
        pass

    # changes speed of audio playback using random processes
    def speed_change(self, sound, vol):
        # randomly generate playback speed 0.3-0.5
        self.rnd_speed = random.randrange(3, 5)
        self. speed = self.rnd_speed / 10
        print ('change of speed = ', self.speed)
        print('change of gain = ', vol)
        # Manually override the frame_rate. This tells the computer how many
        # samples to play per second
        self.sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
             "frame_rate": int(sound.frame_rate * self.speed)
          })
        # change gain
        self.sound_with_altered_frame_rate_and_gain = self.sound_with_altered_frame_rate.apply_gain(vol)
        # convert the sound with altered frame rate to a standard frame rate
        # so that regular playback programs will work right. They often only
        # know how to play audio at standard frame rate (like 44.1k)
        return self.sound_with_altered_frame_rate_and_gain.set_frame_rate(sound.frame_rate)

    def random_design(self):
        self.rnd_file = random.randrange(self.num)
        self.sound_file = self.list_all_audio[self.rnd_file]
        print('sound file = ', self.sound_file)
        self.sound = AudioSegment.from_wav(self.sound_file)
        # gain structure?
        self.gain_rnd = random.randrange(1)
        self.gain = self.gain_rnd + 0.5
        # play (sound)
        self.new_sound = self.speed_change(self.sound, self.gain)
        length = self.new_sound.duration_seconds
        print('length = ', length)
        self.fade_sound = self.new_sound.fade_in(1000).fade_out(500)
        return(self.fade_sound)

#
# # listening out for 'space bar' to end the performance
# def on_press(key):
#     global break_program
#     if key == keyboard.Key.space:
#         print ('end pressed')
#         break_program = True
#         return False


"""
--------------------------------------
----- produce performance score ------
--------------------------------------
"""
class ScoreDev():
    def __init__(self):
        # then generate midi files
        self.max_generate = 100
        self.unique_notes = note_tokenizer.unique_word
        self.seq_len = 50

    # expand durations on generated score and open as LilyPond png
    def delta_change(self, midi_file_name):
        self.in_file = MidiFile(midi_file_name)
        self.outfile = MidiFile()
        self.track = MidiTrack()
        self.outfile.tracks.append(self.track)
        for trx in self.in_file.tracks:
            for msg in trx:
                if msg.type == 'note_on' or 'note_off' and not msg.is_meta:
                    self.new_time = msg.time * 3
                    self.new_msg = msg.copy(time=self.new_time)
                    self.track.append(self.new_msg)
                else:
                    self.track.append(msg)
        self.outfile.save(midi_file_name)

    def generatng_score(self):
        #  generation from a single Carla DNA note
        self.starting_note = "".join(self.carla_rnd())
        generate = generate_from_one_note(note_tokenizer, starting_note)

        # create the midi file for visual notation
        generate = generate_notes(generate, model, unique_notes, max_generate, seq_len)
        now = datetime.now()
        current_time = now.strftime("%d-%m-%Y-%H-%M-%S")
        midi_file_name = "data/output/nautilus" + current_time + ".mid"
        print(midi_file_name)
        write_midi_file_from_generated(generate, midi_file_name, start_index=seq_len - 1, fs=8, max_generated=max_generate)

        # open midifile after manipulating duration data
        outfile = delta_change(midi_file_name)
        # open midi file in Musescore here
        openmidi = str('open ' + midi_file_name)
        print(openmidi)
        os.system(openmidi)

    # randomly generates the seed note from Carla's list of notes, to seed the NN process
    def carla_rnd(self):
        with open('training/data/carlaDNA-v9.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile))
            length = len(data)
            rnd = random.randrange(length)
            starting_note = data[rnd]
            print(starting_note)
            return starting_note

"""
--------------------------
-----mission control------
--------------------------
"""
class MissionControl():
    def __init__(self):
        print ('Mission control is online!')
        self.running = True

    def terminate(self):
        self.running = False

    def keyboard(self):
        """listens out for keyboard control"""
        while self.running:
            with keyboard.Listener(on_press=self.on_press) as listener:
                # break if keyboard is pressed for various reasons SPACE = ends prog
                listener.join()

    def snd_listen(self):
        pass

    def on_press(self, key):
        if key == keyboard.Key.space:
            print('end pressed')
            self.running = False
            return False

     def audio_comp(self):
        audio_bot = AudioBot()
        while self.running:
            # select file from random list
            self.snd = audio_bot.random_design()
            play(self.snd)
            #sleep(length/2)

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
    score.generatng_score() # asks score-bot to generate a score for performance


    # start threading. This is where the program starts
    mc = MissionControl() # initiates a bot to control the threading (multiple operations) in this program

    t1 = Thread(target=mc.keyboard) # listens to the keyboard for exit/ stop key (= space)
    t2 = Thread(target=mc.snd_listen, daemon=True) # starts the process of listening to the computer mic
    t3 = Thread(target=mc.audio_comp, daemon=True) # starts the process of randomly generating the sonic accompniment

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

