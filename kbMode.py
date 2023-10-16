class KbMode:
    def __init__(self):
        self.xStartOffset = None
        self.yStartOffset = None
        self.keyboard = None

    def setXStartOffset(self, value):
        self.xStartOffset = value

    def setYStartOffset(self, value):
        self.yStartOffset = value

    def setKeyboard(self, keyboard):
        self.keyboard = keyboard

    def calculateStickInput(self, stickValues):
        pressedValues = [False, False, False, False]
        xStick = stickValues[0]
        yStick = stickValues[1]
        xStickAbs = abs(xStick)
        yStickAbs = abs(yStick)

        if xStickAbs > self.xStartOffset:
            extraOffset = self.rangeMap(yStickAbs, 0, 127, self.xStartOffset, 90)

            if xStickAbs > extraOffset:
                if xStick > 0:
                    pressedValues[3] = True
                elif xStick < 0:
                    pressedValues[2] = True

        if yStickAbs > self.yStartOffset:
            if yStick > 0:
                pressedValues[1] = True
            elif yStick < 0:
                pressedValues[0] = True

        return pressedValues

    def handleKeyboundModeKey(self, key, isPressed):
        if isPressed:
            self.keyboard.press(key)
        else:
            self.keyboard.release(key)

    def rangeMap(self, x, inMin, inMax, outMin, outMax):
        return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
