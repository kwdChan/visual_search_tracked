from psychopy import visual, core, event, monitors, gui
import psychopy

import numpy as np
WIN_PIX = [2048, 1152]
MONITOR_WIDTH_CM = 60
MONITOR_DISTANCE_CM = 70.0
psychopy.prefs.hardware['audioLib'] = [ 'PTB','pyo', 'sounddevice', 'pygame' ]

def get_psychopy_window():
    """
    class psychopy.visual.Window(size=800, 600, pos=None, color=0, 0, 0, colorSpace='rgb', rgb=None, dkl=None, lms=None, fullscr=None, allowGUI=None, monitor=None, bitsMode=None, winType=None, units=None, gamma=None, blendMode='avg', screen=0, viewScale=None, viewPos=None, viewOri=0.0, waitBlanking=True, allowStencil=False, multiSample=False, numSamples=2, stereo=False, name='window1', checkTiming=True, useFBO=False, useRetina=True, autoLog=True, gammaErrorPolicy='raise', bpc=8, 8, 8, depthBits=8, stencilBits=8, backendConf=None)
    """
    mon = monitors.Monitor('myMonitor', width=MONITOR_WIDTH_CM, distance=MONITOR_DISTANCE_CM)
    win = visual.Window(
        fullscr=True,
        size = WIN_PIX,
        monitor=mon,
        color=(0,0,0),
        #winType='pyglet',
        units='pix')
    return win


def cm2pix(cm):
    return int(cm*WIN_PIX[0]/MONITOR_WIDTH_CM)

def deg2pix(deg):
    assert deg > 0
    len_in_cm = MONITOR_DISTANCE_CM*np.tan(deg2rad(deg))
    return cm2pix(len_in_cm)

def deg2rad(deg):
    return np.pi*deg/180
