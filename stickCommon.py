import math

xHigh = const(46535)
xLow = const(19000)
yHigh = const(47535)
yLow = const(19000)

def magnitude(x, y):
    return math.sqrt(x * x + y * y)

def normalize(magnitude, x, y):
    return [x / magnitude, y / magnitude]

def constrain(x, a, b):
    if x < a:
        x = a
    elif x > b:
        x = b

    return x

def rangeMap(x, inMin, inMax, outMin, outMax):
    return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
