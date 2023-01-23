
colourName2RGB = {
    'red': (1, -1, -1), 
    'blue': (-1, -1, 1),
    'black': (-1, -1, -1)
}
# fixation cross parameters
fixation_cross_width = 2
fixation_cross_height = 30

fixation_cross_in_region_color = colourName2RGB['red']
fixation_cross_out_region_color = colourName2RGB['black']

fixation_trigger_allowance_pix = 40

fixation_duration_sec = 1
fixation_timeout_sec = 10


# search object parameters
bar_width = 10
bar_height = 50

target_param = {'colourRGB':colourName2RGB['red'], 'ori':45}

distractor_params = [
    {'colourRGB':colourName2RGB['red'], 'ori':-45},
    {'colourRGB':colourName2RGB['blue'], 'ori':45}, 
    ]

# array parameters
distractor_proportions = [[3.2, 6.8], [5, 5]]
num_row_column = [8, 10]
obj_spacing = 70

"""
10*10*0.5  = 50
10*10*0.32 = 32
8* 8* 0.5  = 32
8* 8* 0.32 = 20.48
"""


# experiment parameters

# per condition
# T/F * distractor_proportions * num_row_column * number_of_repeat
number_of_repeat = 45
maxWait = 1
accepted_keys = ['q', 'p']
inter_trial_interval = 1



"""
100 items / 20Hz = 5 seconds 
10 second per trial (2 sec fixation, 5 sec searching, 1 sec inter-trial)

10 minutes reading 
60 minutes visual search 
 
2(T/F)*2(set-size)*2(proportion) = 8

60*60sec/(10sec*8) = 45 
"""