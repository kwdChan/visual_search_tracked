from __future__ import absolute_import, division
import psychopy
from psychopy import core, gui, visual, event, monitors
import numpy as np
import pandas as pd
from . import my_param
def scale(arr, minimum, maximum):
    """
    scale the number from [0, 1] to [minimum, maximum]
    """
    return arr*(maximum-minimum)+minimum

def horizontal_hexagon_array(n_cols, n_rows, obj_distance):
    """
    gives the locations of objects for the search array
    """
    # (2, n_cols, n_rows)
    # 0 -> columns coor
    # 1 -> rows coor
    grid = np.mgrid[0:n_cols, 0:n_rows].astype(np.float64)

    # shift to centre
    grid[0] = grid[0]-(n_cols-1)/2
    grid[1] = grid[1]-(n_rows-1)/2

    # vertical distance scaling
    grid[1, :, :] = grid[1, :, :]*np.sin(np.pi*60/180)

    # horizontal shift (for every other row)
    grid[0, :, ::2] = grid[0, :, ::2] + np.cos(np.pi*60/180)
    
    # scaling 
    grid = grid*obj_distance

    # flatten grid
    #grid.reshape((2, -1)).transpose()
    # return (n, 2)
    return grid.reshape((2, -1)).transpose()

class Visual_search_stimulus_condition:
    def __init__(self, win, n_columns, n_rows, obj_distance, target_params, distractor_params, distractor_occurances):
        """
        target_params:dict
        distractor_params: list[dict]
        distractor_occurances: list with the same length as distractor_params 

        this object define the stimulus condition and is able to generate different trials with this condition
        """
        self.win = win
        self.n_columns = n_columns
        self.n_rows = n_rows    
        self.obj_distance = obj_distance    

        # target parameters
        self.target_params = target_params

        # a list of distractor parameters
        self.distractor_params = distractor_params

        # occurance of each distractor parameters set
        self.distractor_occurances = np.array(distractor_occurances)
        self.distractor_occurances = self.distractor_occurances/self.distractor_occurances.sum()
        
        # (x, y) position of each object in (n_obj, 2) 
        self.object_pos = horizontal_hexagon_array(n_columns, n_rows, obj_distance)

        # all global setting should be grouped together
        self.__global_setting()

    def __global_setting(self):
        self.bar_width = my_param.bar_width
        self.bar_height = my_param.bar_height
        self.colourRGB_byName = my_param.colourRGB

    def draw_object(self, x, y, colour, ori, contrast):
        """
        the search object is defined here, exactly

        Not randomisation is to be done here
        """
        visual.Rect(
            win=self.win,
            fillColor=self.colourRGB_byName[colour],
            ori=ori,
            width=self.bar_width,
            height=self.bar_height,
            pos=(x, y),
            lineWidth=0,
            contrast=contrast,
            #opacity=contrast,
            fillColorSpace='rgb255'
        ).draw()

    def get_search_array_df(self, is_target_present):
        """
        randomisation can be done here for trial-to-trial variation 

        output the stimulus parameters produce the exact same stimulus
        """

        n_obj = len(self.object_pos)


        # distractor occurance
        n_distractor = n_obj - int(is_target_present)
        n_repeat_each_distractor_param = np.floor(self.distractor_occurances*n_distractor).astype(int)
        n_leftover = n_distractor - n_repeat_each_distractor_param.sum()
        
        print(n_leftover)
        # TODO: to have the leftover randomly assigned according to occurance
        for i in range(int(n_leftover)):
            n_repeat_each_distractor_param[i] += 1

        # distractor object list
        param_list =[]
        for each_distractor_param, each_occurance in zip(self.distractor_params,  n_repeat_each_distractor_param):
            param_list += [each_distractor_param]*each_occurance
        # target
        param_list += [self.target_params]*int(is_target_present)
        np.random.shuffle(param_list)


        # object dataframe 
        object_parameters = pd.DataFrame(self.object_pos, columns=['x', 'y'])
        object_parameters = (object_parameters.join(pd.DataFrame(param_list)))
        object_parameters['contrast'] = 1 
        return object_parameters

    def draw_from_df(self, object_parameters):
        for idx, param in object_parameters.iterrows():
            self.draw_object( **param)

    def draw(self, is_target_present):
        """
        draw the objects with the provided parameters
        """
        object_parameters = self.get_search_array_df(is_target_present)
        self.draw_from_df(object_parameters)

def hexagon_conj_search_array_df(
    n_cols, n_rows, obj_distance, 
    n_target,
    target_param,
    distractor_params):

    """
    gives the object parameters in a dataframe for a standard orientation-colour conjunction search task with jittering contrast
    """

    obj_pos_list = visual_search_utils.horizontal_hexagon_array(n_cols, n_rows, obj_distance)
    n_obj = len(obj_pos_list)
    obj_contrast_list = visual_search_utils.scale(np.random.random(n_obj), minimum=my_param.minimum_contrast, maximum=my_param.maximum_contrast)

    # distractor
    distractor_params = distractor_params[:]
    np.random.shuffle(distractor_params)

    n_distractor = n_obj - n_target
    n_evenly_divided = (n_distractor//len(distractor_params))
    n_leftout = n_distractor - n_evenly_divided*len(distractor_params)
    distractor_param_list = distractor_params*n_evenly_divided + distractor_params[:n_leftout]

    # target
    target_param_list = [target_param]*int(n_target)

    # the full list
    param_list = distractor_param_list + target_param_list
    np.random.shuffle(param_list)

    # data frame for object parambers
    object_parameters = pd.DataFrame(obj_pos_list, columns=['x', 'y'])
    object_parameters['contrast'] = obj_contrast_list
    param_list=pd.DataFrame(param_list).values

    object_parameters['ori']= param_list[:, 0]
    object_parameters['color_name']= param_list[:, 1]

    return object_parameters

def conj_search_array_df(
    n_obj,
    n_target,
    radius,
    target_param,
    distractor_params):

    """
    Using the Kmeans method, 
    gives the object parameters in a dataframe for a standard orientation-colour conjunction search task with jittering contrast
    """

    obj_pos_list = visual_search_utils.kmean_random(n_obj=n_obj, radius=radius, center=(0,0))
    obj_contrast_list = visual_search_utils.scale(np.random.random(n_obj), minimum=my_param.minimum_contrast, maximum=my_param.maximum_contrast)

    # distractor
    distractor_params = distractor_params[:]
    np.random.shuffle(distractor_params)

    n_distractor = n_obj - n_target
    n_evenly_divided = (n_distractor//len(distractor_params))
    n_leftout = n_distractor - n_evenly_divided*len(distractor_params)
    distractor_param_list = distractor_params*n_evenly_divided + distractor_params[:n_leftout]

    # target
    target_param_list = [target_param]*int(n_target)

    # the full list
    param_list = distractor_param_list + target_param_list
    np.random.shuffle(param_list)

    # data frame for object parambers
    object_parameters = pd.DataFrame(obj_pos_list, columns=['x', 'y'])
    object_parameters['contrast'] = obj_contrast_list
    param_list=pd.DataFrame(param_list).values

    object_parameters['ori']= param_list[:, 0]
    object_parameters['color_name']= param_list[:, 1]

    return object_parameters

def intro(win):
    visual.TextStim(win, text='Please press space to start', color=(1,1,1)).draw()
    win.flip()

    waitResponse = event.waitKeys(keyList=['space'])
    win.flip()

def rest(win, n_done, n_total):
    visual.TextStim(win, text='%s of %s trials were completed\n\nPlease press the spacebar when you are ready to continue'%(n_done, n_total), color=(1,1,1)).draw()
    win.flip()

    waitResponse = event.waitKeys(keyList=['space'])
    win.flip()

def thanks(win):
    visual.TextStim(win, text='Thank you!', color=(1,1,1)).draw()
    win.flip()

    waitResponse = event.waitKeys(keyList=['space'])
    win.flip()


