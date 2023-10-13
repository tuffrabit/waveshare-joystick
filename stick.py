import math

class Stick:
    def __init__(self):
        self.deadzone = None
        self.xHigh = 48535
        self.xLow = 19000
        self.yHigh = 47535
        self.yLow = 19000
        self.mappedDeadzone = 0

    def setDeadzone(self, deadzone):
        self.deadzone = deadzone
        self.mappedDeadzone = self.rangeMap(deadzone.getDeadzone(), 0, 32768, 0.0, 1.0)

    def magnitude(self, x, y):
        return math.sqrt(x * x + y * y)

    def normalize(self, magnitude, x, y):
        return [x / magnitude, y / magnitude]

    def doStickCalculations(self, analogX, analogY, constrainDeadzone = False):
        xStick = analogX.value
        yStick = 65535 - analogY.value

        if constrainDeadzone:
            x = self.constrain(self.rangeMap(xStick, self.xLow, self.xHigh, -1.0, 1.0), -1.0, 1.0)
            y = self.constrain(self.rangeMap(yStick, self.yLow, self.yHigh, -1.0, 1.0), -1.0, 1.0)
            magnitude = self.magnitude(x, y)

            if magnitude > self.mappedDeadzone:
                x = self.constrain(self.rangeMap(xStick, self.xLow, self.xHigh, -1.0, 1.0), -1.0, 1.0)
                y = self.constrain(self.rangeMap(yStick, self.yLow, self.yHigh, -1.0, 1.0), -1.0, 1.0)

                factor = (magnitude - self.mappedDeadzone) / (1 - self.mappedDeadzone)
                rawInputs = self.normalize(magnitude, x, y)
                mappedX = self.rangeMap(rawInputs[0] * factor, -1.0, 1.0, -127, 127)
                mappedY = self.rangeMap(rawInputs[1] * factor, -1.0, 1.0, -127, 127)
                xStick = int(self.constrain(mappedX, -127, 127))
                yStick = int(self.constrain(mappedY, -127, 127))
            else:
                xStick = 0
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
        return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
