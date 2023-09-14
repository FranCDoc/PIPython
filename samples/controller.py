"""
PI controller
Author: Franco Chiesa Docampo
"""

from pipython import GCSDevice, pitools
import time
import csv

class PI:
    def __init__(self):
        """Initialize PI controller"""
        pidevice = GCSDevice()
        devices = pidevice.EnumerateUSB()
        pidevice.ConnectUSB(devices[0]) # connect to the first device
        pidevice.qVER()
        pitools.startup(pidevice,[],[])
        self.pidevice = pidevice
            
    def setzero(self):
        """Set 22.5,22.5 as zero point"""
        self.pidevice.MOV(self.pidevice.axes[:2],(22.5,22.5)) # initial position
        time.sleep(0.25)
        res = self.pidevice.qPOS()
        print("Zero midpoint set at: ",res)
        print("Your limits are 7.5-45 (um) for both x and y.")

    def shift(self,x:str,y:str):
        """Move relative to current position"""
        x = str(float(x)+22.5) # from relative to absolute position
        y = str(float(y)+22.5) # from relative to absolute position
        if float(x) > 44.9 or float(x) < 7.49 or float(y) > 44.9 or float(y) < 7.49:
            return "Out of limits, stay in range 7.5-45 (um) for both x and y."
        self.pidevice.MOV(self.pidevice.axes[:2],(x,y))

    def getpos(self):
        """Get current position"""
        res = self.pidevice.qPOS()
        return res
    
    def getmap(self):
        """Get relative 2D movement path from a CSV file. First row is x, second row is y."""
        map_file = 'relative_coor_2d_path.csv'
        shift_x_values = []
        shift_y_values = []
        with open(map_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                shift_x_values.append(float(row[0]))
                shift_y_values.append(float(row[1]))
        print("x_values:", shift_x_values)
        print("y_values:", shift_y_values)
        return shift_x_values, shift_y_values

    def run_map(self,shift_x_values:list,shift_y_values:list):
        """Run relative 2D movement map"""
        for i in range(len(shift_x_values)):
            self.shift(shift_x_values[i],shift_y_values[i])
            pitools.waitontarget(self.pidevice)
            print("Current position:",self.getpos())
        print("Done")

    def geterror(self):
        """Get current error"""
        res = self.pidevice.qERR()
        return res