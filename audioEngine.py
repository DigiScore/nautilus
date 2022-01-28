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

# import project modules
# from score import ScoreDev
# from audio import AudioBot

class Audio_engine():
    def __init__(self):
        print('Audio bot is now working')

        # define class params 4 audio listener
        self.go_bang = False
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
        print('threading 1 started')
        th1 = threading.Thread(target=self.listener)
        th1.start()

        print('threading 2 started')

        # start the composition thread
        th2 = threading.Timer(0.1, self.audio_wrangler)
        th2.start()

    def listener(self):
        # open the listener feed
        while True:
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
        while True:
            if self.go_bang:
                chance_make = random.randrange(100)
                if self.peak > 4000:
                    if chance_make > 20: # 80% chance of playing if you activate me
                        print ('react to sound')
                        self.audio_comp()
                else:
                    #if no audio detected then 50% chance of self generatig a sound
                    if chance_make > 50:
                        print(f'{chance_make}   =  on my own')
                        self.audio_comp()

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




#
#
#
#
#     def show_score(self):
#         # make windows
#         window1 = Tk()
#
#         # create canvass
#         canvas_one = Canvas(window1, width=1024, height=600, bg='white')
#         canvas_one.pack()
#
#         # create image from each PNG and put in position on canvas
#         for img in self.images:
#             score = PhotoImage(file=img)
#         # score1_large = score1.zoom(2, 2)  # zoom 2x
#             mypart1 = canvas_one.create_image(512, 300, image=score)  # put in middle of canvas
#
#             window1.update()
#
#             sleep(10)
#
#         if not self.running:
#             window1.destroy()
#
# """
# ------------------------------------------------
# --------- main programme starts here -----------
# ------------------------------------------------
# """
#
# if __name__ == '__main__':
#     # # first we need to build model from trained files
#     # model = tf.keras.models.load_model('data/epochs4-long-model_ep4.h5' , custom_objects=SeqSelfAttention.get_custom_objects())
#     # note_tokenizer = pickle.load(open("data/epochs4-long-tokenizer.p", "rb"))
#
#
#     # #then we generate the score, save it to disk as .mid, then open it in MuseScore or sim.
#     # score = ScoreDev() # initiates a score bot to create the unique score
#     # carla_start_note = score.carla_rnd() # generates a start note from Carla's improv transcipt
#     # file_to_open = score.generatng_score(carla_start_note) # asks score-bot to generate a score for performance
#     # open_score = score.open_score(file_to_open) # score bot  or sim to open the generated .Mid file
#
#     # todo  replace with TK in control
#     # start threading. This is where the program starts
#     mc = MissionControl() # initiates a bot to control the threading (multiple operations) in this program
#
#     # t1 = Thread(target=mc.keyboard) # listens to the keyboard for exit/ stop key (= space)
#     t2 = Thread(target=mc.snd_listen, daemon=True) # starts the process of listening to the computer mic
#     t3 = Thread(target=mc.audio_wrangler, daemon=True) # starts the process of randomly generating the sonic accompniment
#     t4 = Thread(target=mc.show_score, daemon=True)
#
#     # here we go ... start your engines
#     # t1.start()
#     t2.start()
#     t3.start()
#     t4.start()
#
#     # when finished join all threads and close mission control
#     # t1.join()
#     t2.join()
#     t3.join()
#     t4.join()
