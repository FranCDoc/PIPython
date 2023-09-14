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
            
    def movecenter(self):
        """Set 22.5,22.5 as mid point"""
        self.pidevice.MOV(self.pidevice.axes[:2],(22.5,22.5)) # initial position
        time.sleep(0.25) # give some time to move before asking for position
        res = self.pidevice.qPOS()
        print("Midpoint set -> current position:",res)
        print("Your limits are 7.5-45 (um) for both x and y.")
        x = float(res["1"])
        y = float(res["2"])
        return x,y
    
    def move(self,x:float,y:float):
        """Move to absolute position"""
        if float(x) > 44.9 or float(x) < 7.49 or float(y) > 44.9 or float(y) < 7.49:
            return "Out of limits, stay in range 7.5-45 (um) for both x and y."
        self.pidevice.MOV(self.pidevice.axes[:2],(float(x),float(y))) # move to new position in absolute coordinates

    def shift(self,x:float,y:float):
        """Move relative to current position"""
        shift_x = float(x) # relative shift x
        shift_y = float(y) # relative shift y

        actual_pos = self.pidevice.qPOS() # get current position
        actual_pos_x = actual_pos["1"]
        actual_pos_y = actual_pos["2"] 
        
        new_pos_x = float(actual_pos_x) + shift_x # new absolute position x
        new_pos_y = float(actual_pos_y) + shift_y # new absolute position y

        if float(new_pos_x) > 44.9 or float(new_pos_x) < 7.49 or float(new_pos_y) > 44.9 or float(new_pos_y) < 7.49:
            return "Out of limits, stay in range 7.5-45 (um) for both x and y."
        
        self.pidevice.MOV(self.pidevice.axes[:2],(new_pos_x,new_pos_y)) # move to new position in absolute coordinates
    
    def getpos(self):
        """Get current position"""
        res = self.pidevice.qPOS()
        print("Current position:",res)
        x = float(res["1"])
        y = float(res["2"])
        return x,y
    
    def loadmap(self,map_file:str):
        """Get relative 2D movement path from a CSV file. First row is x, second row is y."""
        map_file = str(map_file)+".csv"
        self.shift_x_values = []
        self.shift_y_values = []
        with open(map_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.shift_x_values.append(float(row[0]))
                self.shift_y_values.append(float(row[1]))
        print("shift x_values:", self.shift_x_values)
        print("shift y_values:", self.shift_y_values)
        return self.shift_x_values, self.shift_y_values

    def runmap(self,mov_pause_ms:float):
        """Run relative 2D movement map"""
        for i in range(len(self.shift_x_values)):
            print("Position before shift:",self.pidevice.qPOS())
            self.shift(self.shift_x_values[i],self.shift_y_values[i])
            pitools.waitontarget(self.pidevice)
            time.sleep(mov_pause_ms/1000)
            self.getpos()
        print("Done")
        
    def runpath(self,shift_x_values:list,shift_y_values:list,mov_pause_ms:float):
        """Run relative 2D movement path based on input lists"""
        for i in range(len(shift_x_values)):
            print("Position before shift:",self.pidevice.qPOS())
            self.shift(shift_x_values[i],shift_y_values[i])
            pitools.waitontarget(self.pidevice)
            time.sleep(mov_pause_ms/1000)
            self.getpos()
        print("Done")

    def geterror(self):
        """Get current error"""
        res = self.pidevice.qERR()
        return res