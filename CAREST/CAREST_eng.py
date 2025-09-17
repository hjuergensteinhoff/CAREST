#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.1.4),
    on September 17, 2025, at 14:28
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# Run 'Before Experiment' code from code_bf_exp
# v_19.08.2025
import serial
import time
import struct
import HP_commands_config as hpc
newClock = core.Clock()
# Setup serial port for heat plate
# Load config file parameters
config = hpc.load_config("config_HP.dat")
ser = serial.Serial(config.serial_port_HP, baudrate = 19200, timeout = 1)
ser.reset_input_buffer()
ser.reset_output_buffer()
time.sleep(0.05)
# Setup serial port for scales
if config.serial_port_scales:
   serscales = serial.Serial(config.serial_port_scales, baudrate = 19200, timeout = 1)
   serscales.reset_input_buffer()
   serscales.reset_output_buffer()
   time.sleep(0.05)
   # Bytes to tare and read the scales
   Scale_tare_byte = bytes([0x30])
   Scale_read_byte = bytes([0x0D])
   # Tare the scales
   serscales.write(Scale_tare_byte)
   serscales.flush()
else:
   print(f" Serial scales port is not available ")
# Prepare the HP controller
# Stop ramp if still running from previous experiment
hpc.Stop_ramp(ser)
# Set and control to SV 
hpc.Set_SV(ser, config)
hpc.Ctrl_tempON(ser)
# Set parameters for temperature ramp
hpc.Set_ramp_val(ser, config)
# Calculate total ramp_up_time
ramp_up_time_total = (config.ramp_up_time_bt + 
                     config.ramp_up_time_pt + 
                     config.hold_time_bt + 
                     config.hold_time_pt
                     )
print(f"The time from start to end of the temperature ramp is {ramp_up_time_total} s")
rating_loop_rep_num = int(ramp_up_time_total / 2)
print(f"The maximum number of repeats of the rating loop is {rating_loop_rep_num}")
# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.1.4'
expName = 'CAREST_eng'  # from the Builder filename that created this script
# information about this experiment
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [1280, 720]
_loggingLevel = logging.getLevel('error')
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']
    # override logging level
    _loggingLevel = logging.getLevel(
        prefs.piloting['pilotLoggingLevel']
    )

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    filename = u'data/%s_%s_%s' % (expInfo['participant'], expInfo['session'], expName)
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        originPath='C:\\Users\\hstei\\Documents\\privat\\Anne\\Annes_Wissenschaft\\Psychopy\\CAREST_19_08_2025\\CAREST\\CAREST_eng.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # this outputs to the screen, not a file
    logging.console.setLevel(_loggingLevel)


def setupWindow(expInfo=None, win=None):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=0,
            winType='pyglet', allowStencil=False,
            monitor='testMonitor', color=[0.9216, 0.9216, 0.7255], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height', 
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0.9216, 0.9216, 0.7255]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        expInfo['frameRate'] = 60
    win.mouseVisible = False
    win.hideMessage()
    # show a visual indicator if we're in piloting mode
    if PILOTING and prefs.piloting['showPilotingIndicator']:
        win.showPilotingIndicator()
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    ioSession = '1'
    if 'session' in expInfo:
        ioSession = str(expInfo['session'])
    ioServer = io.launchHubServer(window=win, **ioConfig)
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], playbackComponents=[]):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    playbackComponents : list, tuple
        List of any components with a `pause` method which need to be paused.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # pause any playback components
    for comp in playbackComponents:
        comp.pause()
    # prevent components from auto-drawing
    win.stashAutoDraw()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # flip the screen
        win.flip()
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    for comp in playbackComponents:
        comp.play()
    # restore auto-drawn components
    win.retrieveAutoDraw()
    # reset any timers
    for timer in timers:
        timer.reset()


def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # mark experiment as started
    thisExp.status = STARTED
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    
    # Start Code - component code to be run after the window creation
    
    # --- Initialize components for Routine "StandbyScreen" ---
    text_standbyScreen = visual.TextStim(win=win, name='text_standbyScreen',
        text='Standby',
        font='Open Sans',
        pos=(0, 0.1), height=0.08, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    slider_start = visual.Slider(win=win, name='slider_start',
        startValue=1, size=(0.4, 0.1), pos=(-0.4, -0.4), units=win.units,
        labels=['0', 'Start'], ticks=(1, 2), granularity=0.0,
        style='choice', styleTweaks=('triangleMarker',), opacity=None,
        labelColor='black', markerColor='Red', lineColor='White', colorSpace='rgb',
        font='Open Sans', labelHeight=0.05,
        flip=False, ori=0.0, depth=-2, readOnly=False)
    
    # --- Initialize components for Routine "CalibrateScales" ---
    text_calibrateScales = visual.TextStim(win=win, name='text_calibrateScales',
        text='Please do not touch the plate!\n\nScales are being calibrated.',
        font='Open Sans',
        pos=(0, 0.1), height=0.08, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "WelcomeScreen" ---
    text_welcomeScreen = visual.TextStim(win=win, name='text_welcomeScreen',
        text='Welcome\n\nPlease put your hand flat onto the plate surface',
        font='Open Sans',
        pos=(0, 0.1), height=0.08, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    slider_continue = visual.Slider(win=win, name='slider_continue',
        startValue=1, size=(0.4, 0.1), pos=(-0.4, -0.4), units=win.units,
        labels=['0', 'continue'], ticks=(1, 2), granularity=0.0,
        style='choice', styleTweaks=('triangleMarker',), opacity=None,
        labelColor='LightGray', markerColor='Red', lineColor='White', colorSpace='rgb',
        font='Open Sans', labelHeight=0.05,
        flip=False, ori=0.0, depth=-1, readOnly=False)
    
    # --- Initialize components for Routine "Start_ramp" ---
    text_start_ramp = visual.TextStim(win=win, name='text_start_ramp',
        text=None,
        font='Open Sans',
        pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    
    # --- Initialize components for Routine "VASexercise1" ---
    imageSliderRating_VASex1 = visual.ImageStim(
        win=win,
        name='imageSliderRating_VASex1', 
        image='VAS_as_v3.jpg', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), size=(1.8, 1.0),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    sliderRating_VASex1 = visual.Slider(win=win, name='sliderRating_VASex1',
        startValue=None, size=(1.43, 0.1), pos=(-0.014, -0.35), units=win.units,
        labels=None, ticks=(0, 100), granularity=1.0,
        style='rating', styleTweaks=(), opacity=None,
        labelColor='black', markerColor='red', lineColor='black', colorSpace='rgb',
        font='Open Sans', labelHeight=0.03,
        flip=False, ori=0.0, depth=-1, readOnly=False)
    slider_VASex1_continue = visual.Slider(win=win, name='slider_VASex1_continue',
        startValue=1, size=(0.25, 0.03), pos=(0.45, 0.45), units=win.units,
        labels=[' ','continue'], ticks=(1, 2), granularity=0.0,
        style='choice', styleTweaks=('triangleMarker',), opacity=0.2,
        labelColor='Gray', markerColor='Darkgray', lineColor='White', colorSpace='rgb',
        font='Open Sans', labelHeight=0.015,
        flip=False, ori=0.0, depth=-2, readOnly=False)
    text_VASex1 = visual.TextStim(win=win, name='text_VASex1',
        text='Exercise 1',
        font='Arial',
        pos=(-0.4, 0.4), height=0.05, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    
    # --- Initialize components for Routine "VASexercise2" ---
    imageSliderRating_VASex2 = visual.ImageStim(
        win=win,
        name='imageSliderRating_VASex2', 
        image='VAS_as_v3.jpg', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), size=(1.8, 1.0),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    sliderRating_VASex2 = visual.Slider(win=win, name='sliderRating_VASex2',
        startValue=None, size=(1.43, 0.1), pos=(-0.014, -0.35), units=win.units,
        labels=None, ticks=(0, 100), granularity=1.0,
        style='rating', styleTweaks=(), opacity=None,
        labelColor='black', markerColor='red', lineColor='black', colorSpace='rgb',
        font='Open Sans', labelHeight=0.03,
        flip=False, ori=0.0, depth=-1, readOnly=False)
    slider_VASex2_continue = visual.Slider(win=win, name='slider_VASex2_continue',
        startValue=1, size=(0.25, 0.03), pos=(0.45, 0.45), units=win.units,
        labels=[' ','continue'], ticks=(1, 2), granularity=0.0,
        style='choice', styleTweaks=('triangleMarker',), opacity=0.2,
        labelColor='Gray', markerColor='Darkgray', lineColor='White', colorSpace='rgb',
        font='Open Sans', labelHeight=0.015,
        flip=False, ori=0.0, depth=-2, readOnly=False)
    text_VASex2 = visual.TextStim(win=win, name='text_VASex2',
        text='Exercise 2',
        font='Arial',
        pos=(-0.4, 0.4), height=0.05, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    
    # --- Initialize components for Routine "VASexercise3" ---
    imageSliderRating_VASex3 = visual.ImageStim(
        win=win,
        name='imageSliderRating_VASex3', 
        image='VAS_as_v3.jpg', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), size=(1.8, 1.0),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    sliderRating_VASex3 = visual.Slider(win=win, name='sliderRating_VASex3',
        startValue=None, size=(1.43, 0.1), pos=(-0.014, -0.35), units=win.units,
        labels=None, ticks=(0, 100), granularity=1.0,
        style='rating', styleTweaks=(), opacity=None,
        labelColor='black', markerColor='red', lineColor='black', colorSpace='rgb',
        font='Open Sans', labelHeight=0.03,
        flip=False, ori=0.0, depth=-1, readOnly=False)
    slider_VASex3_continue = visual.Slider(win=win, name='slider_VASex3_continue',
        startValue=1, size=(0.25, 0.03), pos=(0.45, 0.45), units=win.units,
        labels=[' ','continue'], ticks=(1, 2), granularity=0.0,
        style='choice', styleTweaks=('triangleMarker',), opacity=0.2,
        labelColor='Gray', markerColor='Darkgray', lineColor='White', colorSpace='rgb',
        font='Open Sans', labelHeight=0.015,
        flip=False, ori=0.0, depth=-2, readOnly=False)
    text_VASex3 = visual.TextStim(win=win, name='text_VASex3',
        text='Exercise 3',
        font='Arial',
        pos=(-0.4, 0.4), height=0.05, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    
    # --- Initialize components for Routine "trial" ---
    imageSliderRating = visual.ImageStim(
        win=win,
        name='imageSliderRating', 
        image='VAS_as_v3.jpg', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), size=(1.8, 1.0),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    sliderRating = visual.Slider(win=win, name='sliderRating',
        startValue=None, size=(1.43, 0.1), pos=(-0.014, -0.35), units=win.units,
        labels=None, ticks=(0, 100), granularity=1.0,
        style='rating', styleTweaks=(), opacity=None,
        labelColor='black', markerColor='red', lineColor='black', colorSpace='rgb',
        font='Open Sans', labelHeight=0.03,
        flip=False, ori=0.0, depth=-1, readOnly=False)
    slider_stop = visual.Slider(win=win, name='slider_stop',
        startValue=1, size=(0.25, 0.03), pos=(0.45, 0.45), units=win.units,
        labels=['ON','OFF'], ticks=(1, 2), granularity=0.0,
        style='choice', styleTweaks=('triangleMarker',), opacity=0.2,
        labelColor='Gray', markerColor='Darkgray', lineColor='White', colorSpace='rgb',
        font='Open Sans', labelHeight=0.015,
        flip=False, ori=0.0, depth=-2, readOnly=False)
    
    # --- Initialize components for Routine "GoodbyScreen" ---
    text = visual.TextStim(win=win, name='text',
        text='Thank you for your participation!',
        font='Open Sans',
        pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # create some handy timers
    
    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    win.flip()  # flip window to reset last flip timer
    # store the exact time the global clock started
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    # --- Prepare to start Routine "StandbyScreen" ---
    continueRoutine = True
    # update component parameters for each repeat
    slider_start.reset()
    # keep track of which components have finished
    StandbyScreenComponents = [text_standbyScreen, slider_start]
    for thisComponent in StandbyScreenComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "StandbyScreen" ---
    routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_standbyScreen* updates
        
        # if text_standbyScreen is starting this frame...
        if text_standbyScreen.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_standbyScreen.frameNStart = frameN  # exact frame index
            text_standbyScreen.tStart = t  # local t and not account for scr refresh
            text_standbyScreen.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_standbyScreen, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_standbyScreen.status = STARTED
            text_standbyScreen.setAutoDraw(True)
        
        # if text_standbyScreen is active this frame...
        if text_standbyScreen.status == STARTED:
            # update params
            pass
        
        # *slider_start* updates
        
        # if slider_start is starting this frame...
        if slider_start.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            slider_start.frameNStart = frameN  # exact frame index
            slider_start.tStart = t  # local t and not account for scr refresh
            slider_start.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(slider_start, 'tStartRefresh')  # time at next scr refresh
            # update status
            slider_start.status = STARTED
            slider_start.setAutoDraw(True)
        
        # if slider_start is active this frame...
        if slider_start.status == STARTED:
            # update params
            pass
        
        # Check slider_start for response to end Routine
        if slider_start.getRating() is not None and slider_start.status == STARTED:
            continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in StandbyScreenComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "StandbyScreen" ---
    for thisComponent in StandbyScreenComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.nextEntry()
    # the Routine "StandbyScreen" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "CalibrateScales" ---
    continueRoutine = True
    # update component parameters for each repeat
    # keep track of which components have finished
    CalibrateScalesComponents = [text_calibrateScales]
    for thisComponent in CalibrateScalesComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "CalibrateScales" ---
    routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 5.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_calibrateScales* updates
        
        # if text_calibrateScales is starting this frame...
        if text_calibrateScales.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_calibrateScales.frameNStart = frameN  # exact frame index
            text_calibrateScales.tStart = t  # local t and not account for scr refresh
            text_calibrateScales.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_calibrateScales, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_calibrateScales.status = STARTED
            text_calibrateScales.setAutoDraw(True)
        
        # if text_calibrateScales is active this frame...
        if text_calibrateScales.status == STARTED:
            # update params
            pass
        
        # if text_calibrateScales is stopping this frame...
        if text_calibrateScales.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_calibrateScales.tStartRefresh + 5-frameTolerance:
                # keep track of stop time/frame for later
                text_calibrateScales.tStop = t  # not accounting for scr refresh
                text_calibrateScales.tStopRefresh = tThisFlipGlobal  # on global time
                text_calibrateScales.frameNStop = frameN  # exact frame index
                # update status
                text_calibrateScales.status = FINISHED
                text_calibrateScales.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in CalibrateScalesComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "CalibrateScales" ---
    for thisComponent in CalibrateScalesComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # Run 'End Routine' code from code_calibrateScales
    # Tare the scales
    if config.serial_port_scales:
       serscales.reset_input_buffer()
       serscales.reset_output_buffer()
       time.sleep(0.1)
       serscales.write(Scale_tare_byte)
       serscales.flush()
       time.sleep(0.1)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-5.000000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "WelcomeScreen" ---
    continueRoutine = True
    # update component parameters for each repeat
    thisExp.addData('WelcomeScreen.started', globalClock.getTime(format='float'))
    slider_continue.reset()
    # keep track of which components have finished
    WelcomeScreenComponents = [text_welcomeScreen, slider_continue]
    for thisComponent in WelcomeScreenComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "WelcomeScreen" ---
    routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_welcomeScreen* updates
        
        # if text_welcomeScreen is starting this frame...
        if text_welcomeScreen.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_welcomeScreen.frameNStart = frameN  # exact frame index
            text_welcomeScreen.tStart = t  # local t and not account for scr refresh
            text_welcomeScreen.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_welcomeScreen, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_welcomeScreen.status = STARTED
            text_welcomeScreen.setAutoDraw(True)
        
        # if text_welcomeScreen is active this frame...
        if text_welcomeScreen.status == STARTED:
            # update params
            pass
        
        # *slider_continue* updates
        
        # if slider_continue is starting this frame...
        if slider_continue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            slider_continue.frameNStart = frameN  # exact frame index
            slider_continue.tStart = t  # local t and not account for scr refresh
            slider_continue.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(slider_continue, 'tStartRefresh')  # time at next scr refresh
            # update status
            slider_continue.status = STARTED
            slider_continue.setAutoDraw(True)
        
        # if slider_continue is active this frame...
        if slider_continue.status == STARTED:
            # update params
            pass
        
        # Check slider_continue for response to end Routine
        if slider_continue.getRating() is not None and slider_continue.status == STARTED:
            continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in WelcomeScreenComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "WelcomeScreen" ---
    for thisComponent in WelcomeScreenComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('WelcomeScreen.stopped', globalClock.getTime(format='float'))
    thisExp.nextEntry()
    # the Routine "WelcomeScreen" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "Start_ramp" ---
    continueRoutine = True
    # update component parameters for each repeat
    # Run 'Begin Routine' code from code_start_ramp
    if config.serial_port_scales:
       serscales.write(Scale_read_byte)
       serscales.flush()
       time.sleep(0.4)
       serscales.readline()
    hpc.Start_ramp(ser)
    # keep track of which components have finished
    Start_rampComponents = [text_start_ramp]
    for thisComponent in Start_rampComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "Start_ramp" ---
    routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 0.5:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_start_ramp* updates
        
        # if text_start_ramp is starting this frame...
        if text_start_ramp.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_start_ramp.frameNStart = frameN  # exact frame index
            text_start_ramp.tStart = t  # local t and not account for scr refresh
            text_start_ramp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_start_ramp, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_start_ramp.status = STARTED
            text_start_ramp.setAutoDraw(True)
        
        # if text_start_ramp is active this frame...
        if text_start_ramp.status == STARTED:
            # update params
            pass
        
        # if text_start_ramp is stopping this frame...
        if text_start_ramp.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_start_ramp.tStartRefresh + 0.5-frameTolerance:
                # keep track of stop time/frame for later
                text_start_ramp.tStop = t  # not accounting for scr refresh
                text_start_ramp.tStopRefresh = tThisFlipGlobal  # on global time
                text_start_ramp.frameNStop = frameN  # exact frame index
                # update status
                text_start_ramp.status = FINISHED
                text_start_ramp.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Start_rampComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Start_ramp" ---
    for thisComponent in Start_rampComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # Run 'End Routine' code from code_clockReset
    newClock.reset()
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-0.500000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "VASexercise1" ---
    continueRoutine = True
    # update component parameters for each repeat
    sliderRating_VASex1.reset()
    slider_VASex1_continue.reset()
    # keep track of which components have finished
    VASexercise1Components = [imageSliderRating_VASex1, sliderRating_VASex1, slider_VASex1_continue, text_VASex1]
    for thisComponent in VASexercise1Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "VASexercise1" ---
    routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 100.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *imageSliderRating_VASex1* updates
        
        # if imageSliderRating_VASex1 is starting this frame...
        if imageSliderRating_VASex1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            imageSliderRating_VASex1.frameNStart = frameN  # exact frame index
            imageSliderRating_VASex1.tStart = t  # local t and not account for scr refresh
            imageSliderRating_VASex1.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(imageSliderRating_VASex1, 'tStartRefresh')  # time at next scr refresh
            # update status
            imageSliderRating_VASex1.status = STARTED
            imageSliderRating_VASex1.setAutoDraw(True)
        
        # if imageSliderRating_VASex1 is active this frame...
        if imageSliderRating_VASex1.status == STARTED:
            # update params
            pass
        
        # if imageSliderRating_VASex1 is stopping this frame...
        if imageSliderRating_VASex1.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > imageSliderRating_VASex1.tStartRefresh + 100-frameTolerance:
                # keep track of stop time/frame for later
                imageSliderRating_VASex1.tStop = t  # not accounting for scr refresh
                imageSliderRating_VASex1.tStopRefresh = tThisFlipGlobal  # on global time
                imageSliderRating_VASex1.frameNStop = frameN  # exact frame index
                # update status
                imageSliderRating_VASex1.status = FINISHED
                imageSliderRating_VASex1.setAutoDraw(False)
        
        # *sliderRating_VASex1* updates
        
        # if sliderRating_VASex1 is starting this frame...
        if sliderRating_VASex1.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sliderRating_VASex1.frameNStart = frameN  # exact frame index
            sliderRating_VASex1.tStart = t  # local t and not account for scr refresh
            sliderRating_VASex1.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(sliderRating_VASex1, 'tStartRefresh')  # time at next scr refresh
            # update status
            sliderRating_VASex1.status = STARTED
            sliderRating_VASex1.setAutoDraw(True)
        
        # if sliderRating_VASex1 is active this frame...
        if sliderRating_VASex1.status == STARTED:
            # update params
            pass
        
        # if sliderRating_VASex1 is stopping this frame...
        if sliderRating_VASex1.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > sliderRating_VASex1.tStartRefresh + 100-frameTolerance:
                # keep track of stop time/frame for later
                sliderRating_VASex1.tStop = t  # not accounting for scr refresh
                sliderRating_VASex1.tStopRefresh = tThisFlipGlobal  # on global time
                sliderRating_VASex1.frameNStop = frameN  # exact frame index
                # update status
                sliderRating_VASex1.status = FINISHED
                sliderRating_VASex1.setAutoDraw(False)
        
        # *slider_VASex1_continue* updates
        
        # if slider_VASex1_continue is starting this frame...
        if slider_VASex1_continue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            slider_VASex1_continue.frameNStart = frameN  # exact frame index
            slider_VASex1_continue.tStart = t  # local t and not account for scr refresh
            slider_VASex1_continue.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(slider_VASex1_continue, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'slider_VASex1_continue.started')
            # update status
            slider_VASex1_continue.status = STARTED
            slider_VASex1_continue.setAutoDraw(True)
        
        # if slider_VASex1_continue is active this frame...
        if slider_VASex1_continue.status == STARTED:
            # update params
            pass
        
        # if slider_VASex1_continue is stopping this frame...
        if slider_VASex1_continue.status == STARTED:
            # is it time to stop? (based on local clock)
            if tThisFlip > 100-frameTolerance:
                # keep track of stop time/frame for later
                slider_VASex1_continue.tStop = t  # not accounting for scr refresh
                slider_VASex1_continue.tStopRefresh = tThisFlipGlobal  # on global time
                slider_VASex1_continue.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'slider_VASex1_continue.stopped')
                # update status
                slider_VASex1_continue.status = FINISHED
                slider_VASex1_continue.setAutoDraw(False)
        
        # Check slider_VASex1_continue for response to end Routine
        if slider_VASex1_continue.getRating() is not None and slider_VASex1_continue.status == STARTED:
            continueRoutine = False
        
        # *text_VASex1* updates
        
        # if text_VASex1 is starting this frame...
        if text_VASex1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_VASex1.frameNStart = frameN  # exact frame index
            text_VASex1.tStart = t  # local t and not account for scr refresh
            text_VASex1.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_VASex1, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_VASex1.status = STARTED
            text_VASex1.setAutoDraw(True)
        
        # if text_VASex1 is active this frame...
        if text_VASex1.status == STARTED:
            # update params
            pass
        
        # if text_VASex1 is stopping this frame...
        if text_VASex1.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_VASex1.tStartRefresh + 100-frameTolerance:
                # keep track of stop time/frame for later
                text_VASex1.tStop = t  # not accounting for scr refresh
                text_VASex1.tStopRefresh = tThisFlipGlobal  # on global time
                text_VASex1.frameNStop = frameN  # exact frame index
                # update status
                text_VASex1.status = FINISHED
                text_VASex1.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in VASexercise1Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "VASexercise1" ---
    for thisComponent in VASexercise1Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('sliderRating_VASex1.response', sliderRating_VASex1.getRating())
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-100.000000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "VASexercise2" ---
    continueRoutine = True
    # update component parameters for each repeat
    sliderRating_VASex2.reset()
    slider_VASex2_continue.reset()
    # keep track of which components have finished
    VASexercise2Components = [imageSliderRating_VASex2, sliderRating_VASex2, slider_VASex2_continue, text_VASex2]
    for thisComponent in VASexercise2Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "VASexercise2" ---
    routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 30.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *imageSliderRating_VASex2* updates
        
        # if imageSliderRating_VASex2 is starting this frame...
        if imageSliderRating_VASex2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            imageSliderRating_VASex2.frameNStart = frameN  # exact frame index
            imageSliderRating_VASex2.tStart = t  # local t and not account for scr refresh
            imageSliderRating_VASex2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(imageSliderRating_VASex2, 'tStartRefresh')  # time at next scr refresh
            # update status
            imageSliderRating_VASex2.status = STARTED
            imageSliderRating_VASex2.setAutoDraw(True)
        
        # if imageSliderRating_VASex2 is active this frame...
        if imageSliderRating_VASex2.status == STARTED:
            # update params
            pass
        
        # if imageSliderRating_VASex2 is stopping this frame...
        if imageSliderRating_VASex2.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > imageSliderRating_VASex2.tStartRefresh + 30-frameTolerance:
                # keep track of stop time/frame for later
                imageSliderRating_VASex2.tStop = t  # not accounting for scr refresh
                imageSliderRating_VASex2.tStopRefresh = tThisFlipGlobal  # on global time
                imageSliderRating_VASex2.frameNStop = frameN  # exact frame index
                # update status
                imageSliderRating_VASex2.status = FINISHED
                imageSliderRating_VASex2.setAutoDraw(False)
        
        # *sliderRating_VASex2* updates
        
        # if sliderRating_VASex2 is starting this frame...
        if sliderRating_VASex2.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sliderRating_VASex2.frameNStart = frameN  # exact frame index
            sliderRating_VASex2.tStart = t  # local t and not account for scr refresh
            sliderRating_VASex2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(sliderRating_VASex2, 'tStartRefresh')  # time at next scr refresh
            # update status
            sliderRating_VASex2.status = STARTED
            sliderRating_VASex2.setAutoDraw(True)
        
        # if sliderRating_VASex2 is active this frame...
        if sliderRating_VASex2.status == STARTED:
            # update params
            pass
        
        # if sliderRating_VASex2 is stopping this frame...
        if sliderRating_VASex2.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > sliderRating_VASex2.tStartRefresh + 30-frameTolerance:
                # keep track of stop time/frame for later
                sliderRating_VASex2.tStop = t  # not accounting for scr refresh
                sliderRating_VASex2.tStopRefresh = tThisFlipGlobal  # on global time
                sliderRating_VASex2.frameNStop = frameN  # exact frame index
                # update status
                sliderRating_VASex2.status = FINISHED
                sliderRating_VASex2.setAutoDraw(False)
        
        # *slider_VASex2_continue* updates
        
        # if slider_VASex2_continue is starting this frame...
        if slider_VASex2_continue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            slider_VASex2_continue.frameNStart = frameN  # exact frame index
            slider_VASex2_continue.tStart = t  # local t and not account for scr refresh
            slider_VASex2_continue.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(slider_VASex2_continue, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'slider_VASex2_continue.started')
            # update status
            slider_VASex2_continue.status = STARTED
            slider_VASex2_continue.setAutoDraw(True)
        
        # if slider_VASex2_continue is active this frame...
        if slider_VASex2_continue.status == STARTED:
            # update params
            pass
        
        # if slider_VASex2_continue is stopping this frame...
        if slider_VASex2_continue.status == STARTED:
            # is it time to stop? (based on local clock)
            if tThisFlip > 30-frameTolerance:
                # keep track of stop time/frame for later
                slider_VASex2_continue.tStop = t  # not accounting for scr refresh
                slider_VASex2_continue.tStopRefresh = tThisFlipGlobal  # on global time
                slider_VASex2_continue.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'slider_VASex2_continue.stopped')
                # update status
                slider_VASex2_continue.status = FINISHED
                slider_VASex2_continue.setAutoDraw(False)
        
        # Check slider_VASex2_continue for response to end Routine
        if slider_VASex2_continue.getRating() is not None and slider_VASex2_continue.status == STARTED:
            continueRoutine = False
        
        # *text_VASex2* updates
        
        # if text_VASex2 is starting this frame...
        if text_VASex2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_VASex2.frameNStart = frameN  # exact frame index
            text_VASex2.tStart = t  # local t and not account for scr refresh
            text_VASex2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_VASex2, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_VASex2.status = STARTED
            text_VASex2.setAutoDraw(True)
        
        # if text_VASex2 is active this frame...
        if text_VASex2.status == STARTED:
            # update params
            pass
        
        # if text_VASex2 is stopping this frame...
        if text_VASex2.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_VASex2.tStartRefresh + 30-frameTolerance:
                # keep track of stop time/frame for later
                text_VASex2.tStop = t  # not accounting for scr refresh
                text_VASex2.tStopRefresh = tThisFlipGlobal  # on global time
                text_VASex2.frameNStop = frameN  # exact frame index
                # update status
                text_VASex2.status = FINISHED
                text_VASex2.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in VASexercise2Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "VASexercise2" ---
    for thisComponent in VASexercise2Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('sliderRating_VASex2.response', sliderRating_VASex2.getRating())
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-30.000000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "VASexercise3" ---
    continueRoutine = True
    # update component parameters for each repeat
    sliderRating_VASex3.reset()
    slider_VASex3_continue.reset()
    # keep track of which components have finished
    VASexercise3Components = [imageSliderRating_VASex3, sliderRating_VASex3, slider_VASex3_continue, text_VASex3]
    for thisComponent in VASexercise3Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "VASexercise3" ---
    routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 30.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *imageSliderRating_VASex3* updates
        
        # if imageSliderRating_VASex3 is starting this frame...
        if imageSliderRating_VASex3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            imageSliderRating_VASex3.frameNStart = frameN  # exact frame index
            imageSliderRating_VASex3.tStart = t  # local t and not account for scr refresh
            imageSliderRating_VASex3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(imageSliderRating_VASex3, 'tStartRefresh')  # time at next scr refresh
            # update status
            imageSliderRating_VASex3.status = STARTED
            imageSliderRating_VASex3.setAutoDraw(True)
        
        # if imageSliderRating_VASex3 is active this frame...
        if imageSliderRating_VASex3.status == STARTED:
            # update params
            pass
        
        # if imageSliderRating_VASex3 is stopping this frame...
        if imageSliderRating_VASex3.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > imageSliderRating_VASex3.tStartRefresh + 30-frameTolerance:
                # keep track of stop time/frame for later
                imageSliderRating_VASex3.tStop = t  # not accounting for scr refresh
                imageSliderRating_VASex3.tStopRefresh = tThisFlipGlobal  # on global time
                imageSliderRating_VASex3.frameNStop = frameN  # exact frame index
                # update status
                imageSliderRating_VASex3.status = FINISHED
                imageSliderRating_VASex3.setAutoDraw(False)
        
        # *sliderRating_VASex3* updates
        
        # if sliderRating_VASex3 is starting this frame...
        if sliderRating_VASex3.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sliderRating_VASex3.frameNStart = frameN  # exact frame index
            sliderRating_VASex3.tStart = t  # local t and not account for scr refresh
            sliderRating_VASex3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(sliderRating_VASex3, 'tStartRefresh')  # time at next scr refresh
            # update status
            sliderRating_VASex3.status = STARTED
            sliderRating_VASex3.setAutoDraw(True)
        
        # if sliderRating_VASex3 is active this frame...
        if sliderRating_VASex3.status == STARTED:
            # update params
            pass
        
        # if sliderRating_VASex3 is stopping this frame...
        if sliderRating_VASex3.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > sliderRating_VASex3.tStartRefresh + 30-frameTolerance:
                # keep track of stop time/frame for later
                sliderRating_VASex3.tStop = t  # not accounting for scr refresh
                sliderRating_VASex3.tStopRefresh = tThisFlipGlobal  # on global time
                sliderRating_VASex3.frameNStop = frameN  # exact frame index
                # update status
                sliderRating_VASex3.status = FINISHED
                sliderRating_VASex3.setAutoDraw(False)
        
        # *slider_VASex3_continue* updates
        
        # if slider_VASex3_continue is starting this frame...
        if slider_VASex3_continue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            slider_VASex3_continue.frameNStart = frameN  # exact frame index
            slider_VASex3_continue.tStart = t  # local t and not account for scr refresh
            slider_VASex3_continue.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(slider_VASex3_continue, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'slider_VASex3_continue.started')
            # update status
            slider_VASex3_continue.status = STARTED
            slider_VASex3_continue.setAutoDraw(True)
        
        # if slider_VASex3_continue is active this frame...
        if slider_VASex3_continue.status == STARTED:
            # update params
            pass
        
        # if slider_VASex3_continue is stopping this frame...
        if slider_VASex3_continue.status == STARTED:
            # is it time to stop? (based on local clock)
            if tThisFlip > 30-frameTolerance:
                # keep track of stop time/frame for later
                slider_VASex3_continue.tStop = t  # not accounting for scr refresh
                slider_VASex3_continue.tStopRefresh = tThisFlipGlobal  # on global time
                slider_VASex3_continue.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'slider_VASex3_continue.stopped')
                # update status
                slider_VASex3_continue.status = FINISHED
                slider_VASex3_continue.setAutoDraw(False)
        
        # Check slider_VASex3_continue for response to end Routine
        if slider_VASex3_continue.getRating() is not None and slider_VASex3_continue.status == STARTED:
            continueRoutine = False
        
        # *text_VASex3* updates
        
        # if text_VASex3 is starting this frame...
        if text_VASex3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_VASex3.frameNStart = frameN  # exact frame index
            text_VASex3.tStart = t  # local t and not account for scr refresh
            text_VASex3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_VASex3, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_VASex3.status = STARTED
            text_VASex3.setAutoDraw(True)
        
        # if text_VASex3 is active this frame...
        if text_VASex3.status == STARTED:
            # update params
            pass
        
        # if text_VASex3 is stopping this frame...
        if text_VASex3.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_VASex3.tStartRefresh + 30-frameTolerance:
                # keep track of stop time/frame for later
                text_VASex3.tStop = t  # not accounting for scr refresh
                text_VASex3.tStopRefresh = tThisFlipGlobal  # on global time
                text_VASex3.frameNStop = frameN  # exact frame index
                # update status
                text_VASex3.status = FINISHED
                text_VASex3.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in VASexercise3Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "VASexercise3" ---
    for thisComponent in VASexercise3Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('sliderRating_VASex3.response', sliderRating_VASex3.getRating())
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-30.000000)
    thisExp.nextEntry()
    
    # set up handler to look after randomisation of conditions etc
    rating_loop = data.TrialHandler(nReps=rating_loop_rep_num, method='sequential', 
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='rating_loop')
    thisExp.addLoop(rating_loop)  # add the loop to the experiment
    thisRating_loop = rating_loop.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisRating_loop.rgb)
    if thisRating_loop != None:
        for paramName in thisRating_loop:
            globals()[paramName] = thisRating_loop[paramName]
    
    for thisRating_loop in rating_loop:
        currentLoop = rating_loop
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
        )
        # abbreviate parameter names if possible (e.g. rgb = thisRating_loop.rgb)
        if thisRating_loop != None:
            for paramName in thisRating_loop:
                globals()[paramName] = thisRating_loop[paramName]
        
        # --- Prepare to start Routine "trial" ---
        continueRoutine = True
        # update component parameters for each repeat
        thisExp.addData('trial.started', globalClock.getTime(format='float'))
        sliderRating.reset()
        slider_stop.reset()
        # Run 'Begin Routine' code from code_clockGetTime
        if newClock.getTime() >= ramp_up_time_total:
            rating_loop.finished = 1
        # keep track of which components have finished
        trialComponents = [imageSliderRating, sliderRating, slider_stop]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "trial" ---
        routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 2.0:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *imageSliderRating* updates
            
            # if imageSliderRating is starting this frame...
            if imageSliderRating.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                imageSliderRating.frameNStart = frameN  # exact frame index
                imageSliderRating.tStart = t  # local t and not account for scr refresh
                imageSliderRating.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(imageSliderRating, 'tStartRefresh')  # time at next scr refresh
                # update status
                imageSliderRating.status = STARTED
                imageSliderRating.setAutoDraw(True)
            
            # if imageSliderRating is active this frame...
            if imageSliderRating.status == STARTED:
                # update params
                pass
            
            # if imageSliderRating is stopping this frame...
            if imageSliderRating.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > imageSliderRating.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    imageSliderRating.tStop = t  # not accounting for scr refresh
                    imageSliderRating.tStopRefresh = tThisFlipGlobal  # on global time
                    imageSliderRating.frameNStop = frameN  # exact frame index
                    # update status
                    imageSliderRating.status = FINISHED
                    imageSliderRating.setAutoDraw(False)
            
            # *sliderRating* updates
            
            # if sliderRating is starting this frame...
            if sliderRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                sliderRating.frameNStart = frameN  # exact frame index
                sliderRating.tStart = t  # local t and not account for scr refresh
                sliderRating.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(sliderRating, 'tStartRefresh')  # time at next scr refresh
                # update status
                sliderRating.status = STARTED
                sliderRating.setAutoDraw(True)
            
            # if sliderRating is active this frame...
            if sliderRating.status == STARTED:
                # update params
                pass
            
            # if sliderRating is stopping this frame...
            if sliderRating.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > sliderRating.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    sliderRating.tStop = t  # not accounting for scr refresh
                    sliderRating.tStopRefresh = tThisFlipGlobal  # on global time
                    sliderRating.frameNStop = frameN  # exact frame index
                    # update status
                    sliderRating.status = FINISHED
                    sliderRating.setAutoDraw(False)
            
            # *slider_stop* updates
            
            # if slider_stop is starting this frame...
            if slider_stop.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                slider_stop.frameNStart = frameN  # exact frame index
                slider_stop.tStart = t  # local t and not account for scr refresh
                slider_stop.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(slider_stop, 'tStartRefresh')  # time at next scr refresh
                # update status
                slider_stop.status = STARTED
                slider_stop.setAutoDraw(True)
            
            # if slider_stop is active this frame...
            if slider_stop.status == STARTED:
                # update params
                pass
            
            # if slider_stop is stopping this frame...
            if slider_stop.status == STARTED:
                # is it time to stop? (based on local clock)
                if tThisFlip > 2-frameTolerance:
                    # keep track of stop time/frame for later
                    slider_stop.tStop = t  # not accounting for scr refresh
                    slider_stop.tStopRefresh = tThisFlipGlobal  # on global time
                    slider_stop.frameNStop = frameN  # exact frame index
                    # update status
                    slider_stop.status = FINISHED
                    slider_stop.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "trial" ---
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        thisExp.addData('trial.stopped', globalClock.getTime(format='float'))
        rating_loop.addData('sliderRating.response', sliderRating.getRating())
        rating_loop.addData('slider_stop.response', slider_stop.getRating())
        # Run 'End Routine' code from code_read_temp
        temperature_PT = hpc.Read_temp(ser)
        rating_loop.addData('temperature_PT', temperature_PT)
        
        # Read contact force data from scales
        if config.serial_port_scales:
           serscales.write(Scale_read_byte)
           serscales.flush()
           time.sleep(0.1)
           cf_bytes_read = serscales.readline()
           decoded_cf_string = cf_bytes_read.decode('latin-1')
           cleaned_cf_string = decoded_cf_string.strip()
           rating_loop.addData('contact_force', cleaned_cf_string)
        else:
           rating_loop.addData('contact_force', None)
        # Run 'End Routine' code from code_marker_save
        rating_loop.addData('sliderRating.markerPos', sliderRating.getMarkerPos())
        #Finish experiment with slider_stop
        if slider_stop.getRating() == 2 :
            hpc.Stop_ramp(ser)
            rating_loop.finished = 1
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if routineForceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-2.000000)
        thisExp.nextEntry()
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
    # completed rating_loop_rep_num repeats of 'rating_loop'
    
    
    # --- Prepare to start Routine "GoodbyScreen" ---
    continueRoutine = True
    # update component parameters for each repeat
    thisExp.addData('GoodbyScreen.started', globalClock.getTime(format='float'))
    # keep track of which components have finished
    GoodbyScreenComponents = [text]
    for thisComponent in GoodbyScreenComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "GoodbyScreen" ---
    routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 10.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text* updates
        
        # if text is starting this frame...
        if text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text.frameNStart = frameN  # exact frame index
            text.tStart = t  # local t and not account for scr refresh
            text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'text.started')
            # update status
            text.status = STARTED
            text.setAutoDraw(True)
        
        # if text is active this frame...
        if text.status == STARTED:
            # update params
            pass
        
        # if text is stopping this frame...
        if text.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text.tStartRefresh + 10.0-frameTolerance:
                # keep track of stop time/frame for later
                text.tStop = t  # not accounting for scr refresh
                text.tStopRefresh = tThisFlipGlobal  # on global time
                text.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'text.stopped')
                # update status
                text.status = FINISHED
                text.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in GoodbyScreenComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "GoodbyScreen" ---
    for thisComponent in GoodbyScreenComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('GoodbyScreen.stopped', globalClock.getTime(format='float'))
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-10.000000)
    thisExp.nextEntry()
    # Run 'End Experiment' code from code_bf_exp
    ser.close()
    if config.serial_port_scales:
       serscales.close()
    
    # mark experiment as finished
    endExperiment(thisExp, win=win)


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='comma')
    thisExp.saveAsPickle(filename)


def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # mark experiment handler as finished
    thisExp.status = FINISHED
    # shut down eyetracker, if there is one
    if deviceManager.getDevice('eyetracker') is not None:
        deviceManager.removeDevice('eyetracker')


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    # shut down eyetracker, if there is one
    if deviceManager.getDevice('eyetracker') is not None:
        deviceManager.removeDevice('eyetracker')
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='iso'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
