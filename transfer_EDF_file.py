import os

import pylink


os.chdir(os.path.dirname(__file__))

EDF_filename = '1'
el_tracker = pylink.EyeLink("100.1.1.1")
el_tracker.receiveDataFile(EDF_filename, './data/manual_transfer/'+EDF_filename+'.edf')