from __future__ import absolute_import, division

# calibrate it for the same luminance
colourRGB = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),

}

# stimulus parameter
array_radius = lambda n_obj: (30*pow(n_obj, 1/2))
bar_width=20*2
#bar_width=5*2
bar_height= 5*2

# orientation and color
conj_target_param =  (0, 'red')
conj_distractor_params = [(90, 'red'), (0, 'blue')]
popout_target_param =  (0, 'red')
popout_distractor_params = [(90, 'red')]

# contrast jittering, flat distribution
minimum_contrast = 0.7
maximum_contrast = 1

# trial parameters
set_sizes = [4, 16, 64]
n_repeats_per_session = 5

maxWait = 2
accepted_keys = ['q', 'p']
inter_trial_interval = .1
rest_interval = 10


# fixation cross
fixation_cross_width = 20
fixation_cross_height = 100
fixation_duration = 1


