import board
import digitalio
import analogio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from hid_gamepad import Gamepad
from stickDeadzone import StickDeadzone
from stick import Stick
from led import Led
from startup import Startup
from kbMode import KbMode

# Key Bindings
BUTTON_JOYSTICK_1_KEY = 1
BUTTON_JOYSTICK_KEY = Keycode.G
KEYBOARD_MODE_STICK_UP_KEY = Keycode.UP_ARROW
KEYBOARD_MODE_STICK_DOWN_KEY = Keycode.DOWN_ARROW
KEYBOARD_MODE_STICK_LEFT_KEY = Keycode.LEFT_ARROW
KEYBOARD_MODE_STICK_RIGHT_KEY = Keycode.RIGHT_ARROW

# Configurable Values
KEYBOARD_MODE_X_START_OFFSET = 45
KEYBOARD_MODE_Y_START_OFFSET = 15

# Globals
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
gp = Gamepad(usb_hid.devices)
stickDeadzone = StickDeadzone()
stick = Stick()
led = Led()
kbMode = KbMode()
startup = Startup()
deadzone = 0
isKeyboardMode = False

#Setup
kbMode.setXStartOffset(KEYBOARD_MODE_X_START_OFFSET)
kbMode.setYStartOffset(KEYBOARD_MODE_Y_START_OFFSET)
kbMode.setKeyboard(keyboard)
led.setExtraLed(board.GP29)
startup.setLed(led)

# Create some buttons. The physical buttons are connected
# to ground on one side and these and these pins on the other.
button = digitalio.DigitalInOut(board.GP28)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Connect an analog two-axis joystick to A4 and A5.
ax = analogio.AnalogIn(board.A0)
ay = analogio.AnalogIn(board.A1)

# Handle deadzone calc
led.setLedState(True)
stickDeadzone.initDeadzone(ax, ay)
deadzone = stickDeadzone.getDeadzone()
stick.setDeadzone(stickDeadzone)
led.setLedState(False)

# Handle startup flags
isKeyboardMode = startup.detectStartupFlags(button)

#print("Deadzone: " + str(deadzone))
#print("Upper Bound: " + str(stickDeadzone.getUpperBoundary()))
#print("Lower Bound: " + str(stickDeadzone.getLowerBoundary()))

while True:
    if button.value:
        #keyboard.release(BUTTON_JOYSTICK_KEY)
        gp.release_buttons(BUTTON_JOYSTICK_1_KEY)
    else:
        #keyboard.press(BUTTON_JOYSTICK_KEY)
        gp.press_buttons(BUTTON_JOYSTICK_1_KEY)

    stickValues = stick.doStickCalculations(ax, ay, True)

    if isKeyboardMode:
        pressedValues = kbMode.calculateStickInput(stickValues)
        kbMode.handleKeyboundModeKey(KEYBOARD_MODE_STICK_UP_KEY, pressedValues[0])
        kbMode.handleKeyboundModeKey(KEYBOARD_MODE_STICK_DOWN_KEY, pressedValues[1])
        kbMode.handleKeyboundModeKey(KEYBOARD_MODE_STICK_LEFT_KEY, pressedValues[2])
        kbMode.handleKeyboundModeKey(KEYBOARD_MODE_STICK_RIGHT_KEY, pressedValues[3])
    else:
        gp.move_joysticks(x=stickValues[0], y=stickValues[1])
