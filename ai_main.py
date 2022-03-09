# import python libs
import sys
from threading import Thread, Timer
from queue import Queue
from time import time

# import project libs
from audioEngine import AudioEngine
from ai_engine import AiDataEngine

class Director:
    """controls the overall behaviour and timing"""

    def __init__(self):
        # logs start time in seconds
        startTime = time()

        # transition into B section starts at 6 mins
        # triggered by density clouds of short attacks from Carla
        self.transA = startTime + 360

        # section B must start at 8 mins
        self.sectionB = startTime + 480

        # transition into C section starts after 30"
        # trans triggered by low C held note
        self.transC = self.sectionB + 30

        # section C must start by 11 mins
        self.sectionC = startTime + 660

        # end section (ascension) must start at 14 mins
        self.endSection = startTime + 840
        self.triggerEndFade = False

        # piece ends at 16 mins
        self.end = startTime + 960

    def conductor(self):
        """controls the overall behaviour and timing"""
        pass

        # get now time
        nowTime = time()

        # are we at the end of the piece?
        if nowTime >= self.end:
            sys.exit()

        # have we started the
        elif nowTime >= self.endSection:
            self.triggerEndFade = True


class Main:
    """start all the data threading
     pass it the master signal class for emmission"""

    def __init__(self):
        # instantiate the AI server
        engine = AiDataEngine(speed=0.1)

        # instantiate the dircetor
        aiDirector = Director()

        # instantiate the controller client and pass it te queue
        audioEngine = AudioEngine(engine, aiDirector)

        # declares all threads and starts the piece
        t1 = Thread(target=engine.make_data)
        t2 = Thread(target=engine.affect)
        t3 = Thread(target=audioEngine.snd_listen)

        # starts the conductor
        t4 = Timer(interval=0.1, function=aiDirector.conductor)

        # assigns them all daemons
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True

        # starts them all
        t1.start()
        t2.start()
        t3.start()
        t4.start()


if __name__ == "__main__":
    go = Main()
