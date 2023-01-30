
from .monitor_settings import deg2pix


colourName2RGB = {
    "red": (1, -1, -1),
    "blue": (-1, -1, 1),
    "black": (-1, -1, -1),
    "white": (1, 1, 1),
}
# fixation cross parameters
fixation_cross_width = 2
fixation_cross_height = 30

fixation_cross_in_region_color = colourName2RGB["red"]
fixation_cross_out_region_color = colourName2RGB["black"]

fixation_trigger_allowance_pix = 40

fixation_duration_sec = 1
fixation_timeout_sec = 10


# search object parameters
bar_colourRGB = colourName2RGB["white"]
big_bar_width = deg2pix(0.24)
big_bar_height = deg2pix(0.98)

small_bar_width = deg2pix(0.12)
small_bar_height = deg2pix(0.5)

target_param = {"width": small_bar_width, "height": small_bar_height, "ori": 0}

distractor_params = [
    {"width": small_bar_width, "height": small_bar_height, "ori": 90},
    {"width": big_bar_width, "height": big_bar_height, "ori": 0},
]

# array parameters
distractor_proportions = [[5, 5]]
num_row_column = [4, 9, 12]
obj_spacing = deg2pix(1)


# experiment parameters

# per condition
# T/F * distractor_proportions * num_row_column * number_of_repeat
number_of_repeat = 45
maxWait = 1
accepted_keys = ["q", "p"]
inter_trial_interval = 1


"""
Classic visual search paradigms (Li et al., 2007) were employed to measure attentional slope, a measure of attentional efficiency. Participants were presented with a conjunction search display (Eizo Flexscan F980 monitor, viewing distance = 135 cm, angular subtense = 12°) that had a variable number (set-size) of white (x = 0.3, y = 0.3, luminance = 25 cd/m2) distracter items — large vertical bars (0.98° × 0.24°) and small horizontal bars (0.12° × 0.50°) against a grey background (x = 0.3, y = 0.3, luminance = 18 cd/m2). In each trial, a target – a small vertical white bar – was either present or absent (see Fig. 1A). The observers' task was to make a rapid judgement as to whether the target was present or absent by pressing an appropriate button. The time taken for this decision (i.e., reaction time for correct trials) was then graphed as a function of set-size (Fig. 1C). The slope of this function (the search slope) determined the search rate (ms/item). Participants also performed a feature search task, where there was only one type of distracter – small horizontal bars (0.12° × 0.50°) – and the goal was to again find the small vertical target (Fig. 1B).


"""
