"""
import xyaxis
xy = xyaxis.xy(offset_x, offset_y, "/home/user/folder_name/absolute_coor_2d_path.csv",0)
xy.update()
xy.move(i) # 0<=i<N_absolute coordinates
"""

import xycontroller as controller

class xy:
    """Class to control an xy PI controller."""
    def __init__(self, offset_x:int, offset_y:int, coord_path:str, coord_init:int):
        self.c = controller.PI()
        self.c.setoffset(offset_x, offset_y)
        self.c.movecenter()
        self.num_movements = self.c.load_abs_map(coord_path)
        self.c.jump_abs_map(coord_init)
        self.c.getpos()

    def move(self,index:int):
        res = self.c.jump_abs_map(index)
        return res 
    
    def update(self):
        res = self.c.getpos()
        return res
