import stickCommon as sc
import math

class Stick:
    def __init__(self):
        self.deadzone = None
        self.mappedDeadzone = 0
        self.deadzoneMagnitude = 0

    def setDeadzone(self, deadzone):
        self.deadzone = deadzone
        self.mappedDeadzone = sc.rangeMap(deadzone.getDeadzone(), 0, 32768, 0.0, 1.0)
        self.deadzoneMagnitude = deadzone.deadzoneMagnitude

    def doStickCalculations(self, analogX, analogY, constrainDeadzone = False):
        xStick = analogX.value
        yStick = 65535 - analogY.value

        if constrainDeadzone:
            x = sc.constrain(sc.rangeMap(xStick, sc.xLow, sc.xHigh, -1.0, 1.0), -1.0, 1.0)
            y = sc.constrain(sc.rangeMap(yStick, sc.yLow, sc.yHigh, -1.0, 1.0), -1.0, 1.0)
            magnitude = sc.magnitude(x, y)

            if magnitude > self.deadzoneMagnitude:
                x = sc.constrain(sc.rangeMap(xStick, sc.xLow, sc.xHigh, -1.0, 1.0), -1.0, 1.0)
                y = sc.constrain(sc.rangeMap(yStick, sc.yLow, sc.yHigh, -1.0, 1.0), -1.0, 1.0)

                factor = (magnitude - self.deadzoneMagnitude) / (1 - self.deadzoneMagnitude)
                rawInputs = sc.normalize(magnitude, x, y)
                mappedX = sc.rangeMap(rawInputs[0] * factor, -1.0, 1.0, -127, 127)
                mappedY = sc.rangeMap(rawInputs[1] * factor, -1.0, 1.0, -127, 127)
                xStick = int(sc.constrain(mappedX, -127, 127))
                yStick = int(sc.constrain(mappedY, -127, 127))
            else:
                xStick = 0
                yStick = 0

        return [xStick, yStick]
