"""main client script
controls microphone stream and audio generation"""

# get python libraries
import numpy as np
from time import sleep
import pyaudio
import glob
import random
import threading
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play


class AudioEngine:
    """controls listening and audio mainpulation when called"""
    def __init__(self, ai_engine):
        print('Audio engine is now working')

        # define class params 4 audio listener
        self.peak = 0
        self.running = True
        self.logging = False

        # define the audio queue (not used at this point)
        self.incoming_commands_queue = Queue()

        # own the AI data server
        self.aiEngine = ai_engine

        # set up mic listening funcs
        self.CHUNK = 2 ** 11
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

        # build send data dict
        self.send_data_dict = {'mic_level': 0,
                               'speed': 1,
                               'tempo': 0.1
                               }

        # define class params 4 audio composer
        self.list_all_audio = glob.glob('data/audio/*.wav')
        self.num = len(self.list_all_audio)
        seed_rnd = random.randrange(self.num)
        random.seed(seed_rnd)
        random.shuffle(self.list_all_audio)

        # # own the ai engine
        # self.aiEngine = aiEngine

        # start listener thread
        print('Audio threading started')
        # th1 = threading.Thread(target=self.parseQueueueue)

        # start the composition thread
        th2 = threading.Timer(interval=0.1, function=self.audio_wrangler)

        # th1.start()
        th2.start()
        #
        # # init got dict
        # self.got_dict = self.engine.datadict

    def snd_listen(self):
        print("mic listener: started!")
        #todo - could implement director in here
        while self.running:
            data = np.frombuffer(self.stream.read(self.CHUNK,
                                                  exception_on_overflow = False),
                                 dtype=np.int16)
            peak = np.average(np.abs(data)) * 2
            if peak > 2000:
                bars = "#" * int(50 * peak / 2 ** 16)
                print("%05d %s" % (peak, bars))
            self.send_data_dict['mic_level'] = peak # / 30000
            self.aiEngine.parse_got_dict(self.send_data_dict)

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def audio_wrangler(self):
        # am listening for sound level above a certain threshold
        print("wrangler started")
        while self.running:
            chance_make = random.randrange(100)
            if self.aiEngine.aiEmissionsQueue.qsize() > 0:
                print('react to sound')
                # self.incoming_commands_queue.put(1)
                _getSomething = self.aiEngine.aiEmissionsQueue.get()
                print("test", _getSomething)
                self.audio_comp()
                # self.aiEngine.aiEmissionsQueue.clear()

            # if no audio detected then 50 % chance of self generating a sound
            elif chance_make > 50:
                print(f'{chance_make}   =  on my own')
                # self.incoming_commands_queue = random.random()
                self.audio_comp()

            elif self.aiEngine.aiEmissionsQueue.qsize() == 0:
                # have a bit of time off
                rndSleep = random.randrange(2, 3)
                sleep(rndSleep)


    # audio shaping and design
    def audio_comp(self):
        snd = self.random_design()
        play(snd)

    # adds random gen params to audio object
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

    # randomly generate playback speed 0.3-0.5
    def speed_change(self, sound, vol):
        rnd_speed = random.randrange(5, 10)
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
