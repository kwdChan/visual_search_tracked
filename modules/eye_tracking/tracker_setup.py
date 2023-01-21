from __future__ import division
from __future__ import print_function

import pylink, os, random, time, sys
from .psychopy_pylink.EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from PIL import Image  # for preparing the Host backdrop image
from string import ascii_letters, digits
from psychopy import visual, core, event, monitors, gui
def check_EDF_filename(input_name):
    # Set up EDF data file name and local data folder
    #
    # The EDF data filename should not exceed 8 alphanumeric characters
    # use ONLY number 0-9, letters, & _ (underscore) in the filename

    # check if the filename is valid (length <= 8 & no special char)
    allowed_char = ascii_letters + digits + '_'
    if not all([c in allowed_char for c in input_name]):
        print('ERROR: Invalid EDF filename')
        return False
    elif len(input_name) > 8:
        print('ERROR: EDF filename should not exceed 8 characters')
        return False
    else:     
        return True

def setup_output_paths(edf_fname, output_folder):
    """
    return a session folder
    """

    # Set up a folder to store the EDF data files and the associated resources
    # e.g., files defining the interest areas used in each trial
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # We download EDF data file from the EyeLink Host PC to the local hard
    # drive at the end of each testing session, here we rename the EDF to
    # include session start date/time
    time_str = time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
    session_identifier = edf_fname + time_str

    # create a folder for the current testing session in the "results" folder
    session_folder = os.path.join(output_folder, session_identifier)
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)
    
    # create a file path in session_folder
    local_edf_path = os.path.join(session_folder, session_identifier + '.EDF')
    return session_folder, local_edf_path

def connect_to_host_pc(edf_file, dummy_mode, host_ip):
    # Step 1: Connect to the EyeLink Host PC
    #
    # The Host IP address, by default, is "100.1.1.1".
    # the "el_tracker" objected created here can be accessed through the Pylink
    # Set the Host PC address to "None" (without quotes) to run the script
    # in "Dummy Mode"
    if dummy_mode:
        el_tracker = pylink.EyeLink(None)
    else:
        try:
            el_tracker = pylink.EyeLink(host_ip)
        except RuntimeError as error:
            print('ERROR:', error)
            core.quit()
            sys.exit()

    # Step 2: Open an EDF data file on the Host PC
    try:
        el_tracker.openDataFile(edf_file)
    except RuntimeError as err:
        print('ERROR:', err)
        # close the link if we have one open
        if el_tracker.isConnected():
            el_tracker.close()
        core.quit()
        sys.exit()


    # Add a header text to the EDF file to identify the current experiment name
    # This is OPTIONAL. If your text starts with "RECORDED BY " it will be
    # available in DataViewer's Inspector window by clicking
    # the EDF session node in the top panel and looking for the "Recorded By:"
    # field in the bottom panel of the Inspector.
    preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
    el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

    return el_tracker

def tracker_config(el_tracker):

    # Step 3: Configure the tracker
    #
    # Put the tracker in offline mode before we change tracking parameters
    el_tracker.setOfflineMode()

    # Get the software version:  0-dummy mode, 1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
    # 5-EyeLink 1000 Plus, 6-Portable DUO
    if not el_tracker.getDummyMode():
        vstr = el_tracker.getTrackerVersionString()
        eyelink_ver = int(vstr.split()[-1].split('.')[0])
    else: 
        vstr = 'dummy mode'
        eyelink_ver = 0
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

    # File and Link data control
    # what eye events to save in the EDF file, include everything by default
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    # what eye events to make available over the link, include everything by default
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    # what sample data to save in the EDF data file and to make available
    # over the link, include the 'HTARGET' flag to save head target sticker
    # data for supported eye trackers
    if eyelink_ver > 3:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    else:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

    # Optional tracking parameters
    # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
    # if eyelink_ver > 2:
    #     el_tracker.sendCommand("sample_rate 1000")

    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = HV9")
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

def setup_genv(el_tracker, psychopy_window):

    # get the native screen resolution used by PsychoPy
    scn_width, scn_height = psychopy_window.size

    # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
    # see the EyeLink Installation Guide, "Customizing Screen Settings"
    el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendCommand(el_coords)

    # Write a DISPLAY_COORDS message to the EDF file
    # Data Viewer needs this piece of info for proper visualization, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendMessage(dv_coords)

    # Configure a graphics environment (genv) for tracker calibration
    genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, psychopy_window)
    print(genv)  # print out the version number of the CoreGraphics library

    # Set background and foreground colors for the calibration target
    # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
    foreground_color = (-1, -1, -1)
    background_color = psychopy_window.color
    genv.setCalibrationColors(foreground_color, background_color)

    # Set up the calibration target
    #
    # The target could be a "circle" (default), a "picture", a "movie" clip,
    # or a rotating "spiral". To configure the type of calibration target, set
    # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
    # genv.setTargetType('picture')
    #
    # Use gen.setPictureTarget() to set a "picture" target
    # genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
    #
    # Use genv.setMovieTarget() to set a "movie" target
    # genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))

    # Use the default calibration target ('circle')
    genv.setTargetType('circle')

    # Configure the size of the calibration target (in pixels)
    # this option applies only to "circle" and "spiral" targets
    genv.setTargetSize(24)

    # Beeps to play during calibration, validation and drift correction
    # parameters: target, good, error
    #     target -- sound to play when target moves
    #     good -- sound to play on successful operation
    #     error -- sound to play on failure or interruption
    # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
    genv.setCalibrationSounds('', '', '')

    # Request Pylink to use the PsychoPy window we opened above for calibration
    pylink.openGraphicsEx(genv)

    return genv

class PsychopyEyeLinkSet:
    def __init__(self, psychopy_window, edf_fname, output_folder, dummy_mode=False, host_ip="100.1.1.1"):

        self.dummy_mode = dummy_mode

        # validate the edf_filename
        if not check_EDF_filename(edf_fname):
            raise ValueError("invalid edf_fname")

        # setup output folder
        self.host_edf_file = edf_fname + '.EDF'
        self.session_folder, self.local_edf_path = setup_output_paths(edf_fname, output_folder)

        # tracker setup
        self.el_tracker = connect_to_host_pc(self.host_edf_file, dummy_mode=self.dummy_mode, host_ip=host_ip)
        tracker_config(self.el_tracker)

        # psychopy window
        self.win = psychopy_window
        self.scn_width, self.scn_height = self.win.size

        # tracker / psychopy 
        self.genv = setup_genv(self.el_tracker, self.win)

    def __show_msg(self, text, wait_for_keypress=True):
        """ Show task instructions on screen"""
        msg = visual.TextStim(
            self.win, 
            text,
            color = self.genv.getForegroundColor(),
            wrapWidth=self.scn_width/2
            )
        msg.draw()
        self.win.flip()

        # wait indefinitely, terminates upon any key press
        if wait_for_keypress:
            event.waitKeys()
            self.win.flip()

    def calibrate(self):
        
        # show instruction
        if self.dummy_mode:
            task_msg = 'Dummy mode\n' + \
                'Press ENTER to continue'
        else:
            task_msg = 'On each trial, look at the cross to start,\n' + \
                'then press SPACEBAR to end a trial\n' + \
                '\nPress Ctrl-C if you need to quit the task early\n' + \
                '\nNow, press ENTER twice to calibrate tracker'
        self.__show_msg(task_msg)

        # calibrate
        if not self.dummy_mode:
            try:
                self.el_tracker.doTrackerSetup()
                return True
            except RuntimeError as err:
                print('ERROR:', err)
                self.el_tracker.exitCalibration()
                return False
        else: 
            print('dummy mode')
            return True

    def start_recording(self, trial_index):

        el_tracker = self.el_tracker

        # tracker related
        el_tracker.setOfflineMode()

        # clear the host screen before we draw the backdrop
        el_tracker.sendCommand('clear_screen 0')

        # send a "TRIALID" message to mark the start of a trial, see Data
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        el_tracker.sendMessage('TRIALID %d' % trial_index)

        # record_status_message : show some info on the Host PC
        # here we show how many trial has been tested
        status_msg = 'TRIAL number %d' % trial_index
        el_tracker.sendCommand("record_status_message '%s'" % status_msg)

        # put tracker in idle/offline mode before recording
        # Why do this again?????????????? 
        el_tracker.setOfflineMode()

        # Start recording
        # arguments: sample_to_file, events_to_file, sample_over_link,
        # event_over_link (1-yes, 0-no)
        try:
            el_tracker.startRecording(1, 1, 1, 1)
        except RuntimeError as error:
            print("ERROR:", error)

            return False

        # Allocate some time for the tracker to cache some samples
        pylink.pumpDelay(100)

        return True

    def is_recording(self):
        return (self.el_tracker.isRecording() == pylink.TRIAL_OK)

    def stop_recording(self):
        # stop recording; add 100 msec to catch final events before stopping
        pylink.pumpDelay(100)
        self.el_tracker.stopRecording()

    def record_variables_end_of_trial(self, **params):
        el_tracker = self.el_tracker
        for key, value in params.items():
            el_tracker.sendMessage(f'!V TRIAL_VAR {key} {value}')
        el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)

    def terminate_task(self):
        """ Terminate the task gracefully and retrieve the EDF data file

        file_to_retrieve: The EDF on the Host that we would like to download
        win: the current window used by the experimental script
        """

        el_tracker = self.el_tracker

        if el_tracker.isConnected():
            # Terminate the current trial first if the task terminated prematurely
            ret = el_tracker.isRecording()
            if ret == pylink.TRIAL_OK:
                self.abort_trial()

            # Put tracker in Offline mode
            el_tracker.setOfflineMode()

            # Clear the Host PC screen and wait for 500 ms
            el_tracker.sendCommand('clear_screen 0')
            pylink.msecDelay(500)

            # Close the edf data file on the Host
            el_tracker.closeDataFile()

            # Show a file transfer message on the screen
            msg = 'EDF data is transferring from EyeLink Host PC...'
            self.__show_msg(msg, wait_for_keypress=False)

            # Download the EDF data file from the Host PC to a local data folder
            # parameters: source_file_on_the_host, destination_file_on_local_drive
            try:
                el_tracker.receiveDataFile(self.host_edf_file, self.local_edf_path)
            except RuntimeError as error:
                print('ERROR:', error)

            # Close the link to the tracker.
            el_tracker.close()

    def abort_trial(self):
        """Ends recording """

        el_tracker = self.el_tracker

        # Stop recording
        if el_tracker.isRecording():
            # add 100 ms to catch final trial events
            pylink.pumpDelay(100)
            el_tracker.stopRecording()

        # Send a message to clear the Data Viewer screen
        bgcolor_RGB = (116, 116, 116)
        el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

        # send a message to mark trial end
        el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)

    def drawImage_to_host(self, img_path):
        """

        # show a backdrop image on the Host screen, imageBackdrop() the recommended
        # function, if you do not need to scale the image on the Host
        # parameters: image_file, crop_x, crop_y, crop_width, crop_height,
        #             x, y on the Host, drawing options
        ##    el_tracker.imageBackdrop(os.path.join('images', pic),
        ##                             0, 0, scn_width, scn_height, 0, 0,
        ##                             pylink.BX_MAXCONTRAST)

        # If you need to scale the backdrop image on the Host, use the old Pylink
        # bitmapBackdrop(), which requires an additional step of converting the
        # image pixels into a recognizable format by the Host PC.
        # pixels = [line1, ...lineH], line = [pix1,...pixW], pix=(R,G,B)
        #
        # the bitmapBackdrop() command takes time to return, not recommended
        # for tasks where the ITI matters, e.g., in an event-related fMRI task
        # parameters: width, height, pixel, crop_x, crop_y,
        #             crop_width, crop_height, x, y on the Host, drawing options
        #
        # Use the code commented below to convert the image and send the backdrop
        """
        scn_width, scn_height = self.scn_width, self.scn_height
        im = Image.open(img_path)  # read image with PIL
        im = im.resize((scn_width, scn_height))
        img_pixels = im.load()  # access the pixel data of the image
        pixels = [[img_pixels[i, j] for i in range(scn_width)]
                for j in range(scn_height)]
        self.el_tracker.bitmapBackdrop(scn_width, scn_height, pixels,
                                0, 0, scn_width, scn_height,
                                0, 0, pylink.BX_MAXCONTRAST)
