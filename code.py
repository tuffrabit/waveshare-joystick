import board
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
from actionManager import ActionManager
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
actionManager = ActionManager(keyboard, gp)
serialHelper = SerialHelper()
currentProfile = None
isKeyboardMode = False
stickXOrientationAxis = 0
stickXOrientationReverse = False
stickYOrientationAxis = 1
stickYOrientationReverse = True

actionManager.registerControl("stickButton")
actionManager.registerControl("kbUp")
actionManager.registerControl("kbDown")
actionManager.registerControl("kbLeft")
actionManager.registerControl("kbRight")

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

# The stick switch line is weakly coupled to the Y-axis wiper inside the
# stick module: at full "up" deflection the wiper nears ground and drags the
# button line low enough to read as a digital press. Measured on device with
# the pin configured as analog: line idles ~40k, full-up sag ~9.3k-11.7k, a
# real click < ~500. Read it as an analog threshold instead of digital.
# GP28 is ADC channel 2 (A2); the hysteresis band also absorbs click bounce.
STICK_BUTTON_PRESS_THRESHOLD = 3000
STICK_BUTTON_RELEASE_THRESHOLD = 6000
joySelectAnalog = analogio.AnalogIn(board.A2)
stickButtonIsPressed = False

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
    global isKeyboardMode
    global actionManager

    isKeyboardMode = profileHelper.getIsKbModeEnabled(currentProfile)

    actionManager.setBinding("stickButton", profileHelper.getJoystickButton(currentProfile))
    actionManager.setBinding("kbUp", profileHelper.getKbModeBinding("up", currentProfile))
    actionManager.setBinding("kbDown", profileHelper.getKbModeBinding("down", currentProfile))
    actionManager.setBinding("kbLeft", profileHelper.getKbModeBinding("left", currentProfile))
    actionManager.setBinding("kbRight", profileHelper.getKbModeBinding("right", currentProfile))

setRunValuesFromCurrentProfile()
resolveStickOrientation()

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

    rawStickButtonValue = joySelectAnalog.value

    if rawStickButtonValue < STICK_BUTTON_PRESS_THRESHOLD:
        stickButtonIsPressed = True
    elif rawStickButtonValue > STICK_BUTTON_RELEASE_THRESHOLD:
        stickButtonIsPressed = False

    actionManager.setPhysicalState("stickButton", stickButtonIsPressed)
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
        actionManager.setPhysicalState("kbUp", up)
        actionManager.setPhysicalState("kbDown", down)
        actionManager.setPhysicalState("kbLeft", left)
        actionManager.setPhysicalState("kbRight", right)
    else:
        gp.move_joysticks(x=stickValues[0], y=stickValues[1])

    # Flush aggregated HID once, after all inputs for this iteration.
    actionManager.applyOutputs()

    navigationAction = actionManager.consumeNavigation()
    profile = None

    if navigationAction == "nextProfile":
        profile = profileManager.getNextProfile()
    elif navigationAction == "previousProfile":
        profile = profileManager.getPreviousProfile()

    if profile != None:
        currentProfile = profile
        setRunValuesFromCurrentProfile()
        actionManager.neutralizeOutputs()

    if reloadCurrentProfile:
        reloadCurrentProfile = False
        currentProfile = profileManager.getCurrentProfile()

        if currentProfile != None:
            setRunValuesFromCurrentProfile()
            actionManager.neutralizeOutputs()
