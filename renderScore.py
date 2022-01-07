# # import python modules
import os
from time import time
from operator import itemgetter

# # import project modules
from brown.common import *


class ImageGen:
    def __init__(self):
        print('setting up')
        brown.setup()
        self.staff_unit = 10
        self.first_note_offset = self.staff_unit / 2

    def make_image(self, note_dict):
        """generate a random seq of notes on a staff
        using current harmonic seq as guide"""
        # brown.setup()
        pitch, octave, duration = itemgetter("pitch",
                                             "octave",
                                             "duration")(note_dict)

        # make flow env for nots
        manuscript_width = (duration + 1) * self.staff_unit + self.first_note_offset

        # create coordinate space container
        flow = Flowable((Mm(0), Mm(0)), Mm(manuscript_width), Mm(30))

        # generate a staff in the container
        # staff = Staff((Mm(0), Mm(0)), Mm(100), flow)
        staff = Staff((Mm(0), Mm(0)), Mm(manuscript_width), flow, Mm(1))

        # populate it with music furniture
        Clef(staff, Mm(0), 'treble')

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

        print(note)

        print(f'printed note  ===== {note}')
        Chordrest(Mm(self.first_note_offset + self.staff_unit), staff, [note], Beat(int(duration), 4))

        # now = datetime.now()
        # time = now.strftime("%d-%m-%Y-%H-%M-%S")
        # # save as a png render
        image_path = os.path.join(os.path.dirname(__file__), 'data/images',
                                  f'nautilus-{time()}.png')

        brown.render_image((Mm(0), Mm(0), Mm(manuscript_width * 2), Mm(75)), image_path,
                           dpi=200,
                           bg_color=Color(0, 120, 185, 0),
                           autocrop=True)

        # brown.show()

        # reset the notation renderer
        staff.remove()
        flow.remove()

        # return image_path

if __name__ == "__main__":
    test_dict = {"pitch": "G", "octave": 7, "duration": 14}
    test = ImageGen()
    test.make_image(test_dict)
