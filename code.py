import board
import digitalio
import analogio
import usb_hid
import usb_cdc

from adafruit_hid.keyboard import Keyboard
from hid_gamepad import Gamepad
from stickDeadzone import StickDeadzone
from stick import Stick
from led import Led
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
gp = Gamepad(usb_hid.devices)
stickDeadzone = StickDeadzone()
stick = Stick()
led = Led()
kbMode = KbMode()
config = Config()
profileManager = ProfileManager()
profileHelper = ProfileHelper()
keyConverter = KeyConverter()
serialHelper = SerialHelper()
currentProfile = None
isKeyboardMode = False
keyboardModeStickUpKey = None
keyboardModeStickDownKey = None
keyboardModeStickLeftKey = None
keyboardModeStickRightKey = None
stickButton = None
stickXOrientationAxis = 0
stickXOrientationReverse = False
stickYOrientationAxis = 1
stickYOrientationReverse = True

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

# Create some buttons. The physical buttons are connected
# to ground on one side and these and these pins on the other.
joySelectButton = digitalio.DigitalInOut(board.GP28)
joySelectButton.direction = digitalio.Direction.INPUT
joySelectButton.pull = digitalio.Pull.UP

# Connect an analog two-axis joystick to A4 and A5.
ax = analogio.AnalogIn(board.A0)
ay = analogio.AnalogIn(board.A1)

def resolveStickOrientation():
    global stickXOrientationAxis
    global stickXOrientationReverse
    global stickYOrientationAxis
    global stickYOrientationReverse

    stickAxesOrientation = config.stickAxesOrientation

    if not isinstance(stickAxesOrientation, dict):
        return

    if isinstance(stickAxesOrientation.get("x"), dict):
        stickXOrientationAxis = stickAxesOrientation["x"].get("axis", 0)
        stickXOrientationReverse = stickAxesOrientation["x"].get("reverse", False)

    if isinstance(stickAxesOrientation.get("y"), dict):
        stickYOrientationAxis = stickAxesOrientation["y"].get("axis", 1)
        stickYOrientationReverse = stickAxesOrientation["y"].get("reverse", True)

# Handle deadzone calc
led.setLedState(True)
stickDeadzone.setDeadzoneBuffer(config.deadzoneSize)
stickDeadzone.setXHigh(config.stickBoundaries["highX"])
stickDeadzone.setXLow(config.stickBoundaries["lowX"])
stickDeadzone.setYHigh(config.stickBoundaries["highY"])
stickDeadzone.setYLow(config.stickBoundaries["lowY"])
stickDeadzone.initDeadzone(ax, ay)
stick.setDeadzone(stickDeadzone)
stick.setXHigh(config.stickBoundaries["highX"])
stick.setXLow(config.stickBoundaries["lowX"])
stick.setYHigh(config.stickBoundaries["highY"])
stick.setYLow(config.stickBoundaries["lowY"])
led.setLedState(False)

def setRunValuesFromCurrentProfile():
    # Profile specific stuff
    global profileHelper
    global currentProfile
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
    global goToNextProfile
    global goToPreviousProfile

    if action is None or action["type"] is None or action["action"] is None:
        return

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

setRunValuesFromCurrentProfile()
resolveStickOrientation()

goToNextProfile = False
goToPreviousProfile = False
reloadCurrentProfile = False

doReadStickValues = False
readStickValues = [
    {"x": 0, "y": 0},
    {"x": 0, "y": 0}
]

if usb_cdc.data:
    usb_cdc.data.reset_input_buffer()

while True:
    commandAction = serialHelper.checkForCommands()

    if commandAction is not None:
        if "profileChange" in commandAction and commandAction["profileChange"]:
            reloadCurrentProfile = True
        elif "readStickValues" in commandAction and commandAction["readStickValues"]:
            doReadStickValues = True
        elif "orientationChange" in commandAction and commandAction["orientationChange"]:
            resolveStickOrientation()

    handleAction("stickButton", not joySelectButton.value, stickButton)
    stickValues = stick.doStickCalculations(ax, ay, True)
    tempXValue = stickValues[0]
    tempYValue = stickValues[1]

    if stickXOrientationAxis == 1:
        stickValues[0] = tempYValue

    if stickXOrientationReverse:
        stickValues[0] = stickValues[0] * -1

    if stickYOrientationAxis == 0:
        stickValues[1] = tempXValue

    if stickYOrientationReverse:
        stickValues[1] = stickValues[1] * -1

    if doReadStickValues:
        doReadStickValues = False
        readStickValues[0]["x"] = ax.value
        readStickValues[0]["y"] = ay.value
        readStickValues[1]["x"] = stickValues[0]
        readStickValues[1]["y"] = stickValues[1]
        serialHelper.write("readStickValues", readStickValues)

    if isKeyboardMode:
        up, down, left, right = kbMode.calculateStickInput(stickValues)
        handleAction("kbUp", up, keyboardModeStickUpKey)
        handleAction("kbDown", down, keyboardModeStickDownKey)
        handleAction("kbLeft", left, keyboardModeStickLeftKey)
        handleAction("kbRight", right, keyboardModeStickRightKey)
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

        if currentProfile != None:
            setRunValuesFromCurrentProfile()
            gp.release_all_buttons()
            keyboard.release_all()
