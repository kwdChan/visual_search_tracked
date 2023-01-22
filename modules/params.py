
colourName2RGB = {
    'red': (1, -1, -1), 
    'blue': (-1, -1, 1),
    'black': (-1, -1, -1)
}
# fixation cross parameters
fixation_cross_width = 10
fixation_cross_height = 50

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
    {'colourRGB':colourName2RGB['blue'], 'ori':45}, 
    {'colourRGB':colourName2RGB['red'], 'ori':-45}
    ]

# array parameters
distractor_proportions = [[6, 4], [5, 5]]
num_row_column = [7, 8, 9]
obj_spacing = 70

# experiment parameters

# per condition
# T/F * distractor_proportion * num_row_column * number_of_repeat
number_of_repeat = 10
n_repeats_per_session = 5
maxWait = 2
accepted_keys = ['q', 'p']
inter_trial_interval = .1



