from psychopy import core, event, visual
from modules.visual_search.exp_stimuli import draw_from_df, draw_object, get_search_array_df

from modules import monitor_settings

win = monitor_settings.get_psychopy_window()

df = get_search_array_df(
    n_rows=12, 
    n_columns = 12,
    obj_distance=70, 
    is_target_present=True, 
    target_param = dict(colourRGB=(0,0,255), ori=45), 
    distractor_params = [dict(colourRGB=(255,0,0), ori=45), dict(colourRGB=(0,0,255), ori=-45)], 
    distractor_proportion= [6, 4]
    
    )

draw_from_df(win, draw_object, df , dict(width=10, height=50))
win.flip()
event.waitKeys()