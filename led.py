import board
import neopixel
import digitalio

class Led:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
        self.extraLedPin = None

    def setExtraLed(self, pin):
        self.extraLedPin = digitalio.DigitalInOut(pin)
        self.extraLedPin.direction = digitalio.Direction.OUTPUT

    def setLedState(self, state):
        if state:
            self.pixels.fill((0, 0, 255))
        else:
            self.pixels.fill((0, 0, 0))

        if self.extraLedPin != None:
            self.extraLedPin.value = state
