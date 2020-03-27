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

# state all vaiables
list_all_audio = glob.glob('data/audio/*.wav')
num = len(list_all_audio)
print (num)
seed_rnd = random.randrange(num)
random.seed(seed_rnd)
random.shuffle(list_all_audio)
print (list_all_audio)
break_program = False

# define all classes

class NoteTokenizer:
    def __init__(self):
        self.notes_to_index = {}
        self.index_to_notes = {}
        self.num_of_word = 0
        self.unique_word = 0
        self.notes_freq = {}


def piano_roll_to_pretty_midi(piano_roll, fs=100, program=0):
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


def generate_batch_song(list_all_midi, batch_music=16, start_index=0, fs=30, seq_len=50, use_tqdm=False):
    """
    Generate Batch music that will be used to be input and output of the neural network
    Parameters
    ==========
    list_all_midi : list
      List of midi files
    batch_music : int
      A number of music in one batch
    start_index : int
      The start index to be batched in list_all_midi
    fs : int
      Sampling frequency of the columns, i.e. each column is spaced apart
        by ``1./fs`` seconds.
    seq_len : int
      The sequence length of the music to be input of neural network
    use_tqdm : bool
      Whether to use tqdm or not in the function
    Returns
    =======
    Tuple of input and target neural network
    """

    assert len(list_all_midi) >= batch_music
    dict_time_notes = generate_dict_time_notes(list_all_midi, batch_music, start_index, fs, use_tqdm=use_tqdm)

    list_musics = process_notes_in_song(dict_time_notes, seq_len)
    collected_list_input, collected_list_target = [], []

    for music in list_musics:
        list_training, list_target = generate_input_and_target(music, seq_len)
        collected_list_input += list_training
        collected_list_target += list_target
    return collected_list_input, collected_list_target


def generate_dict_time_notes(list_all_midi, batch_song=16, start_index=0, fs=30, use_tqdm=True):
    """ Generate map (dictionary) of music ( in index ) to piano_roll (in np.array)
    Parameters
    ==========
    list_all_midi : list
        List of midi files
    batch_music : int
      A number of music in one batch
    start_index : int
      The start index to be batched in list_all_midi
    fs : int
      Sampling frequency of the columns, i.e. each column is spaced apart
        by ``1./fs`` seconds.
    use_tqdm : bool
      Whether to use tqdm or not in the function
    Returns
    =======
    dictionary of music to piano_roll (in np.array)
    """
    assert len(list_all_midi) >= batch_song

    dict_time_notes = {}
    process_tqdm_midi = tqdm(
        range(start_index, min(start_index + batch_song, len(list_all_midi)))) if use_tqdm else range(start_index, min(
        start_index + batch_song, len(list_all_midi)))
    for i in process_tqdm_midi:
        midi_file_name = list_all_midi[i]
        if use_tqdm:
            process_tqdm_midi.set_description("Processing {}".format(midi_file_name))
        try:  # Handle exception on malformat MIDI files
            midi_pretty_format = pretty_midi.PrettyMIDI(midi_file_name)
            piano_midi = midi_pretty_format.instruments[0]  # Get the piano channels
            piano_roll = piano_midi.get_piano_roll(fs=fs)
            dict_time_notes[i] = piano_roll
        except Exception as e:
            print(e)
            print("broken file : {}".format(midi_file_name))
            pass
    return dict_time_notes


def generate_input_and_target(dict_keys_time, seq_len=50):
    """ Generate input and the target of our deep learning for one music.
    Parameters
    ==========
    dict_keys_time : dict
      Dictionary of timestep and notes
    seq_len : int
      The length of the sequence
    Returns
    =======
    Tuple of list of input and list of target of neural network.
    """
    # Get the start time and end time
    start_time, end_time = list(dict_keys_time.keys())[0], list(dict_keys_time.keys())[-1]
    list_training, list_target = [], []
    for index_enum, time in enumerate(range(start_time, end_time)):
        list_append_training, list_append_target = [], []
        start_iterate = 0
        flag_target_append = False  # flag to append the test list
        if index_enum < seq_len:
            start_iterate = seq_len - index_enum - 1
            for i in range(start_iterate):  # add 'e' to the seq list.
                list_append_training.append('e')
                flag_target_append = True

        for i in range(start_iterate, seq_len):
            index_enum = time - (seq_len - i - 1)
            if index_enum in dict_keys_time:
                list_append_training.append(','.join(str(x) for x in dict_keys_time[index_enum]))
            else:
                list_append_training.append('e')

        # add time + 1 to the list_append_target
        if time + 1 in dict_keys_time:
            list_append_target.append(','.join(str(x) for x in dict_keys_time[time + 1]))
        else:
            list_append_target.append('e')
        list_training.append(list_append_training)
        list_target.append(list_append_target)
    return list_training, list_target


def process_notes_in_song(dict_time_notes, seq_len=50):
    """
    Iterate the dict of piano rolls into dictionary of timesteps and note played
    Parameters
    ==========
    dict_time_notes : dict
      dict contains index of music ( in index ) to piano_roll (in np.array)
    seq_len : int
      Length of the sequence
    Returns
    =======
    Dict of timesteps and note played
    """
    list_of_dict_keys_time = []

    for key in dict_time_notes:
        sample = dict_time_notes[key]
        times = np.unique(np.where(sample > 0)[1])
        index = np.where(sample > 0)
        dict_keys_time = {}

        for time in times:
            index_where = np.where(index[1] == time)
            notes = index[0][index_where]
            dict_keys_time[time] = notes
        list_of_dict_keys_time.append(dict_keys_time)
    return list_of_dict_keys_time


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


def carla_rnd():
    with open('training/data/carlaDNA-v9.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
        length = len(data)
        rnd = random.randrange(length)
        starting_note = data[rnd]
        print(starting_note)
        return starting_note


def speed_change(sound, vol):
    # randomly generate playback speed 0.3-0.5
    rnd_speed = random.randrange(3, 5)
    speed = rnd_speed / 10
    print ('change of speed = ', speed)
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


def on_press(key):
    global break_program
    if key == keyboard.Key.space:
        print ('end pressed')
        break_program = True
        return False

# --------- programme starts here -----------
if __name__ == '__main__':
    # build model from trained files
    model = tf.keras.models.load_model('data/epochs4-long-model_ep4.h5', custom_objects=SeqSelfAttention.get_custom_objects())
    note_tokenizer  = pickle.load(open("data/epochs4-long-tokenizer.p", "rb"))

    # generate midi files
    max_generate = 100
    unique_notes = note_tokenizer.unique_word
    seq_len = 50

    #  generation from a single Carla DNA note
    starting_note = "".join(carla_rnd())
    generate = generate_from_one_note(note_tokenizer, starting_note)

    generate = generate_notes(generate, model, unique_notes, max_generate, seq_len)
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y-%H-%M-%S")
    midi_file_name = "data/output/nautilus" + current_time + ".mid"
    print (midi_file_name)
    write_midi_file_from_generated(generate, midi_file_name, start_index=seq_len-1, fs=8, max_generated = max_generate)

    # open midi file in Musescore here
    openmidi = str('open '+ midi_file_name)
    print (openmidi)
    os.system(openmidi)

    # this is where the progran starts
    with keyboard.Listener(on_press=on_press) as listener:
        while break_program == False:
            # select file from random list
            rnd_file = random.randrange(num)
            sound_file = list_all_audio[rnd_file]
            print ('sound file = ', sound_file)
            sound = AudioSegment.from_wav(sound_file)
            # gain structure?
            gain_rnd = random.randrange(2)
            gain = gain_rnd + 1
            # play (sound)
            new_sound = speed_change(sound, gain)
            length = new_sound.duration_seconds
            print('length = ', length)
            fade_sound = new_sound.fade_in(1000).fade_out(500)
            play(fade_sound)
            sleep(length)
        listener.join()
