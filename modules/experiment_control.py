from .monitor_settings import get_psychopy_window
from .eye_tracking.tracker_setup import PsychopyEyeLinkSet
from .visual_search import recorder

import os, json

class EyeTrackingVisualSearchExperiment:
    def __init__(self, subjectID, sessionID, datapath, dummy_mode):

        # io 
        # TODO: assumed 
        self.visual_search_subject = recorder.Subject(os.path.join(datapath, subjectID))
        self.visual_search_subject.new_session(sessionID)

        # tracker/display apparatus setup
        self.win = get_psychopy_window()
        self.dummy_mode = dummy_mode
        self.tracker = PsychopyEyeLinkSet(
            psychopy_window = self.win, 
            edf_fname = self.visual_search_subject.current_session.sid, 
            output_folder = self.visual_search_subject.current_session.path, 
            dummy_mode=dummy_mode, 
            host_ip="100.1.1.1"
        )
        self.current_trial_index = 0
        self.__trial_sequence = None
        self.__trial_pool = []
        self.__completed_trial = []
        self.__all_trial_history = []

    def lastTrial(self):
        self.__trial_pool = []        

    def trial(self, **kwargs):
        """
        responsible for intertrial intervals, data io, stimuli control and tracker control


        return the status of trial
        
        can be:
            completed
            redo_later
            redo_now
            terminate
        """
        print('hi')

        return 'completed'
        

    def set_trial_sequence(self, kwargs_list):
        """
        provide a list of dict 
        """
        assert self.__trial_sequence is None, "self.__trial_sequence is already set"
        self.__trial_sequence = kwargs_list
        self.__trial_pool = kwargs_list

    def __termination_handle(self):
        """
        1. transfer EDF file
        2. save self.__trial_sequence, self.__trial_pool, self.__all_trial_history, self.__completed_trial
        """
        # 1. transfer EDF file
        self.tracker.terminate_task()

        trial_history = dict(
            trial_sequence = self.__trial_sequence, 
            trial_pool = self.__trial_pool, 
            all_trial_history = self.__all_trial_history, 
            completed_trial = self.__completed_trial, 
        )
        trial_info_output_path = os.path.join(self.visual_search_subject.current_session.path, 'trial_info.json')

        json.dump(trial_history, open(trial_info_output_path, 'w'))


    def run_next_trial(self):
        """
        run and decide what trial comes next
        """
        assert len(self.__trial_pool), "no more trials"

        # the current trial number for tracker 
        self.current_trial_index = len(self.__all_trial_history)

        # get trial condition, remove it from the trial pool
        trial_kwargs = self.__trial_pool.pop(0)
        
        # record the trial
        self.__all_trial_history.append(trial_kwargs)

        # start the trial
        status = self.trial(**trial_kwargs)

        # check the status of the trial
        if status == 'completed':
            self.__completed_trial.append(trial_kwargs)

        elif status == 'redo_later':
            # append to the end of trial pool
            self.__trial_pool = self.__trial_pool + [trial_kwargs]
            self.tracker.calibrate()

        elif status == 'redo_now':
            # append to the start of trial pool
            self.__trial_pool = [trial_kwargs] + self.__trial_pool
            self.tracker.calibrate()

        else:
            # terminate
            self.__trial_pool = []

        # is are there more trials? 
        if len(self.__trial_pool) == 0:
            return False
        else: 
            return True

    def run(self):
        while self.run_next_trial():
            print('number of trials:', self.current_trial_index)
        self.__termination_handle()
