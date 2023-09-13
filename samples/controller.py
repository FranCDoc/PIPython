"""
PI API (WIP)
"""
from pipython import GCSDevice
from pipython import pitools
import time

class PI:
    def __init__(self):
        pidevice = GCSDevice()
        devices = pidevice.EnumerateUSB()
        pidevice.ConnectUSB(devices[0]) # connect to the first device
        pidevice.qVER()
        pitools.startup(pidevice,[],[])
        self.pidevice = pidevice
            
    def setzero(self):
        self.pidevice.MOV(self.pidevice.axes[:2],(22.5,22.5)) # initial position
        time.sleep(0.25)
        res = self.pidevice.qPOS()
        print(res)

    def shift(self,x:str,y:str):
        """Move relative to current position"""
        x = str(float(x)+22.5)
        y = str(float(y)+22.5)
        # if absolute position (x,y) is bigger than 44.9 or smaller than 7.49, return out of limits
        if float(x) > 44.9 or float(x) < 7.49 or float(y) > 44.9 or float(y) < 7.49:
            return "out of limits, stay in range 7.5-45 (um) for both x and y"
        self.pidevice.MOV(self.pidevice.axes[:2],(x,y))

    def getpos(self):
        """Get current position"""
        res = self.pidevice.qPOS()
        return res