import itertools
import os
import random

from psychopy import core, event, gui, monitors, visual
from modules import monitor_settings

from modules.components import Gaze_trigger_v3
from modules.experiment_control import EyeTrackingVisualSearchExperiment
from modules.eye_tracking import tracker_setup
from modules.visual_search import exp_stimuli

import session_info
os.chdir(os.path.dirname(__file__))

if session_info.stimulus_type == 'serial':
    from modules import params_serial_search as params

elif session_info.stimulus_type == 'parallel':
    from modules import params_feature_search as params
else: 
    raise ValueError('stimulus_type must be either serial or parallel')

fixation_params = params.fixation_params
fixation_params['trigger_allowance_pix']=monitor_settings.deg2pix(
    session_info.fixation_trigger_allowance_deg
    )

class EyeTrackingSerialSearchExperiment(EyeTrackingVisualSearchExperiment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def trial(self, object_df, n_obj, is_present):

        tracker = self.tracker
        win = tracker.win
        el_tracker = tracker.el_tracker

        # drift check
        nth_trial = self.current_trial_index
        every_nth_trial = params.drift_correction_params['every_nth_trial']

        if not (nth_trial % every_nth_trial):
            order = (nth_trial/every_nth_trial)%len(params.drift_correction_params['positions'])
            coords = params.drift_correction_params['positions'][int(order)]
            tracker.drift_correction(coords)

            core.wait(params.drift_correction_params['wait_after_correction_sec'])

        recording_ok = tracker.start_recording(self.current_trial_index)

        # if failed to record
        if not recording_ok:
            return "redo_now"

        # wait for fixation
        exp_stimuli.display_tone(win)
        gaze_trigger_ok = Gaze_trigger_v3(
            tracker, target_pos_psychopy_coor=(0, 0), 
            fixation_cross_params=fixation_params
        ).waitTrigger()

        # if failed to fixate, recalibration needed, or tracker disconnected
        if not gaze_trigger_ok:
            exp_stimuli.incorrect_tone(win)
            el_tracker.sendMessage("gaze_trigger_timeout")
            return "redo_now"
        el_tracker.sendMessage("gaze_trigger_ok")

        # stimuli presented
        exp_stimuli.draw_from_df(
            win,
            exp_stimuli.draw_object,
            object_df,
            dict(colourRGB=params.bar_colourRGB),
        )
        win.flip()
        el_tracker.sendMessage("stim_onset")

        # wait for reseponse
        waitResponse = event.waitKeys(
            maxWait=params.maxWait,
            keyList=params.accepted_keys,
            timeStamped=core.Clock(),
        )
        win.flip()
        el_tracker.sendMessage("blank_screen")

        # check if recording has been aborted by the host pc
        if not tracker.is_recording():
            el_tracker.sendMessage("aborted_by_host")
            return "redo_later"

        # record responses (local)
        data = dict(is_present=is_present, n_obj=n_obj)
        if waitResponse is None:
            response = None, params.maxWait
        else:
            response = waitResponse[0]



        if ((response[0] == 'p') and is_present):
            exp_stimuli.correct_tone(win)
        elif ((response[0] == 'q') and (not is_present)):
            exp_stimuli.correct_tone(win)
        else:
            exp_stimuli.incorrect_tone(win)


        data["keyPressed"], data["timeTaken"] = response

        self.visual_search_subject.current_session.record_trial_data(object_df, **data)

        # record trial variables to the EDF data file, for details, see Data
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        tracker.record_variables_end_of_trial(
            key_pressed=response[0], response_time_msec=response[1] * 1000
        )

        # inter-trial intervals
        core.wait(params.inter_trial_interval)

        # stop recording
        tracker.stop_recording()
        return "completed"

num_repeat = params.number_of_repeat if (session_info.overwrite_n_repeat is None) else session_info.overwrite_n_repeat

def trial_params():

    # trial conditions: size * proportion * is_present
    trial_conditions = (
        list(
            itertools.product(
                params.num_row_column, params.distractor_proportions, [True, False]
            )
        )
        * num_repeat
    )

    # create object df
    random.shuffle(trial_conditions)

    trial_data = []
    for i_num_rc, i_dist_occ, i_is_present in trial_conditions:

        df = exp_stimuli.get_search_array_df_with_noise(
            n_rows=i_num_rc[0],
            n_columns=i_num_rc[1],
            obj_distance=params.obj_spacing,
            is_target_present=i_is_present,
            target_param=params.target_param,
            distractor_params=params.distractor_params,
            distractor_proportion=i_dist_occ,
            noise_level = params.noise_level
        )

        trial_data.append(
            dict(object_df=df, n_obj=i_num_rc[0] * i_num_rc[1], is_present=i_is_present)
        )

    return trial_conditions, trial_data


exp = EyeTrackingSerialSearchExperiment(
    subjectID  =  session_info.subjectID, 
    sessionID  =  session_info.sessionID, 
    datapath   =  "./data", 
    dummy_mode =  session_info.dummy_mode,
    comment    =  session_info.comment + f"\nfixation_trigger_allowance_deg: {session_info.fixation_trigger_allowance_deg}"
)
event.globalKeys.add(key="g", modifiers=["ctrl"], func=exp.terminate, name="shutdown")
exp.set_trial_sequence(*trial_params())


exp_stimuli.intro(exp.win)
exp.tracker.calibrate()
exp.run()
exp_stimuli.thanks(exp.win)
exp.win.close()