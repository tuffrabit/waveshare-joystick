import board
import digitalio
import analogio
import usb_hid
import usb_cdc
import gc
import time

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from hid_gamepad import Gamepad
from stickDeadzone import StickDeadzone
from stick import Stick
from led import Led
from startup import Startup
from kbMode import KbMode
from config import Config
from profileManager import ProfileManager
from profileHelper import ProfileHelper
from keyConverter import KeyConverter
from serialHelper import SerialHelper

# ActionType: KEY = 1
# ActionType: GAMEPAD = 2
# ActionType: PROFILE = 3

# Globals
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
gp = Gamepad(usb_hid.devices)
stickDeadzone = StickDeadzone()
stick = Stick()
led = Led()
kbMode = KbMode()
startup = Startup()
config = Config()
profileManager = ProfileManager()
profileHelper = ProfileHelper()
keyConverter = KeyConverter()
serialHelper = SerialHelper()
currentProfile = None
deadzone = 0
isKeyboardMode = False
keyboardModeStickUpKey = None
keyboardModeStickDownKey = None
keyboardModeStickLeftKey = None
keyboardModeStickRightKey = None
stickButton = None

actionStates = {
    "stickButton": False,
    "kbUp": False,
    "kbDown": False,
    "kbLeft": False,
    "kbRight": False
}

# Config
config.loadFromFile()
profileManager.setConfig(config)
profileHelper.setKeyConverter(keyConverter)
currentProfile = profileManager.getInitialProfile()
serialHelper.setConfig(config)
serialHelper.setProfileManager(profileManager)
serialHelper.setStickDeadzone(stickDeadzone)
serialHelper.setStick(stick)
serialHelper.setKbMode(kbMode)

# Setup
kbMode.setXStartOffset(config.kbModeOffsets['x'])
kbMode.setYStartOffset(config.kbModeOffsets['y'])
kbMode.setYConeEnd(config.kbModeYConeEnd)
kbMode.setKeyboard(keyboard)
led.setExtraLed(board.GP29)
startup.setLed(led)

# Create some buttons. The physical buttons are connected
# to ground on one side and these and these pins on the other.
joySelectButton = digitalio.DigitalInOut(board.GP28)
joySelectButton.direction = digitalio.Direction.INPUT
joySelectButton.pull = digitalio.Pull.UP

# Connect an analog two-axis joystick to A4 and A5.
ax = analogio.AnalogIn(board.A0)
ay = analogio.AnalogIn(board.A1)

# Handle deadzone calc
led.setLedState(True)
stickDeadzone.setDeadzoneBuffer(config.deadzoneSize)
stickDeadzone.setXHigh(config.stickBoundaries["highX"])
stickDeadzone.setXLow(config.stickBoundaries["lowX"])
stickDeadzone.setYHigh(config.stickBoundaries["highY"])
stickDeadzone.setYLow(config.stickBoundaries["lowY"])
stickDeadzone.initDeadzone(ax, ay)
deadzone = stickDeadzone.getDeadzone()
stick.setDeadzone(stickDeadzone)
stick.setXHigh(config.stickBoundaries["highX"])
stick.setXLow(config.stickBoundaries["lowX"])
stick.setYHigh(config.stickBoundaries["highY"])
stick.setYLow(config.stickBoundaries["lowY"])
led.setLedState(False)

# Handle startup flags
startup.detectStartupFlags(joySelectButton)

def setRunValuesFromCurrentProfile():
    # Profile specific stuff
    global profileHelper
    global currentProfile
    global rgbLedValues
    global led
    global isKeyboardMode
    global keyboardModeStickUpKey
    global keyboardModeStickDownKey
    global keyboardModeStickLeftKey
    global keyboardModeStickRightKey
    global stickButton

    isKeyboardMode = profileHelper.getIsKbModeEnabled(currentProfile)
    keyboardModeStickUpKey = profileHelper.getKbModeBinding("up", currentProfile)
    keyboardModeStickDownKey = profileHelper.getKbModeBinding("down", currentProfile)
    keyboardModeStickLeftKey = profileHelper.getKbModeBinding("left", currentProfile)
    keyboardModeStickRightKey = profileHelper.getKbModeBinding("right", currentProfile)
    stickButton = profileHelper.getJoystickButton(currentProfile)

def handleAction(stateIndex, trigger, action):
    global actionStates
    goToNextProfile = False
    goToPreviousProfile = False

    if trigger != actionStates[stateIndex]:
        actionStates[stateIndex] = trigger

        if action["type"] == 1:
            if trigger:
                keyboard.press(action["action"])
            else:
                keyboard.release(action["action"])
        elif action["type"] == 2:
            if trigger:
                gp.press_buttons(action["action"])
            else:
                gp.release_buttons(action["action"])
        elif action["type"] == 3:
            if trigger:
                if action["action"] == "nextProfile":
                    goToNextProfile = True
                elif action["action"] == "previousProfile":
                    goToPreviousProfile = True

    return goToNextProfile, goToPreviousProfile

setRunValuesFromCurrentProfile()
#print("free memory: " + str(gc.mem_alloc()))

goToNextProfile = False
goToPreviousProfile = False
reloadCurrentProfile = False
#currentTime = time.monotonic()
#iterations = 0

if usb_cdc.data:
    usb_cdc.data.reset_input_buffer()

lastUpdateTime = time.monotonic()

while True:
    currentTime = time.monotonic()
    doLoop = True

    # 0.00833 milliseconds = 120hz
    #if (currentTime - lastUpdateTime) >= 0.00833:
    # 0.002 milliseconds = 500hz
    #if (currentTime - lastUpdateTime) >= 0.002:
    #    lastUpdateTime = currentTime
    #    doLoop = True

    if doLoop:
        commandAction = serialHelper.checkForCommands()

        if commandAction is not None:
            if "profileChange" in commandAction and commandAction["profileChange"]:
                reloadCurrentProfile = True

        #if time.monotonic() - currentTime > 1.0:
        #    print("free memory: " + str(gc.mem_alloc()))
        #    print("iterations: " + str(iterations))
        #    print("")
        #    iterations = 0
        #    currentTime = time.monotonic()

        goToNextProfile, goToPreviousProfile = handleAction("stickButton", not joySelectButton.value, stickButton)
        stickValues = stick.doStickCalculations(ax, ay, True)
        stickAxesOrientation = config.stickAxesOrientation
        stickXAxisOrientation = stickAxesOrientation["x"]
        stickYAxisOrientation = stickAxesOrientation["y"]
        tempXValue = stickValues[0]
        tempYValue = stickValues[1]

        if stickXAxisOrientation is not None:
            if stickXAxisOrientation["axis"] == 1:
                stickValues[0] = tempYValue

            if stickXAxisOrientation["reverse"]:
                stickValues[0] = stickValues[0] * -1

        if stickYAxisOrientation is not None:
            if stickYAxisOrientation["axis"] == 0:
                stickValues[1] = tempXValue

            if stickYAxisOrientation["reverse"]:
                stickValues[1] = stickValues[1] * -1

        if isKeyboardMode:
            up, down, left, right = kbMode.calculateStickInput(stickValues)
            goToNextProfile, goToPreviousProfile = handleAction("kbUp", up, keyboardModeStickUpKey)
            goToNextProfile, goToPreviousProfile = handleAction("kbDown", down, keyboardModeStickDownKey)
            goToNextProfile, goToPreviousProfile = handleAction("kbLeft", left, keyboardModeStickLeftKey)
            goToNextProfile, goToPreviousProfile = handleAction("kbRight", right, keyboardModeStickRightKey)
        else:
            gp.move_joysticks(x=stickValues[0], y=stickValues[1])

        if goToNextProfile or goToPreviousProfile:
            profile = None

            if goToNextProfile:
                profile = profileManager.getNextProfile()
            elif goToPreviousProfile:
                profile = profileManager.getPreviousProfile()

            goToNextProfile = False
            goToPreviousProfile = False

            if profile != None:
                currentProfile = profile
                setRunValuesFromCurrentProfile()
                gp.release_all_buttons()
                keyboard.release_all()

        if reloadCurrentProfile:
            reloadCurrentProfile = False
            currentProfile = profileManager.getCurrentProfile()
            setRunValuesFromCurrentProfile()
            gp.release_all_buttons()
            keyboard.release_all()

        #iterations = iterations + 1
