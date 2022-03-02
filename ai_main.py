# import python libs
from threading import Thread
from queue import Queue

# import project libs
from audioEngine import AudioEngine
from ai_engine import AiDataEngine


class AIData:
    """start all the data threading
     pass it the master signal class for emmission"""

    def __init__(self):
        # # start a thread to wait for commands to write
        # self.incoming_commands_queue = Queue()

        # instantiate the AI server
        engine = AiDataEngine(speed=1)

        # instantiate the controller client and pass it te queue
        audioEngine = AudioEngine(engine)

        # declares all threads
        t1 = Thread(target=engine.make_data)
        t2 = Thread(target=engine.affect)
        t3 = Thread(target=audioEngine.snd_listen)
        # t4 = Thread(target=cl.data_exchange)
        # t5 = Thread(target=cl.sound_bot)

        # assigns them all daemons
        t1.daemon = True
        t2.daemon = True
        # t3.daemon = True
        # t4.daemon = True

        # starts them all
        t1.start()
        t2.start()
        t3.start()
        # t4.start()
        # t5.start()


if __name__ == "__main__":
    go = AIData()

    # listeningThread = Thread(target=listening, args=(incoming_commands_queue,), daemon=True)
    # listeningThread.start()
    #
    #
    # ai_signal = GotAISignal()
    #
    # # and connect to emitting stream
    # ai_signal.ai_str.connect(self.got_ai_signal)
    #
    # # open a signal streamer for music harmony reporting
    # harmony_signal = GotMusicSignal()
    #
    # # and connect to emitting stream
    # harmony_signal.harmony_str.connect(self.got_harmony_signal)
    #
    # # init the harmony dict
    # self.harmony_dict = {}
    #
    # # # init the image generator to get notes for bespoke images
    # # self.image_gen = ImageGen()
    #
    # # start the ball rolling with all data generation and parsing
    # self._ai_data_engine = AIData(ai_signal, harmony_signal)
