"""
------------------------------------
----- audio file manipulation ------
------------------------------------
"""


import glob
import random

from pydub import AudioSegment
from pydub.playback import play

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

