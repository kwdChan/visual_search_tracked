from psychopy import visual, core, event, monitors, gui
def get_psychopy_window():
    """
    class psychopy.visual.Window(size=800, 600, pos=None, color=0, 0, 0, colorSpace='rgb', rgb=None, dkl=None, lms=None, fullscr=None, allowGUI=None, monitor=None, bitsMode=None, winType=None, units=None, gamma=None, blendMode='avg', screen=0, viewScale=None, viewPos=None, viewOri=0.0, waitBlanking=True, allowStencil=False, multiSample=False, numSamples=2, stereo=False, name='window1', checkTiming=True, useFBO=False, useRetina=True, autoLog=True, gammaErrorPolicy='raise', bpc=8, 8, 8, depthBits=8, stencilBits=8, backendConf=None)
    """
    mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)
    win = visual.Window(fullscr=True,
                        monitor=mon,
                        #winType='pyglet',
                        units='pix')
    #event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)

    return win



