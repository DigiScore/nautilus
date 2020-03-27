from distutils.core import setup

APP = ['nautilus-v04']
DATA_FILES = ['/data/model/epochs4-long-model_ep4.h5', '/data/weights/epochs4-long-tokenizer.p']

setup(name=APP,
      version='1.0',
      data_files = DATA_FILES,
      py_modules=[APP],
      author='Craig Vear',
      author_email='cvear@dmu.ac.uk',
      )