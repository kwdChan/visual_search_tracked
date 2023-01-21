import pylink, os, random, time, sys, json
from modules import recorder, my_param
from pathlib import Path
from psychopy import gui
subjectID = 'TEST'



dataFolder = './data'
os.chdir(os.path.dirname(__file__))
subject = recorder.Subject(os.path.join(dataFolder, subjectID))



blockTypes = ['serial', 'parallel', 'read']
myDlg = gui.Dlg(title="Experiment")
for blockID in blockTypes:
    myDlg.addField(blockID, False)

myDlg.show()