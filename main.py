import itertools
import os
import random

from psychopy import core, event, gui, monitors, visual

from modules import monitor_settings, params
from modules.components import Gaze_trigger_v2
from modules.experiment_control import EyeTrackingVisualSearchExperiment
from modules.eye_tracking import tracker_setup
from modules.visual_search import exp_stimuli
import session_info


os.chdir(os.path.dirname(__file__))


class EyeTrackingSerialSearchExperiment(EyeTrackingVisualSearchExperiment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def trial(self, object_df, n_obj, is_present):

        tracker = self.tracker
        win = tracker.win
        el_tracker = tracker.el_tracker

        # inter-trial intervals
        core.wait(params.inter_trial_interval)

        # start recording
        recording_ok = tracker.start_recording(self.current_trial_index)

        # if failed to record
        if not recording_ok:
            return "redo_now"

        # wait for fixation
        gaze_trigger_ok = Gaze_trigger_v2(
            tracker, target_pos_psychopy_coor=(0, 0)
        ).waitTrigger()

        # if failed to fixate, recalibration needed, or tracker disconnected
        if not gaze_trigger_ok:
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

        # stop recording
        tracker.stop_recording()

        # record responses (local)
        data = dict(is_present=is_present, n_obj=n_obj)
        if waitResponse is None:
            response = None, params.maxWait
        else:
            response = waitResponse[0]

        data["keyPressed"], data["timeTaken"] = response

        self.visual_search_subject.current_session.record_trial_data(object_df, **data)

        # record trial variables to the EDF data file, for details, see Data
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        tracker.record_variables_end_of_trial(
            key_pressed=response[0], response_time_msec=response[1] * 1000
        )
        return "completed"


def trial_params():

    # trial conditions: size * proportion * is_present
    trial_conditions = (
        list(
            itertools.product(
                params.num_row_column, params.distractor_proportions, [True, False]
            )
        )
        * params.number_of_repeat
    )

    # create object df
    random.shuffle(trial_conditions)

    trial_data = []
    for i_num_rc, i_dist_occ, i_is_present in trial_conditions:

        df = exp_stimuli.get_search_array_df(
            n_rows=i_num_rc,
            n_columns=i_num_rc,
            obj_distance=params.obj_spacing,
            is_target_present=i_is_present,
            target_param=params.target_param,
            distractor_params=params.distractor_params,
            distractor_proportion=i_dist_occ,
        )

        trial_data.append(
            dict(object_df=df, n_obj=i_num_rc * i_num_rc, is_present=i_is_present)
        )

    return trial_conditions, trial_data


exp = EyeTrackingSerialSearchExperiment(
    subjectID  =  session_info.subjectID, 
    sessionID  =  session_info.sessionID, 
    datapath   =  "./data", 
    dummy_mode =  session_info.dummy_mode,
    comment    =  session_info.comment
)
event.globalKeys.add(key="c", modifiers=["ctrl"], func=exp.lastTrial, name="shutdown")
exp.set_trial_sequence(*trial_params())



exp_stimuli.intro(exp.win)
exp.tracker.calibrate()
exp.run()
exp_stimuli.thanks(exp.win)