import glob
import random
from pydub import AudioSegment
from pydub.playback import play
from time import sleep
from pynput import keyboard

# state all vaiables
list_all_audio = glob.glob('data/audio/*.wav')
num = len(list_all_audio)
print (num)
seed_rnd = random.randrange(num)
random.seed(seed_rnd)
random.shuffle(list_all_audio)
print (list_all_audio)
break_program = False

# define all methods and functions
def speed_change(sound, vol):
    # randomly generate playback speed 0.2-0.5
    rnd_speed = random.randrange(2, 5)
    speed = rnd_speed / 10
    print ('change of speed = ', speed)
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

def on_press(key):
    global break_program
    print (key)
    if key == keyboard.Key.space:
        print ('end pressed')
        break_program = True
        return False

# this is where the progran starts
with keyboard.Listener(on_press=on_press) as listener:
    while break_program == False:
        # select file from random list
        rnd_file = random.randrange(num)
        sound_file = list_all_audio[rnd_file]
        print ('sound file = ', sound_file)
        sound = AudioSegment.from_wav(sound_file)
        # gain structure?
        gain_rnd = random.randrange(2)
        gain = gain_rnd + 1
        # play (sound)
        new_sound = speed_change(sound, gain)
        length = new_sound.duration_seconds
        print('length = ', length)
        fade_sound = new_sound.fade_in(1000).fade_out(500)
        play(fade_sound)
        sleep(length)
    listener.join()
