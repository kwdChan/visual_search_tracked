from psychopy import core, event, visual
from modules.visual_search.exp_stimuli import Visual_search_stimulus_condition

from modules import monitor_settings

win = monitor_settings.get_psychopy_window()

cond = Visual_search_stimulus_condition(
    win=win,
    n_columns = 12,
    n_rows = 12,
    obj_distance = 70,
    target_params = dict(colour='red', ori=45),
    distractor_params = [dict(colour='blue', ori=45), dict(colour='red', ori=-45)],
    distractor_occurances = [6, 4]

)

while True: 
    cond.draw(True)
    win.flip()
    event.waitKeys()