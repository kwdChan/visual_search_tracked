import os
import pandas as pd
import numpy as np
from datetime import datetime
from psychopy import visual, core, event, monitors, gui

import json

def new_subject(datapath, subjectID, subjectInfo):

    # put subjectID into subjectInfo
    assert type(subjectInfo) is dict
    assert not ("id" in subjectInfo), "cannot have properties named id"
    subjectInfo['id'] = subjectID

    # create directory for participant, raise an Error if the directory always exists
    subject_path = os.path.join(datapath, subjectID)
    os.mkdir(subject_path)

    # save the subject info
    output_path = os.path.join(subject_path, "subject_info.json")
    json.dump(subjectInfo, open(output_path, "w"))

class Subject:
    """
    the same subject is assumed to be accessed by one instance only.
    
    subject's of folder and subject_info.json is to be created manually


    """
    def __init__(self, path):

        # check if the folder exist
        self.path = os.path.normpath(path)
        assert os.path.exists(self.path), "Subject folder does not exist"


        # check if subject_info.json exists (to verify that its a subject's folder)
        self.files = os.listdir(self.path)
        assert "subject_info.json" in self.files, "subject_info.json does not exist"

        """
        # session metadata
        self.session_meta_path = os.path.join(self.path, 'sessions_meta.json')
        if not os.path.exists(self.session_meta_path):
            self.session_meta = []
        else:
            self.session_meta = json.load(open(self.session_meta_path))

        self.current_session = None
        """
        self.current_session = None
        
    def new_session(self, sid):
        self.current_session = Session(sid, self.path)

class Session:
    def __init__(self, sid, parent, metadata={}):
        self.sid = sid

        # make sure the session does not exist and create a folder for the session
        self.path  = os.path.join(os.path.normpath(parent), sid)
        assert not os.path.exists(self.path),  "the session id already exists"
        os.mkdir(self.path)

        # meta
        self.metadata_path = os.path.join(self.path, 'metadata.json')
        assert not 'datetime' in metadata, "cannot have properties named datetime"
        metadata['datetime'] = str(datetime.now())
        self.metadata = metadata
        json.dump(self.metadata, open(self.metadata_path, 'w'))

        # json for trial data
        self.trial_data = []
        self.trial_data_path = os.path.join(self.path, 'trial_data.json')

        # a folder with stimulus related data for each trial
        self.stimulus_data_path = os.path.join(self.path, 'stimulus')
        os.mkdir(self.stimulus_data_path)

    def record_trial_data(self, object_df, **data):
  
        trial_id = len(self.trial_data)

        # response data 
        assert not '_trial_id' in data, 'the key is reserved'
        assert not '_datetime' in data, 'the key is reserved'

        data['_trial_id'] = trial_id
        data['_datetime'] =  str(datetime.now())
        self.trial_data.append(data)
        json.dump(self.trial_data, open(self.trial_data_path, 'w'))

        # object_df 
        path = os.path.join(self.stimulus_data_path, str(trial_id))
        assert not os.path.exists(path), 'already exists. not overwritting'
        object_df.to_csv(path)
