# # import python modules
import os
from time import time
from operator import itemgetter

# # import project modules
from brown.common import *


class ImageGen:
    """generates png images using Brown from
    the raw midi data supplied by Neural Nets"""
    def __init__(self):
        print('setting up')
        brown.setup()
        self.staff_unit = 5
        self.first_note_offset = 0

    def make_image(self, note_dict):
        """generate a random seq of notes on a staff
        using current harmonic seq as guide"""
        # brown.setup()
        pitch, octave, duration = itemgetter("pitch",
                                             "octave",
                                             "duration")(note_dict)

        # make flow env for notes. gap + offset on left + gap right
        manuscript_width = self.staff_unit * 2

        # create coordinate space container
        flow = Flowable((Mm(0), Mm(0)), Mm(manuscript_width), Mm(30))

        # generate a staff in the container
        # staff = Staff((Mm(0), Mm(0)), Mm(100), flow)
        staff = Staff((Mm(0), Mm(0)), Mm(manuscript_width), flow, Mm(1))

        # populate it with music furniture
        InvisibleClef(staff, Mm(0), 'treble')

        # parse music21 details to brown notation
        # e.g. Music21 = G#, octave 5 - brown = gs'

        # find if # or b
        if len(pitch) > 1:
            if pitch[-1] == "#":
                accidental = "s"
            else:
                accidental = "f"
            note = pitch[0].lower() + accidental

        else:
            note = pitch[0].lower()

        # calc octave (4 = lowest!!)
        if octave > 4:
            ticks = octave - 4
            for t in range(ticks):
                note += "'"

        if duration > 8:
            duration = 8
        else:
            int(duration)

        print(f'printed note  ===== {note}')
        Chordrest(Mm(self.staff_unit), staff, [note], Beat(int(duration), 4))

        # save as a png render
        image_path = os.path.join(os.path.dirname(__file__), 'data/images',
                                  f'nautilus-{time()}-{note}-{duration}.png')

        try:
            brown.render_image((Mm(0), Mm(0), Mm(75), Mm(75)), image_path,
                           dpi=600,
                           bg_color=Color(0, 120, 185, 0),
                           autocrop=True)
        except:
            print('print error')

        # brown.show()

        # reset the notation renderer
        staff.remove()
        flow.remove()


if __name__ == "__main__":
    pitches = ["A", "A#", "B-", "B", "C-", "C",
               "C#", "D-", "D", "D#", "E-",
               "E", "E#", "F-", "F", "F#", "G-",
               "G", "G#", "A-"]

    octave = [4, 5, 6]

    test = ImageGen()

    for octav in octave:
        for pitch in pitches:
            pitch_dict = {"pitch": pitch, "octave": octav, "duration": 4}

    # test_dict = {"pitch": "G", "octave": 7, "duration": 14}

            test.make_image(pitch_dict)
