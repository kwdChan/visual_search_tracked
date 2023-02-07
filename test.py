from modules import monitor_settings
from modules.visual_search.exp_stimuli import vertical_hexagon_array

from psychopy import sound, core, event
win = monitor_settings.get_psychopy_window()

#test = sound.Sound(value='C', secs=0.1, octave=7, sampleRate=44100).play()
#core.wait(1)

#test = sound.Sound(value='E', secs=0.1, octave=6, sampleRate=44100).play()
#core.wait(1)
#test = sound.Sound(value='D', secs=0.1, octave=6, sampleRate=44100).play()
print(event.waitKeys())