from __future__ import division
from __future__ import print_function

import pylink, os, random, time, sys
from psychopy import visual, core, event, monitors, gui
from modules.tracker_setup import PsychopyEyeLinkSet, check_EDF_filename
from modules.components import run_trial, gaze_trigger
from modules import recorder, my_param, exp_stimuli, monitor_settings


# Switch to the script folder
os.chdir(os.path.dirname(__file__))

#script_path = os.path.dirname(sys.argv[0])
#if len(script_path) != 0:
#    os.chdir(script_path)

def ask_input_loop(dataFolder):
    subjectID = 'TEST'
    sessionID = 'TEST'
    
    while True:
        subjectID, sessionID = recorder.ask_input(subjectID, sessionID)
        
        try: 
            subject = recorder.Subject(os.path.join(dataFolder, subjectID))
        except AssertionError:
            recorder.gui_message(f'Subject not found. Entered subjectID = {subjectID}')
            continue
        
        try: 
            subject.new_session(sessionID)
            break
        except AssertionError:
            recorder.gui_message(f'SessionID already exists. Entered sessionID = {sessionID}')
            continue
        
        if not check_EDF_filename(sessionID):
            recorder.gui_message(f'Invalide sessionID = {sessionID}')
            continue
        else: 
            break

    return subject


class EyeTrackingExperiment:
    def __init__(self, tracker_setup, subject):
        self.tracker_setup = tracker_setup
        self.subject = subject
        self.next_trial_index = 0

    def trial(self, n_obj, is_present):
        """
        TODO: what if the trial is aborted?
        """
        tracker_setup = self.tracker_setup
        trial_index = self.next_trial_index
        self.next_trial_index = self.next_trial_index + 1

        
        win = tracker_setup.win
        el_tracker = tracker_setup.el_tracker

        core.wait(my_param.inter_trial_interval)

        
        # start recording
        tracker_setup.start_recording(trial_index)
        print('start_recording')

        # fixation 
        gaze_trigger_status = gaze_trigger(tracker_setup, minimum_duration=0.3, time_limit=10)

        Gaze_trigger_v2()
        if not gaze_trigger_status == True: 
            return gaze_trigger_status


        exp_stimuli.draw_fixation_cross(win)
        win.flip()
        el_tracker.sendMessage('fix_onset')
        core.wait(my_param.fixation_duration)

        # stimuli
        obj_param_df = exp_stimuli.draw_search_array_popout(win, n_obj, is_present)
        win.flip()
        el_tracker.sendMessage('stim_onset')

        # wait for reseponse 
        waitResponse = event.waitKeys(maxWait=my_param.maxWait, keyList=my_param.accepted_keys, timeStamped=core.Clock())
        win.flip()
        el_tracker.sendMessage('blank_screen')

        # stop recording
        tracker_setup.stop_recording()

        # record responses (local)
        data = dict(is_present=is_present, n_obj=n_obj)
        if waitResponse is None:
            response = None, my_param.maxWait
        else: 
            response = waitResponse[0]

        data['keyPressed'], data['timeTaken'] = response

        self.subject.current_session.record_trial_data(obj_param_df, **data)

        # record trial variables to the EDF data file, for details, see Data 
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        tracker_setup.record_variables_end_of_trial(
            key_pressed = response[0], 
            response_time_msec = response[1]*1000
        )

    def run(self, trial_parameters):
        """
        
        """

        self.tracker_setup.calibrate()
        win = self.tracker_setup.win

        exp_stimuli.intro(win)
        count = 0
        total_trial_number = len(trial_parameters)
        for idx, (n_object, is_present) in enumerate(trial_parameters):
            self.trial(n_object, is_present)

            print("%s of %s trials"%(idx+1, total_trial_number))

            count += 1
            if (count == my_param.rest_interval) and (idx!=total_trial_number-1):
                count = 0
                exp_stimuli.rest(win, idx+1, total_trial_number)

        self.tracker_setup.terminate_task()
        exp_stimuli.thanks(win)


def trial_params():
    _set_sizes = my_param.set_sizes + my_param.set_sizes
    _is_present = [True]*len(my_param.set_sizes ) + [False]*len(my_param.set_sizes)

    trial_parameters = list(zip(_set_sizes, _is_present))*my_param.n_repeats_per_session
    random.shuffle(trial_parameters)
    return trial_parameters


# main
subject = ask_input_loop('./data')
win = monitor_settings.get_psychopy_window()
tracker_setup = PsychopyEyeLinkSet(win, subject.current_session.sid, output_folder=subject.current_session.path, dummy_mode=True)
exp = EyeTrackingExperiment(tracker_setup, subject)
exp.run(trial_params())

