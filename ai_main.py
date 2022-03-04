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
        # todo - need to implement some sort of director for the
        # instantiate the AI server
        engine = AiDataEngine(speed=0.1)

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
