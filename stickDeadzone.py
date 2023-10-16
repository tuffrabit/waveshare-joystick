import time

class StickDeadzone:
    def __init__(self):
        self.deadzone = 0
        self.edgeAdjust = 0
        self.upperBoundary = 0
        self.lowerBoundary = 0

    def getDeadzone(self):
        return self.deadzone

    def getEdgeAdjust(self):
        return self.edgeAdjust

    def getUpperBoundary(self):
        return self.upperBoundary

    def getLowerBoundary(self):
        return self.lowerBoundary

    def diff(self, x, y):
        if x > y:
            return x - y
        elif x < y:
            return y - x

    def initDeadzone(self, analogX, analogY):
        startTime = time.monotonic()
        biggestDiff = 0
        lowestX = 65535
        highestX = 0
        lowestY = 65535
        highestY = 0

        # loop for 5 seconds
        while True:
            newTime = time.monotonic()

            if (newTime - startTime) > 5:
                break

            #65535 is full range
            xValue = analogX.value
            yValue = analogY.value

            if xValue > highestX:
                highestX = xValue

            if xValue < lowestX:
                lowestX = xValue

            if yValue > highestY:
                highestY = yValue

            if yValue < lowestY:
                lowestY = yValue

        lowest = lowestX
        highest = highestX

        if lowestY < lowest:
            lowest = lowestY

        if highestY > highest:
            highest = highestY

        lowDiff = self.diff(32768, lowest)
        highDiff = self.diff(32768, highest)
        biggestDiff = highDiff

        if lowDiff > biggestDiff:
            biggestDiff = lowDiff

        self.deadzone = biggestDiff
        self.initBoundary()

    def initBoundary(self):
        self.deadzone = self.deadzone + 7000
        self.edgeAdjust = self.deadzone + 250
        self.upperBoundary = 32768 + self.deadzone
        self.lowerBoundary = 32768 - self.deadzone
