class Stick:
    def __init__(self):
        self.deadzone = None
        self.xHigh = 63535
        self.xLow = 2000
        self.yHigh = 63535
        self.yLow = 2000

    def setDeadzone(self, deadzone):
        self.deadzone = deadzone

    def doStickCalculations(self, analogX, analogY, constrainDeadzone = False):
        xStick = analogX.value
        yStick = 65535 - analogY.value

        if constrainDeadzone:
            deadzone = self.deadzone.getDeadzone()

            if self.isInsideDeadzone(xStick):
                xStick = 0
            else:
                if xStick > 32768:
                    xMapped = self.rangeMap(xStick - deadzone, 32769, self.xHigh - deadzone, 1, 127)
                    xStick = self.constrain(xMapped, 1, 127)
                elif xStick < 32768:
                    xMapped = self.rangeMap(xStick + deadzone, 32769, self.xLow + deadzone, -1, -127)
                    xStick = self.constrain(xMapped, -127, -1)
                else:
                    xStick = 0

            if self.isInsideDeadzone(yStick):
                yStick = 0
            else:
                if yStick > 32768:
                    yMapped = self.rangeMap(yStick - deadzone, 32769, self.yHigh - deadzone, 1, 127)
                    yStick = self.constrain(yMapped, 1, 127)
                elif yStick < 32768:
                    yMapped = self.rangeMap(yStick + deadzone, 32769, self.yLow + deadzone, -1, -127)
                    yStick = self.constrain(yMapped, -127, -1)
                else:
                    yStick = 0

        return [xStick, yStick]

    def isInsideDeadzone(self, rawStickValue):
        returnValue = False

        if ((rawStickValue > 32768 and rawStickValue <= self.deadzone.getUpperBoundary()) or
        (rawStickValue < 32768 and rawStickValue >= self.deadzone.getLowerBoundary())):
            returnValue = True

        return returnValue

    def constrain(self, x, a, b):
        if x < a:
            x = a
        elif x > b:
            x = b

        return x

    def rangeMap(self, x, inMin, inMax, outMin, outMax):
        return (x - inMin) * (outMax - outMin) // (inMax - inMin) + outMin
