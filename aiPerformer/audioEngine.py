"""main client script
controls microphone stream and audio generation"""

# get python libraries
import numpy as np
from time import sleep, time
import pyaudio
import glob
import random
import threading
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play


class AudioEngine:
    """controls listening and audio mainpulation when called"""
    def __init__(self, ai_engine, aiDirector):
        print('Audio engine is now working')

        # define class params 4 audio listener
        self.peak = 0
        self.running = True
        self.logging = False

        # define the audio queue (not used at this point)
        self.incoming_commands_queue = Queue()

        # own the AI data server
        self.aiEngine = ai_engine

        # own the dircetor object
        self.aiDirector = aiDirector

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
        self.gain = 0

        # start listener thread
        print('Audio threading started')

        # start the composition thread
        th1 = threading.Timer(interval=0.1, function=self.audio_wrangler)

        # start timer thread
        th1.start()


    def snd_listen(self):
        print("mic listener: started!")
        oldbarcount = 0

        # loop starts here
        while self.running:

            #set up listening stream
            data = np.frombuffer(self.stream.read(self.CHUNK,
                                                  exception_on_overflow = False),
                                 dtype=np.int16)
            self.peak = np.average(np.abs(data)) * 2

            # do stuff with this data
            # if self.peak > 2000:
            #     bars = "#" * int(50 * self.peak / 2 ** 16)
            #     print("%05d %s" % (self.peak, bars))

            # share the data
            self.send_data_dict['mic_level'] = self.peak # / 30000
            self.aiEngine.parse_got_dict(self.send_data_dict)

            # todo - realtime analysis of live audio
            # how many spikes per section?

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def audio_wrangler(self):
        """listening for sound level above a certain threshold
        & controlling all the director timing"""

        print("wrangler started")

        while self.running:
            """part 1 - respond as sound"""
            chance_make = random.randrange(100)
            if self.aiEngine.aiEmissionsQueue.qsize() > 0:
                print('react to sound')
                # self.incoming_commands_queue.put(1)
                _getSomething = self.aiEngine.aiEmissionsQueue.get()
                # print("test", _getSomething)
                self.audio_comp()
                # self.aiEngine.aiEmissionsQueue.clear()

            # if no audio detected then 50 % chance of self generating a sound
            elif chance_make > 36:
                print(f'{chance_make}   =  on my own')
                # self.incoming_commands_queue = random.random()
                self.audio_comp()

            elif self.aiEngine.aiEmissionsQueue.qsize() == 0:
                # have a bit of time off
                rndSleep = random.randrange(2, 3)
                sleep(rndSleep)

            # """part 2 - listen to behaviour for triggering"""
            # # transition to section B = short dense events
            # if self.aiDirector.globalForm == 2:
            #     # is Carla giving us the Q?
            #     # short dense sounds
            #     # if self.peak >
            #     # todo - temporary fix


    def randomTime(self):
        nowTime = time()
        rndDuration = random.randrange(20, 120)
        return nowTime+rndDuration

    # audio shaping and design
    def audio_comp(self):
        if self.aiDirector.globalForm < 7:
            snd = self.random_design()

            # reverse for upside down world only
            if self.aiDirector.globalForm == 5:
                snd = snd.reverse()

            play(snd)

    # adds random gen params to audio object
    def random_design(self):
        # choose a random file
        rnd_file = random.randrange(self.num)
        sound_file = self.list_all_audio[rnd_file]
        print('sound file = ', sound_file)
        sound = AudioSegment.from_wav(sound_file)

        # gain structure for end fade
        if self.aiDirector.globalForm >= 6:
            # reduce the gain by 0.0083 every second for 120 secs
            self.gain -= 0.55

        # play (sound)
        new_sound = self.speed_change(sound, self.gain)
        # length = new_sound.duration_seconds
        # print('length = ', length)
        # fade_sound = new_sound.fade_in(5).fade_out(5)
        return new_sound

    # randomly generate playback speed 0.3-0.5
    def speed_change(self, sound, vol):
        """determines transposition rate onto audio files"""

        # determines pitch shift behaviours on global form
        # high pitch for ascension
        if self.aiDirector.globalForm >= 6:
            rndSpeed = random.randrange(20, 40)

        # normal pitch for section 5
        # (zone C upside down world)
        elif self.aiDirector.globalForm >= 5:
            rndSpeed = 10

        elif self.aiDirector.globalForm >= 4:
            rndSpeed = random.randrange(10, 40)

        # big range for transition into particle zone
        elif self.aiDirector.globalForm >= 2:
            rndSpeed = random.randrange(30, 45)

        # section A
        else:
            rndSpeed = random.randrange(5, 10)

        speed = rndSpeed / 10
        if speed == 0:
            speed = 1
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
    audio_test = AudioEngine()
