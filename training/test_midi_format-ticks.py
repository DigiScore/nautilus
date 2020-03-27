from music21 import midi
import glob

for file in glob.glob("data/RELEASE2/*.midi"):
    print (file)
    mf = midi.MidiFile()
    mf.open(file, attrib='rb')
    mf.read()
    # print (mf)
    # mf.writeMThdStr()
    print (mf.ticksPerQuarterNote)
    if mf.ticksPerSecond != None:
        print ('ticks')
        mf.readstr(1024)
        print (mf.ticksPerQuarterNote)
    mf.close()

#mf.write()
# m
#
