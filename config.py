import stickCommon as sc
import  json
import storage

class Config:
    def __init__(self):
        self.stickBoundaries = {
            "lowX": 15000,
            "highX": 52535,
            "lowY": 15000,
            "highY": 52535
        }

        self.stickAxesOrientation = {
            "x": {
                "axis": 0,
                "reverse": False
            },
            "y": {
                "axis": 1,
                "reverse": True
            }
        }

        self.deadzoneSize = 3000
        self.kbModeOffsets = {
            "x": 10,
            "y": 10
        }
        self.kbModeYConeEnd = 90

        self.profiles = [self.getDefaultProfileData("1")]

    def getDefaultProfileData(self, name = ""):
        return {
            "name": name,
            "joystickButton": "leftAlt",
            "isKbModeEnabled": False,
            "kbMode": {
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right"
            }
        }

    def setStickXLow(self, value):
        self.stickBoundaries["lowX"] = value

    def setStickXHigh(self, value):
        self.stickBoundaries["highX"] = value

    def setStickYLow(self, value):
        self.stickBoundaries["lowY"] = value

    def setStickYHigh(self, value):
        self.stickBoundaries["highY"] = value

    def setStickXOrientation(self, value):
        self.stickAxesOrientation["x"]["axis"] = int(value["axis"])
        self.stickAxesOrientation["x"]["reverse"] = bool(value["reverse"])

    def setStickYOrientation(self, value):
        self.stickAxesOrientation["y"]["axis"] = int(value["axis"])
        self.stickAxesOrientation["y"]["reverse"] = bool(value["reverse"])

    def setDeadzoneSize(self, value):
        self.deadzoneSize = sc.getStickValue(value)
        return self.deadzoneSize

    def setKbModeXOffset(self, value):
        self.kbModeOffsets["x"] = sc.getStickValue(value)
        return self.kbModeOffsets["x"]

    def setKbModeYOffset(self, value):
        self.kbModeOffsets["y"] = sc.getStickValue(value)
        return self.kbModeOffsets["y"]

    def setKbModeYConeEnd(self, value):
        self.kbModeYConeEnd = value
        return self.kbModeYConeEnd

    def loadFromFile(self):
        configFilePointer = None

        try:
            configFilePointer = open('config.json', 'r')
        except:
            pass

        if configFilePointer != None:
            configData = json.load(configFilePointer)
            configFilePointer.close()

            if configData:
                if "stickBoundaries" in configData:
                    self.stickBoundaries = configData["stickBoundaries"]

                if "stickAxesOrientation" in configData:
                    self.stickAxesOrientation = configData["stickAxesOrientation"]

                if "deadzoneSize" in configData:
                    self.deadzoneSize = configData["deadzoneSize"]

                if "kbModeOffsets" in configData:
                    self.kbModeOffsets = configData["kbModeOffsets"]

                if "kbModeYConeEnd" in configData:
                    self.kbModeYConeEnd = configData["kbModeYConeEnd"]

                if "profiles" in configData:
                    self.profiles = configData["profiles"]

    def saveToFile(self):
        configData = {
            "stickBoundaries": self.stickBoundaries,
            "stickAxesOrientation": self.stickAxesOrientation,
            "deadzoneSize": self.deadzoneSize,
            "kbModeOffsets": self.kbModeOffsets,
            "kbModeYConeEnd": self.kbModeYConeEnd,
            "profiles": self.profiles
        }

        configJson = json.dumps(configData)
        written = 0

        with open('config.json', 'w') as f:
            written = f.write(configJson)

        if written > 0:
            return True
        else:
            return False

    def getDataJson(self):
        configData = {
            "stickBoundaries": self.stickBoundaries,
            "stickAxesOrientation": self.stickAxesOrientation,
            "deadzoneSize": self.deadzoneSize,
            "kbModeOffsets": self.kbModeOffsets,
            "kbModeYConeEnd": self.kbModeYConeEnd,
            "profiles": self.profiles
        }

        return json.dumps(configData)
