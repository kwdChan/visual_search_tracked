from modules.eye_tracking import tracker_setup
from modules.visual_search import exp_stimuli
from modules import monitor_settings
from psychopy import core
import os, random
from modules.experiment_control import EyeTrackingVisualSearchExperiment
from modules.visual_search import my_param
from modules.components import Gaze_trigger_v2
from psychopy import visual, core, event, monitors, gui

#from psychopy.preferences import prefs
#prefs.general['shutdownKey'] = 'b'
os.chdir(os.path.dirname(__file__))






class EyeTrackingSerialSearchExperiment(EyeTrackingVisualSearchExperiment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def trial(self, n_obj, is_present):

        tracker = self.tracker
        win = tracker.win
        el_tracker = tracker.el_tracker

        # inter-trial intervals
        core.wait(my_param.inter_trial_interval)

        # start recording
        recording_ok = tracker.start_recording(self.current_trial_index)

        # if failed to record
        if not recording_ok: return 'redo_now'


        # wait for fixation 
        gaze_trigger_ok = Gaze_trigger_v2(tracker, target_pos_psychopy_coor=(0,0)).waitTrigger()

        # if failed to fixate, recalibration needed, or tracker disconnected
        if not gaze_trigger_ok: return 'redo_now'
        el_tracker.sendMessage('gaze_trigger_ok')


        # stimuli presented
        obj_param_df = exp_stimuli.draw_search_array_temp(win, n_obj, is_present)
        win.flip()
        el_tracker.sendMessage('stim_onset')


        # wait for reseponse 
        waitResponse = event.waitKeys(maxWait=my_param.maxWait, keyList=my_param.accepted_keys, timeStamped=core.Clock())
        win.flip()
        el_tracker.sendMessage('blank_screen')


        # stop recording
        tracker.stop_recording()


        # record responses (local)
        data = dict(is_present=is_present, n_obj=n_obj)
        if waitResponse is None:
            response = None, my_param.maxWait
        else: 
            response = waitResponse[0]

        data['keyPressed'], data['timeTaken'] = response

        self.visual_search_subject.current_session.record_trial_data(obj_param_df, **data)

        # record trial variables to the EDF data file, for details, see Data 
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        tracker.record_variables_end_of_trial(
            key_pressed = response[0], 
            response_time_msec = response[1]*1000
        )

        return 'completed'

def trial_params():
    _set_sizes = my_param.set_sizes + my_param.set_sizes
    _is_present = [True]*len(my_param.set_sizes ) + [False]*len(my_param.set_sizes)

    trial_parameters = []
    for i_set_sizes, i_is_present in zip(_set_sizes,_is_present):
        trial_parameters.append(dict(n_obj=i_set_sizes, is_present=i_is_present))

    trial_parameters = trial_parameters*my_param.n_repeats_per_session
    random.shuffle(trial_parameters)
    return trial_parameters




exp = EyeTrackingSerialSearchExperiment(subjectID='TEST',sessionID='t123444', datapath='./data', dummy_mode=True)
event.globalKeys.add(key='c', modifiers=['ctrl'], func=exp.lastTrial, name='shutdown')


exp.set_trial_sequence(trial_params())
exp.tracker.calibrate()
exp.run()



