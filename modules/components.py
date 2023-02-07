import pylink
import os
import random
import time
import sys
from psychopy import visual, core, event, monitors, gui
#from . import params
import numpy as np
#from .eye_tracking.dummy_eye_movement import DummyEyeMovementCursor

class Gaze_trigger_v3:
    def __init__(self, tracker_window, target_pos_psychopy_coor, fixation_cross_params):
        self.tracker_window = tracker_window
        self.win = tracker_window.win
        self.el_tracker = tracker_window.el_tracker

        # to psychopy, (0,0) is the center of the screen
        self.target_pos_psychopy_coor = target_pos_psychopy_coor

        # to eyelink, (0,0) is the top-left corner
        scn_width, scn_height = self.win.size
        self.target_pos_eyeLink_coor = target_pos_psychopy_coor[0]+scn_width/2, -target_pos_psychopy_coor[1]+scn_height/2
        #print ( self.target_pos_eyeLink_coor)
        self.existing_sample = None

        self.__apply_parameters(fixation_cross_params)

    def __apply_parameters(self, fixation_cross_params):
        self.fixation_trigger_allowance_pix = fixation_cross_params['trigger_allowance_pix']
        self.fixation_cross_width = fixation_cross_params['width']
        self.fixation_cross_height = fixation_cross_params['height']
        self.fixation_cross_in_region_color = fixation_cross_params['in_region_color']
        self.fixation_cross_out_region_color = fixation_cross_params['out_region_color']

        self.fixation_duration_sec = fixation_cross_params['duration_sec']
        self.fixation_timeout_sec = fixation_cross_params['timeout_sec']


    def fixation_trigger_allowance_pix(self):
        fixation_trigger_allowance_pix 
    def __get_eye_used(self):
        # determine which eye(s) is/are available
        # 0- left, 1-right, 2-binocular
        eye_used = self.el_tracker.eyeAvailable()

        if eye_used == 1:
            pass # self.el_tracker.sendMessage("EYE_USED 1 RIGHT")
        elif eye_used == 0 or eye_used == 2:
            pass # self.el_tracker.sendMessage("EYE_USED 0 LEFT")
            eye_used = 0
        else:
            print("Error in getting the eye information!")
            # TODO: 
            return pylink.TRIAL_ERROR

        return eye_used
    
    def waitTrigger(self):
        """
        return True if success
        return False if timeout or has an error
        """
        if self.tracker_window.dummy_mode:
            core.wait(self.fixation_duration_sec)
            return True
        fixation_duration_sec = self.fixation_duration_sec
        timeout_sec = self.fixation_timeout_sec 
        eye_used = self.__get_eye_used()
        startTime = core.getTime()

        was_in_region = False
        in_region_startTime = None


        assert self.tracker_window.is_recording(), "Cannot do gaze trigger before the recording starts"
        self.__fixation_target_drawer(False)
        self.win.flip()
        eye_in_region = None

        while True:
            if core.getTime() - startTime > timeout_sec:
                return False


            sample_eye0 = self.__get_new_sample(0)
            sample_eye1 = self.__get_new_sample(1)

            if (sample_eye1 is None) and (sample_eye0 is None):
                continue


            if not (sample_eye0 is None): 
                if eye_in_region == 0:
                    continue

                eye0_is_in_region = self.__isGazedInRegion(sample_eye0)
                eye_in_region = 0
            else: 
                eye0_is_in_region = False
                eye_in_region = None if eye_in_region == 0 else eye_in_region


            if not (sample_eye1 is None): 
                if eye_in_region == 1:
                    continue

                eye1_is_in_region = self.__isGazedInRegion(sample_eye1)
                eye_in_region = 1
            else: 
                eye1_is_in_region = False
                eye_in_region = None if eye_in_region == 1 else eye_in_region


            # if in region: start timer
            if eye0_is_in_region or eye1_is_in_region:
                if not was_in_region: 
                    was_in_region = True
                    self.__fixation_target_drawer(True)
                    self.win.flip()
                    in_region_startTime = core.getTime()
                
                if core.getTime() - in_region_startTime > fixation_duration_sec:
                    self.win.flip()
                    return True

            # if not in region: reset timer
            else: 
                if was_in_region:
                    was_in_region = False
                    self.__fixation_target_drawer(False)
                    self.win.flip()
                    in_region_startTime = None # not neccessary
                else: 
                    pass

        # won't get here
        raise RuntimeError

    def __isGazedInRegion(self, gazePos):
        # break the while loop if the current gaze position is
        # in a 120 x 120 pixels region around the screen centered
        target_x, target_y = self.target_pos_eyeLink_coor
        gaze_x, gaze_y = gazePos
        allowance = self.fixation_trigger_allowance_pix
        
        return (abs(gaze_x - target_x) < allowance and abs(gaze_y - target_y) < allowance)


    def __get_new_sample(self, eye_used):
        """
        return the new (x,y) position of the gaze of the eye used 
        return None if no new data is avaiable
        
        """
        
        existing_sample = self.existing_sample

        # get sample 
        el_tracker = self.el_tracker
        new_sample = el_tracker.getNewestSample()
        if new_sample is None: 
            return None 

        elif (existing_sample is None) or (new_sample.getTime() != existing_sample.getTime()): 


            # check if the data for the eye used is avaible
            if eye_used == 1 and new_sample.isRightSample():
                self.existing_sample = new_sample

                # g_x, g_y 
                return new_sample.getRightEye().getGaze()

            if eye_used == 0 and new_sample.isLeftSample():
                self.existing_sample = new_sample

                # g_x, g_y
                return new_sample.getLeftEye().getGaze()

            else: 

                # not saving the sample 
                return None

            return None

        else:
            return None       

    def __fixation_target_drawer(self, is_in_region):

        fillColor = self.fixation_cross_in_region_color if is_in_region else self.fixation_cross_out_region_color 
        #print(fillColor)

        bar = visual.Rect(
            win=self.win,
            width=self.fixation_cross_width,
            height=self.fixation_cross_height,
            lineWidth=0,
            #fillColor=fillColor,
            fillColor=fillColor,
            fillColorSpace='rgb', 
            pos=self.target_pos_psychopy_coor,
            ori=90
            )
        bar.draw()
        bar.setOri(0)
        bar.draw()


class Gaze_trigger_v3:
    def __init__(self, tracker_window, target_pos_psychopy_coor, fixation_cross_params):
        self.tracker_window = tracker_window
        self.win = tracker_window.win
        self.el_tracker = tracker_window.el_tracker

        # to psychopy, (0,0) is the center of the screen
        self.target_pos_psychopy_coor = target_pos_psychopy_coor

        # to eyelink, (0,0) is the top-left corner
        scn_width, scn_height = self.win.size
        self.target_pos_eyeLink_coor = target_pos_psychopy_coor[0]+scn_width/2, -target_pos_psychopy_coor[1]+scn_height/2
        #print ( self.target_pos_eyeLink_coor)
        self.existing_sample = None

        self.__apply_parameters(fixation_cross_params)

    def __apply_parameters(self, fixation_cross_params):
        self.fixation_trigger_allowance_pix = fixation_cross_params['trigger_allowance_pix']
        self.fixation_cross_width = fixation_cross_params['width']
        self.fixation_cross_height = fixation_cross_params['height']
        self.fixation_cross_in_region_color = fixation_cross_params['in_region_color']
        self.fixation_cross_out_region_color = fixation_cross_params['out_region_color']

        self.fixation_duration_sec = fixation_cross_params['duration_sec']
        self.fixation_timeout_sec = fixation_cross_params['timeout_sec']


    def fixation_trigger_allowance_pix(self):
        fixation_trigger_allowance_pix 
    def __get_eye_used(self):
        # determine which eye(s) is/are available
        # 0- left, 1-right, 2-binocular
        eye_used = self.el_tracker.eyeAvailable()

        if eye_used == 1:
            pass # self.el_tracker.sendMessage("EYE_USED 1 RIGHT")
        elif eye_used == 0 or eye_used == 2:
            pass # self.el_tracker.sendMessage("EYE_USED 0 LEFT")
            eye_used = 0
        else:
            print("Error in getting the eye information!")
            # TODO: 
            return pylink.TRIAL_ERROR

        return eye_used
    
    def waitTrigger(self):
        """
        return True if success
        return False if timeout or has an error
        """
        if self.tracker_window.dummy_mode:
            core.wait(self.fixation_duration_sec)
            return True
        fixation_duration_sec = self.fixation_duration_sec
        timeout_sec = self.fixation_timeout_sec 
        eye_used = self.__get_eye_used()
        startTime = core.getTime()

        was_in_region = False
        in_region_startTime = None


        assert self.tracker_window.is_recording(), "Cannot do gaze trigger before the recording starts"
        self.__fixation_target_drawer(False)
        self.win.flip()
        eye_in_region = None

        while True:
            if core.getTime() - startTime > timeout_sec:
                return False


            sample_eye0 = self.__get_new_sample(0)
            sample_eye1 = self.__get_new_sample(1)

            if (sample_eye1 is None) and (sample_eye0 is None):
                continue


            if not (sample_eye0 is None): 
                if eye_in_region == 0:
                    continue

                eye0_is_in_region = self.__isGazedInRegion(sample_eye0)
                eye_in_region = 0
            else: 
                eye0_is_in_region = False
                eye_in_region = None if eye_in_region == 0 else eye_in_region


            if not (sample_eye1 is None): 
                if eye_in_region == 1:
                    continue

                eye1_is_in_region = self.__isGazedInRegion(sample_eye1)
                eye_in_region = 1
            else: 
                eye1_is_in_region = False
                eye_in_region = None if eye_in_region == 1 else eye_in_region


            # if in region: start timer
            if eye0_is_in_region or eye1_is_in_region:
                if not was_in_region: 
                    was_in_region = True
                    self.__fixation_target_drawer(True)
                    self.win.flip()
                    in_region_startTime = core.getTime()
                
                if core.getTime() - in_region_startTime > fixation_duration_sec:
                    self.win.flip()
                    return True

            # if not in region: reset timer
            else: 
                if was_in_region:
                    was_in_region = False
                    self.__fixation_target_drawer(False)
                    self.win.flip()
                    in_region_startTime = None # not neccessary
                else: 
                    pass

        # won't get here
        raise RuntimeError

        
    def waitTrigger_binocular_optional(self):
        """
        return True if success
        return False if timeout or has an error
        """
        if self.tracker_window.dummy_mode:
            core.wait(self.fixation_duration_sec)
            return True
        fixation_duration_sec = self.fixation_duration_sec
        timeout_sec = self.fixation_timeout_sec 
        eye_used = self.__get_eye_used()
        startTime = core.getTime()

        was_in_region = False
        in_region_startTime = None


        assert self.tracker_window.is_recording(), "Cannot do gaze trigger before the recording starts"
        self.__fixation_target_drawer(False)
        self.win.flip()
        eye0_in_region = False
        eye1_in_region = False

        while True:
            if core.getTime() - startTime > timeout_sec:
                return False


            sample_eye0 = self.__get_new_sample(0)
            sample_eye1 = self.__get_new_sample(1)
            if not(sample_eye0 is None):
                eye0_in_region =  self.__isGazedInRegion(sample_eye0)
            # else: same as before

            if not(sample_eye1 is None):
                eye1_in_region =  self.__isGazedInRegion(sample_eye1)
            # else: same as before


            # if in region: start timer
            if eye0_in_region and eye1_in_region:
                # else: nothing to do
                if not was_in_region: 
                    was_in_region = True
                    self.__fixation_target_drawer(True)
                    self.win.flip()
                    in_region_startTime = core.getTime()
                
                if core.getTime() - in_region_startTime > fixation_duration_sec:
                    self.win.flip()
                    return True
            # if not in region: reset timer
            else: 
                if was_in_region:
                    was_in_region = False
                    self.__fixation_target_drawer(False)
                    self.win.flip()
                    in_region_startTime = None # not neccessary
                else: 
                    pass

        # won't get here
        raise RuntimeError


    def __isGazedInRegion(self, gazePos):
        # break the while loop if the current gaze position is
        # in a 120 x 120 pixels region around the screen centered
        target_x, target_y = self.target_pos_eyeLink_coor
        gaze_x, gaze_y = gazePos
        allowance = self.fixation_trigger_allowance_pix
        
        return (abs(gaze_x - target_x) < allowance and abs(gaze_y - target_y) < allowance)


    def __get_new_sample(self, eye_used):
        """
        return the new (x,y) position of the gaze of the eye used 
        return None if no new data is avaiable
        
        """
        
        existing_sample = self.existing_sample

        # get sample 
        el_tracker = self.el_tracker
        new_sample = el_tracker.getNewestSample()
        if new_sample is None: 
            return None 

        elif (existing_sample is None) or (new_sample.getTime() != existing_sample.getTime()): 


            # check if the data for the eye used is avaible
            if eye_used == 1 and new_sample.isRightSample():
                self.existing_sample = new_sample

                # g_x, g_y 
                return new_sample.getRightEye().getGaze()

            if eye_used == 0 and new_sample.isLeftSample():
                self.existing_sample = new_sample

                # g_x, g_y
                return new_sample.getLeftEye().getGaze()

            else: 

                # not saving the sample 
                return None

            return None

        else:
            return None       

    def __fixation_target_drawer(self, is_in_region):

        fillColor = self.fixation_cross_in_region_color if is_in_region else self.fixation_cross_out_region_color 
        #print(fillColor)

        bar = visual.Rect(
            win=self.win,
            width=self.fixation_cross_width,
            height=self.fixation_cross_height,
            lineWidth=0,
            #fillColor=fillColor,
            fillColor=fillColor,
            fillColorSpace='rgb', 
            pos=self.target_pos_psychopy_coor,
            ori=90
            )
        bar.draw()
        bar.setOri(0)
        bar.draw()




