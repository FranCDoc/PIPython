import controller

if __name__ == "__main__":
    c = controller.PI()
    c.setzero()
    c.getpos()
    c.shift(10,10)
    c.getpos()