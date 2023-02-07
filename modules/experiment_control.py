from .monitor_settings import get_psychopy_window
from .eye_tracking.tracker_setup import PsychopyEyeLinkSet
from .visual_search import recorder

import os, json

class EyeTrackingVisualSearchExperiment:
    def __init__(self, subjectID, sessionID, datapath, dummy_mode, comment):
        """
        
        
        
        
        """
        # io 
        # TODO: assumed 
        self.visual_search_subject = recorder.Subject(os.path.join(datapath, subjectID))
        self.visual_search_subject.new_session(sessionID, comment=comment)

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
        """
        provide a list of dict 
        the dict is the keyword arguments for self.trial
        
        self.__trial_label_sequence : the pre-planned sequence of trials
        self.__trial_data_sequence : the data for the pre-planned sequence of trials

        self.__trial_pool : the index of self.__trial_sequence_label of the upcomming trials
        self.__completed_trial : the index of self.__trial_sequence_label of the successfully completed trials
        self.__all_trial_history : the index of self.__trial_sequence_label of the started (completed or not) trials

        """
        
        self.current_trial_index = 0
        self.__trial_label_sequence = None
        self.__trial_data_sequence = None
        self.__trial_pool = []
        self.__completed_trial = []
        self.__all_trial_history = []

    def lastTrial(self):
        "allow the experiment to be terminated externally"
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
        

    def set_trial_sequence(self, trial_label_sequence, trial_data_sequence):
        """
        trial_label_sequence is a list of turple of the labels for each trial. it does not affect the trial condition. 
        trial_data_sequence is a list of dict that contains the keyword arguments passed to self.trial for each trial. 

        trial_label_sequence is saved by the trial schedualler in .JSON but trial_data_sequence is not. 
        data in trial_data_sequence can be saved manually within the trial
        """

        assert self.__trial_label_sequence is None, "self.__trial_label_sequence is already set"
        self.__trial_label_sequence = trial_label_sequence
        self.__trial_data_sequence = trial_data_sequence
        self.__trial_pool = list(range(len(trial_label_sequence)))


        # save to ensure __trial_label_sequence is possible to be saved as JSON
        trial_info_output_path = os.path.join(self.visual_search_subject.current_session.path, 'planned_trial_labels.json')
        json.dump(self.__trial_label_sequence, open(trial_info_output_path, 'w'))



    def terminate(self):
        self.__termination_handle()

    def __termination_handle(self):
        """
        1. transfer EDF file
        2. save self.__trial_label_sequence, self.__trial_pool, self.__all_trial_history, self.__completed_trial
        """
        # 1. transfer EDF file
        
        trial_history = dict(
            trial_sequence = self.__trial_label_sequence, 
            trial_pool = self.__trial_pool, # this function won't be called unless __trial_pool is empty...
            all_trial_history = self.__all_trial_history, 
            completed_trial = self.__completed_trial, 
        )
        trial_info_output_path = os.path.join(self.visual_search_subject.current_session.path, 'trial_info.json')

        json.dump(trial_history, open(trial_info_output_path, 'w'))

        self.tracker.terminate_task()
        self.win.close()



    def run_next_trial(self):
        """
        run and decide what trial comes next
        """
        assert len(self.__trial_pool), "no more trials"

        # the current trial number for tracker 
        self.current_trial_index = len(self.__all_trial_history)

        # get trial condition, remove it from the trial pool
        trial_arg_idx = self.__trial_pool.pop(0)
        trial_kwargs = self.__trial_data_sequence[trial_arg_idx]
        
        # record the start of the trial
        self.__all_trial_history.append(trial_arg_idx)

        # start the trial
        status = self.trial(**trial_kwargs)

        # check the status of the trial
        if status == 'completed':
            self.__completed_trial.append(trial_arg_idx)

        elif status == 'redo_later':
            # append to the end of trial pool
            self.__trial_pool = self.__trial_pool + [trial_arg_idx]
            self.tracker.calibrate()

        elif status == 'redo_now':
            # append to the start of trial pool
            self.__trial_pool = [trial_arg_idx] + self.__trial_pool
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
