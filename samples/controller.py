"""
PI controller
Author: Franco Chiesa Docampo
"""

from pipython import GCSDevice, pitools
import time
import csv

SET_PAUSE = 1.5 # pause between movements in seconds

class PI:
    def __init__(self):
        """Initialize PI controller"""
        pidevice = GCSDevice()
        devices = pidevice.EnumerateUSB()
        pidevice.ConnectUSB(devices[0]) # connect to the first device
        pidevice.qVER()
        pitools.startup(pidevice,[],[])
        self.pidevice = pidevice
        self.shift_counter = 0 # counter for relative map
        self.move_counter = 0 # counter for absolute map
        self.buffer_abs = 0 # number of jumps in the absolute map
        self.buffer_rel = 0 # number of jumps in the relative map
        self.offset_x = 0 # offset for absolute map
        self.offset_y = 0 # offset for absolute map

    def movecenter(self):
        """Set 22.5,22.5 as mid point"""
        self.pidevice.MOV(self.pidevice.axes[:2],(22.5,22.5)) # initial position
        time.sleep(SET_PAUSE) # give some time to move before asking for position
        res = self.pidevice.qPOS()
        print("Midpoint set -> current position:",res)
        x = float(res["1"])
        y = float(res["2"])
        return x,y
    
    def move(self,x:float,y:float):
        """Move to absolute position"""
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
        
        self.pidevice.MOV(self.pidevice.axes[:2],(new_pos_x,new_pos_y)) # move to new position in absolute coordinates
    
    def getpos(self):
        """Get current position"""
        res = self.pidevice.qPOS()
        print("Current position:",res)
        x = float(res["1"])
        y = float(res["2"])
        return x,y

    def setoffset(self,x:float,y:float):
        """Set offset for absolute map"""
        self.offset_x = float(x)
        self.offset_y = float(y)
        print("Offset for absolute map set to:",self.offset_x,self.offset_y)
        return self.offset_x,self.offset_y
    
    def load_rel_map(self,map_file:str):
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
        self.buffer_rel = len(self.shift_x_values) # number of jumps in the map
        return self.shift_x_values, self.shift_y_values
            
    def load_abs_map(self,map_file:str):
        """Get absolute 2D movement path from a CSV file. First row is x, second row is y."""
        map_file = str(map_file)+".csv"
        self.move_x_values = []
        self.move_y_values = []
        with open(map_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.move_x_values.append(float(row[0])+float(self.offset_x))
                self.move_y_values.append(float(row[1])+float(self.offset_y))
        print("move x_values:", self.move_x_values)
        print("move y_values:", self.move_y_values)
        self.buffer_abs = len(self.move_x_values)

    def run_rel_map(self,mov_pause_ms:float):
        """Run relative 2D movement map"""
        for i in range(len(self.shift_x_values)):
            print("Position before shift:",self.pidevice.qPOS())
            self.shift(self.shift_x_values[i],self.shift_y_values[i])
            pitools.waitontarget(self.pidevice)
            time.sleep(mov_pause_ms/1000)
            self.getpos()
        print("Done")
    
    def run_abs_map(self,mov_pause_ms:float):
        """Run absolute 2D movement map"""
        for i in range(len(self.move_x_values)):
            print("Position before move:",self.pidevice.qPOS())
            self.move(self.move_x_values[i],self.move_y_values[i])
            pitools.waitontarget(self.pidevice)
            time.sleep(mov_pause_ms/1000)
            self.getpos()
        print("Done")

    def nextshift(self):
        """Execute 1 jump in the relative coordinates map (it has to be loaded first with load_rel_map function). Useful for synchronizing with other devices."""
        self.shift(self.shift_x_values[self.shift_counter],self.shift_y_values[self.shift_counter])
        pitools.waitontarget(self.pidevice)
        time.sleep(SET_PAUSE)
        self.getpos()
        self.shift_counter += 1
        if self.buffer_rel == self.shift_counter:
            self.shift_counter = 0
            print("Restarting map")
    
    def nextmove(self):
        """Execute 1 jump in the absolute coordinates map (it has to be loaded first with load_abs_map function). Useful for synchronizing with other devices."""
        self.move(self.move_x_values[self.move_counter],self.move_y_values[self.move_counter])
        pitools.waitontarget(self.pidevice)
        time.sleep(SET_PAUSE)
        self.getpos()
        self.move_counter += 1
        if self.buffer_abs == self.move_counter:
            self.move_counter = 0
            print("Restarting map")

    def run_rel_path(self,shift_x_values:list,shift_y_values:list,mov_pause_ms:float):
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