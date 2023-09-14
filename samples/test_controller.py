"""
PI test controller
Author: Franco Chiesa Docampo
"""

import controller

if __name__ == "__main__":
    c = controller.PI()
    c.getpos()
    c.shift(10,10)
    c.getpos()
    map = c.getmap()
    c.setzero()
    c.run_map(map[0],map[1])
