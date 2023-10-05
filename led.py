import board
import neopixel
import digitalio

class Led:
    def __init__(self):
        #self.mainLedPin = digitalio.DigitalInOut(board.GP16)
        #self.mainLedPin.direction = digitalio.Direction.OUTPUT
        #pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False, pixel_order=(1, 0, 2, 3))
        self.pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
        self.extraLedPin = None

    def setExtraLed(self, pin):
        self.extraLedPin = digitalio.DigitalInOut(pin)
        self.extraLedPin.direction = digitalio.Direction.OUTPUT

    def setLedState(self, state):
        #self.mainLedPin.value = not state
        if state:
            self.pixels.fill((0, 0, 255))
        else:
            self.pixels.fill((0, 0, 0))

        if self.extraLedPin != None:
            self.extraLedPin.value = state
