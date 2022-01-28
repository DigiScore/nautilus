#!/usr/bin/env python3

import numpy as np
from time import sleep
import pyaudio
# from music21 import stream, converter, clef, meter
import glob
import random
import threading
from pydub import AudioSegment
from pydub.playback import play
import concurrent.futures

# import project modules
# from score import ScoreDev
# from audio import AudioBot

class Audio_engine():
    def __init__(self):
        print('Audio bot is now working')

        # define class params 4 audio listener
        self.go_bang = False # waiting from go from __main__
        self.running = True
        self.peak = 0
        self.CHUNK = 2 ** 11
        self.RATE = 44100

        # define class params 4 audio composer
        self.list_all_audio = glob.glob('data/audio/*.wav')
        self.num = len(self.list_all_audio)
        seed_rnd = random.randrange(self.num)
        random.seed(seed_rnd)
        random.shuffle(self.list_all_audio)

        # start listener thread
        print('Audio threading started')
        th1 = threading.Thread(target=self.listener)

        # start the composition thread
        th2 = threading.Timer(interval=0.1, function=self.audio_wrangler)

        th1.start()
        th2.start()

    def listener(self):
        # open the listener feed
        while self.running:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)
            self.data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
            self.peak = np.average(np.abs(self.data)) * 2
            bars = "#" * int(50 * self.peak / 2 ** 16)
            print("%05d %s" % (self.peak, bars))
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def audio_wrangler(self):
        # am listening for sound level above a certain threshold
        while self.running:
            while self.go_bang:
                chance_make = random.randrange(100)
                if self.peak > 4000:
                    if chance_make > 20: # 80% chance of playing if you activate me
                        print ('react to sound')
                        self.audio_comp()
                # if no audio detected then 50 % chance of self generatig a sound
                elif chance_make > 50:
                    print(f'{chance_make}   =  on my own')
                    self.audio_comp()

            # sleep(0.1)

    # todo replace with queue
    def audio_comp(self):
        snd = self.random_design()
        play(snd)

    def random_design(self):
        # choose a random file
        rnd_file = random.randrange(self.num)
        sound_file = self.list_all_audio[rnd_file]
        print('sound file = ', sound_file)
        sound = AudioSegment.from_wav(sound_file)

        # gain structure?
        gain_rnd = random.randrange(1)
        gain = 1  # gain_rnd + 0.5

        # play (sound)
        new_sound = self.speed_change(sound, gain)
        length = new_sound.duration_seconds
        print('length = ', length)
        fade_sound = new_sound.fade_in(1000).fade_out(500)
        return fade_sound

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


if __name__ == '__main__':
    audio_test = Audio_engine()
