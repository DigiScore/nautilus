# import python libs
import concurrent.futures
import sys
from threading import Thread, Timer
from random import randrange
from time import time, sleep
from concurrent import futures
from pynput.keyboard import Key, Listener
from pynput import keyboard

# import project libs
from audioEngine import AudioEngine
from ai_engine import AiDataEngine

class Director:
    """controls the overall behaviour and timing"""

    def __init__(self):
        # logs start time in seconds
        startTime = time()

        self.waitForSpaceFlag = True

        # todo - this is a wizard-of-oz HACK
        # todo - need to implement the 2 audio analysis transistions

        # 1) global form starts at 1
        self.globalForm = 1

        # 2) transition into B section starts at 6 mins
        # triggered by density clouds of short attacks from Carla
        self.transA = startTime + 360

        # 3) section B must start before 8 mins or when triggered by Carla
        self.sectionB = self.transA + randrange(20, 60) # startTime + 480

        # 4) transition into C section starts after 30"
        # trans triggered by low C held note
        self.transC = self.sectionB + 30

        # 5) section C must start by 11 mins
        self.sectionC = self.transC + randrange(30, 150) # startTime + 660
        # self.pitchChange = "low"

        # 6) end section (ascension) must start at 14 mins
        self.endSection = startTime + 840
        # self.triggerEndFade = False

        # 7) piece ends at 16 mins
        self.end = startTime + 960

        # # start keyboard listening thread
        # with Listener(on_press=self.getKey) as listener:
        #     listener.join()

    def getKey(self):
        self.waitForSpaceFlag = False

    def conductor(self):
        """controls the overall behaviour and timing"""

        # determime which section we are in
        # get now time
        nowTime = time()

        # are we at the end of the piece?
        if nowTime >= self.end:
            self.globalForm = 7
            print("================\t\t\t\tFinsihed")

        # last section (ascension)
        elif nowTime >= self.endSection:
            # self.triggerEndFade = True
            self.globalForm = 6
            print("================\t\t\t\tAscension")

        elif nowTime >= self.sectionC:
            # self.pitchChange = "high"
            self.globalForm = 5
            print("================\t\t\t\tSection C")

        elif nowTime >= self.transC:
            # self.pitchChange = "norm"
            self.globalForm = 4
            print("================\t\t\t\tTransition to Section C")

        elif nowTime >= self.sectionB:
            self.globalForm = 3
            print("================\t\t\t\tSection B")

        elif nowTime >= self.transA:
            self.globalForm = 2
            print("================\t\t\t\tTransition to Section B")

    def keyboardControl(self):
        # determime which section we are in
        # get now time
        while True:
            nowTime = time()

            # check if end section
            if self.globalForm >= 5:

                if time() >= endEnd:
                    self.globalForm = 7
                    print("================\t\t\t\tFinsihed")

                elif time() >= endStartPoint:
                    self.globalForm = 6
                    print("================\t\t\t\tAscension")

            elif self.globalForm >= 4:
                if not self.waitForSpaceFlag:
                # if keyboard.is_pressed('space'):
                    # self.pitchChange = "high"
                    self.globalForm = 5
                    print("================\t\t\t\tSection C")

                    # end points are 4 and 6 mins after this press
                    endStartPoint = time() + 240
                    endEnd = time() + 360
                    self.waitForSpaceFlag = True

            # move auto into trans2
            elif self.globalForm >= 3:
                if time() >= sectionBStarTime + 3:
                    self.globalForm = 4
                    print("================\t\t\t\tTransition to Section C")

            # wait for a #2 to be pressed for end of trans A
            elif self.globalForm >= 2:
                if self.waitForSpaceFlag == False:
                    # if keyboard.is_pressed('space'):
                    print("moving to section B")
                    self.globalForm = 3
                    print("================\t\t\t\tSection B")

                    # reset the timer
                    sectionBStarTime = time()
                    self.waitForSpaceFlag = True

            # move into section 2 automatically
            elif nowTime >= self.transA:
                self.globalForm = 2
                print("================\t\t\t\tTransition to Section B")

            print(f'global form is currently {self.globalForm}')
            self.waitForSpaceFlag = True
            sleep(1)

class Main:
    """start all the data threading"""

    def __init__(self):
        # instantiate the AI server
        engine = AiDataEngine(speed=0.1)

        # wait to go
        _empty = input('ready to go ("1")?')

        # instantiate the dircetor
        self.aiDirector = Director()

        # instantiate the controller client and pass it te queue
        audioEngine = AudioEngine(engine, self.aiDirector)

        # declares all threads and starts the piece
        t1 = Thread(target=engine.make_data)
        t2 = Thread(target=engine.affect)
        t3 = Thread(target=audioEngine.snd_listen)

        # starts the conductor
        t4 = Thread(target=self.aiDirector.keyboardControl)

        # assigns them all daemons
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True

        # starts them all
        t1.start()
        t2.start()
        t3.start()
        t4.start()

        # start keyboard listening thread
        with Listener(on_press=self.getKey) as listener:
            listener.join()

    def getKey(self, key):
        print("changing flag", key)
        self.aiDirector.waitForSpaceFlag = False


if __name__ == "__main__":
    go = Main()
