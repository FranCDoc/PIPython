from math import cos, sin, pi
from pipython import GCSDevice, pitools
from pipython.datarectools import getservotime

class PiController:

    def __init__(self):
        with GCSDevice() as pidevice:
            print('search for controllers...')
            devices = pidevice.EnumerateUSB()
            for i, device in enumerate(devices):
                print('{} - {}'.format(i, device))
            item = int(input('select device to connect: '))
            pidevice.ConnectUSB(devices[item])
            print('connected: {}'.format(pidevice.qIDN().strip()))
            pitools.getaxeslist(devices[item],axes=None)
            if pidevice.HasqVER():
                print('version info:\n{}'.format(pidevice.qVER().strip()))
        return pidevice
    
    def runprofile(self,pidevice,PERIOD:float,CENTERPOS:tuple,AMPLITUDE:tuple,BUFFERMIN:int):
        """Move to start position, set up and run trajectories and wait until they are finished.
        @type pidevice : pipython.gcscommands.GCSCommands
        @param pidevice : The pipython controller.
        @param PERIOD : Duration of one sine period in seconds as float.
        @param CENTERPOS : Center position of the circular motion as float for both axes. Tuple of floats.
        @param AMPLITUDE : Amplitude (i.e. diameter) of the circular motion as float for both axes. Tuple of floats.
        @param BUFFERMIN : Minimum number of points in buffer until motion is started as integer.

        """
        assert 2 == len(pidevice.axes[:2]), 'this sample requires two connected axes'
        trajectories = (1, 2)
        numpoints = pidevice.qSPA(1, 0x22000020)[1][0x22000020]  # maximum buffer size
        xvals = [2 * pi * float(i) / float(numpoints) for i in range(numpoints)]
        xtrajectory = [CENTERPOS[0] + AMPLITUDE[0] / 2.0 * sin(xval) for xval in xvals]
        ytrajectory = [CENTERPOS[1] + AMPLITUDE[1] / 2.0 * cos(xval) for xval in xvals]
        
        print('move axes {} to their start positions {}'.format(pidevice.axes[:2], (xtrajectory[0], ytrajectory[0])))
        pidevice.MOV(pidevice.axes[:2], (xtrajectory[0], ytrajectory[0]))
        pitools.waitontarget(pidevice, pidevice.axes[:2])
        servotime = getservotime(pidevice)
        tgtvalue = int(float(PERIOD) / float(numpoints) / servotime)
        print('set %d servo cycles per point -> period of %.2f seconds' % (tgtvalue, tgtvalue * servotime * numpoints))
        pidevice.TGT(tgtvalue)
        
        print('trajectory timing: {}'.format(pidevice.qTGT()))
        print('clear existing trajectories')
        pidevice.TGC(trajectories)
        pointnum = 0
        print('\r%s' % (' ' * 40)),
        
        while pointnum < numpoints:
            if pidevice.qTGL(1)[1] < BUFFERMIN:
                pidevice.TGA(trajectories, (xtrajectory[pointnum], ytrajectory[pointnum]))
                pointnum += 1
                print('\rappend point {}/{}'.format(pointnum, numpoints)),
            if BUFFERMIN == pointnum:
                print('\nstarting trajectories')
                pidevice.TGS(trajectories)
            if numpoints == pointnum:
                print('\nfinishing trajectories')
                pidevice.TGF(trajectories)
        pitools.waitontrajectory(pidevice, trajectories)