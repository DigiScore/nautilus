from robots.robot import Robot
from robots.arm import Arm
from piano import Piano
from random import randrange, getrandbits
from time import sleep
import config

class SoundBot:
    def __init__(self, harmony_signal):
        # is the robot connected
        self.robot_connected = config.robot_connected
        self.arm_connected = config.arm_connected
        self.direction = 1
        self.speed_factor = 0.3

        # instantiate robot
        if self.robot_connected:
            self.robot_robot = Robot()

        if self.arm_connected:
            self.robot_arm = Arm()
            self.robot_arm.wait_ready()

        # instanstiate piano player class and pass harmony_signal
        self.harmony_signal = harmony_signal
        self.piano = Piano(self.harmony_signal)

    # def sound_bot(self):
    #     # make a serial port connection here
    #     print('im here sound bot - sleeping for 3')
    #     # sleep(3)
    #
    #     # then start improvisers
    #     while True:
    #         print('im here4')
    #         # grab raw data from engine stream
    #         raw_data_from_dict = self.got_dict['master_output']
    #         rhythm_rate = self.got_dict['rhythm_rate']
    #         # print('data = ', raw_data_from_dict, rhythm_rate)
    #
    #         # make a sound & move bot
    #         self.make_sound(raw_data_from_dict, rhythm_rate)
    #         print('making a new one')


    def make_sound(self, incoming_raw_data, rhythm_rate):
        # # temp random num gen
        # rnd = randrange(self.audio_dir_len)
        # print(self.audio_dir[rnd])
        # print('making sound')

        # # make some duration decisions
        # intensity = self.got_dict['self_awareness']
        # len_delta = (random() + intensity) * 1000
        # duration = rhythm_rate + len_delta
        #
        # # print('duration = ', duration)
        #

        # send make sound signal to piano
        self.piano.note_to_play(incoming_raw_data, rhythm_rate)

        # move bot
        if self.robot_connected:
            self.move_robot(incoming_raw_data, rhythm_rate)
        else:
            sleep(rhythm_rate)

        # move arm
        if self.arm_connected:
            self.move_arm(incoming_raw_data, rhythm_rate)
        else:
            sleep(rhythm_rate)

        # print('fininshed a play')


    def move_robot(self, incoming_data, duration):
        # which movement: fwd, back, left, right
        # define movement
        rnd_move = randrange(4)

        rnd_speed = randrange(1, 5)
        rnd_speed = rnd_speed * self.speed_factor  # int(rnd_speed * self.speed_factor)

        # move an arm joint
        if rnd_move == 0:
            self.robot_robot.forward(rnd_speed)

        elif rnd_move == 1:
            self.robot_robot.backward(rnd_speed)

        elif rnd_move == 2:
            self.robot_robot.left(rnd_speed)

        elif rnd_move == 3:
            self.robot_robot.right(rnd_speed)

        # sleep for duration then send a stop command
        sleep(duration / 1000)
        self.robot_robot.stop()

    def move_arm(self, incoming_data, duration):

        if getrandbits(1):
            # select a joint
            rnd_joint = randrange(4)

            # rnd direction
            rnd_direction = randrange(2)
            if rnd_direction == 1:
                direction = -20
            else:
                direction = 20

            rnd_speed = randrange(3, 15)
            # rnd_speed *= 10

            # move an arm joint
            # if rnd_joint <= 15:
            joint = rnd_joint + 1
            self.robot_arm.move_joint_relative_speed(joint, direction, rnd_speed)


            # sleep for duration then send a stop command
            # sleep(duration / 1000)
            # self.robot_robot.stop()
