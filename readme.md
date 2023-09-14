# PIPython

PIPython is a collection of Python modules to access a PI device and process
GCS data. It can be used with Python 3.6+ on Windows, Linux and OS X
and without the GCS DLL also on any other platform.

## Installation

By using PIPython you agree to the license agreement, see the provided file:

    eula.md

### From local folder 

Unzip the file PIPython.zip, open a command entry (Linux Console or Windows CMD window) and run:

    python setup.py install

For further reading open the *index.html* file in your browser and see the samples in the
*samples* folder.

### From GitHub

[PIPython on GitHub](https://github.com/PI-PhysikInstrumente/PIPython)

    git clone git@github.com:PI-PhysikInstrumente/PIPython.git
    python setup.py install

### From pypi.org

    pip install PIPython    

### Feedback 

We appreciate your feedback at:

    service@pi.de

## Quickstart

Communicate to a PI device via `GCSDevice` which wraps the GCS DLL functions
and provides methods to connect to the device. Call `GCSDevice` with the
controller name as argument.

~~~python
from pipython import GCSDevice
pidevice = GCSDevice('C-884')
pidevice.InterfaceSetupDlg()
print pidevice.qIDN()
pidevice.CloseConnection()
~~~

`GCSDevice` is a context manager which closes the connection if an exception
raises inside the `with` statement.

~~~python
from pipython import GCSDevice
with GCSDevice('C-884') as pidevice:
    pidevice.InterfaceSetupDlg()
    print(pidevice.qIDN())
~~~

See also the provided samples in the `samples` subdirectory. Start with `quickstart.py`.

## Requirements

Download these python packages with pip install:

- PyUSB
- PySocket
- PySerial

With pipython.interfaces.piusb you can connect a USB device without using the GCS DLL.
This works only with Linux and requires LibUSB which usually is provided by the OS.

## Arguments

From now on `pidevice` refers to a connected `GCSDevice` instance.

### Setter functions

Usually you can call a setter function with
- a dictionary of axes/channels and values
- a list for axes/channels and a list of the values
- a single item for axis/channel and a single value

~~~python
gcs.MOV({'X': 1.23, 'Y': 2.34})
gcs.MOV(['X', 'Y'], [1.23, 2.34])
gcs.MOV('X', 1.23)
~~~

For channels and numeric axis names you can omit the quotes.

~~~python
gcs.MOV({1: 1.23, 2: 2.34})
gcs.MOV([1, 2], [1.23, 2.34])
gcs.MOV(1, 1.23)
~~~


### Getter functions

#### GCS 2.0

Usually getter commands can be called with

- a list of axes/channels.
- a single item for axis/channel, without quotes if numeric
- without any arguments which will return the answer for all available axes/channels

~~~python
gcs.qPOS(['X', 'Y'])
gcs.qPOS('X')
gcs.qPOS(1)
gcs.qPOS()
~~~


#### GCS 3.0

Usually getter commands can be called with

- a single axis
- without any arguments which will return the answer for all available axes

~~~python
gcs.qPOS('AXIS_1')
gcs.qPOS()
~~~

## Return values

Axes or channel related answers are returned as (ordered) dictionary.

~~~python
pidevice.qPOS()
>>>{'X': 1.23, 'Y': 2.34}
~~~


If you do not provide arguments you always have to use strings as keys.

~~~python
pos = pidevice.qPOS()
print(pos['1'])
~~~

The following sample will move all `axes` to `targets` and waits until the motion has finished.
It shows how to use only the values from the returned dictionary.

~~~python
from time import sleep
...
pidevice.MOV(axes, targets)
while not all(list(pidevice.qONT(axes).values())):
    sleep(0.1)
~~~

#### GCS 2.0

If you provide arguments their types are preserved and you can use these as keys.

~~~python
pos = pidevice.qPOS([1, 2, 3])
print(pos[1])
~~~

#### GCS 3.0

If you provide arguments their types are preserved and you can use these as keys.

~~~python
pos = pidevice.qPOS('AXIS_1') # only one axis is possible
print(pos['AXIS_1'])
~~~

## Some hints...

### Helpers

In `pipython.pitools` you will find some helper funtions for your convenience. See the provided
samples for how to use them. The sample above can then be written as:

~~~python
from pipython import pitools
...
pidevice.MOV(axes, targets)
pitools.waitontarget(pidevice, axes)
~~~


### Enable debug logging

To log debug messages on the console just enter these lines prior to calling `GCSDevice`.

~~~python
from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL

PILogger.setLevel(DEBUG)
~~~

### GCSError and error check

By default an "ERR?" command is sent after each command to query if an error
occurred on the device which then will be raised as `GCSError` exception. If communication
speed is an issue you can disable error checking.

~~~python
pidevice.errcheck = False
~~~

To handle a catched `GCSError` exception you can use the defines provided by
`gcserror` instead of pure numeric values. Remember the difference between `GCSError` which
is the exception class and `gcserror` which is the according module.

~~~python
from pipython import GCSDevice, GCSError, gcserror
with GCSDevice('C-884') as pidevice:
    try:
        pidevice.MOV('X', 1.23)
    except GCSError as exc:
        if exc == gcserror.E_1024_PI_MOTION_ERROR:
            print('There was a motion error, please check the mechanics.')
        else:
            raise
~~~

The exception class `GCSError` will translate the error code into a readable message.

~~~python
from pipython import GCSError, gcserror
raise GCSError(gcserror.E_1024_PI_MOTION_ERROR)
>>>GCSError: Motion error: position error too large, servo is switched off automatically (-1024)
~~~

#### GCS 3.0

- to reset the error state of 1 or more axes 
~~~python
for axis in device.axes:
    if axis_has_error(device):
        while check_axis_status_bit(device, axis, AXIS_STATUS_FAULT_REACTION_ACTIVE):
            pass
        print('reset axis error: ', axis)
        device.RES(axis)
~~~


### Big data

Commands like `qDRR()` for GCS 2.0 syntax, or `qREC_DAT()` for GCS 3.0 syntax
which read a large amount of GCS data return immediately with
the header dictionary containing information about the data. Then they will start
a background task that carries on reading data from the device into an internal buffer. The
`bufstate` property returns the progress of the reading as floating point number in the range
0 to 1 and turns to `True` when reading has finished. Hence, when using it in a loop check for
`is not True`. (Remember, this is not the same as `!= True`.)

#### GCS 2.0

~~~python
header = pidevice.qDRR(1, 1, 8192)
while pidevice.bufstate is not True:
    print('read data {:.1f}%...'.format(pidevice.bufstate * 100))
    sleep(0.1)
data = pidevice.bufdata
~~~

#### GCS 3.0

~~~python
header = pidevice.qREC_DAT('REC_1', 'ASCII', 1, 1, 8192)
while pidevice.bufstate is not True:
    print('read data {:.1f}%...'.format(pidevice.bufstate * 100))
    sleep(0.1)
data = pidevice.bufdata
~~~

### Textual interface

Besides the functions implemented in GCSCommands you can send GCS commands as strings to the
controller. Use `read()` for commands returning an answer, `read_gcsdata()` for commands returning
GCS data and `send()` for non-answering commands.

~~~python
print(pidevice.read('POS?'))
print(pidevice.read_gcsdata('DRR? 1 100 1'))
pidevice.send('MOV X 1.23')
~~~

They return the raw string or GCS data from the controller. If `errorcheck` is enabled the
error state is queried from the device automatically. We recommend to use the provided
functions instead of sending raw strings.

In line with the C++ GCS DLL the functions `ReadGCSCommand()` and `GcsCommandset()` are also
available. They will never query an error from the device.

~~~python
print(pidevice.ReadGCSCommand('POS?'))
pidevice.GcsCommandset('MOV X 1.23')
~~~

### Usefull data for development and testing
- https://github.com/libusb/libusb
- https://github.com/Ulm-IQO/qudi/issues/503
- https://github.com/diamond2nv/qudi/blob/POI_autocatch/hardware/motor/piezo_stage_pi_py_gcs2.py
- https://github.com/diamond2nv/qudi/tree/POI_autocatch
- libpi_pi_gcs2.so https://www.physikinstrumente.com/fileadmin/user_upload/web_files/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf
- libpi_pi_gcs2.so http://www.le.infn.it/~chiodini/allow_listing/pi/Manuals/PIGCS_2_0_DLL_SM151E210.pdf
- https://www.physikinstrumente.com/en/products/software-suite/communication-concept-interfaces
- https://pipython.physikinstrumente.com/quickstart.html

### PI Python install procedure

~/PI_drivers/Linux/PI_E727-1.3.0.0-INSTALL/PI_E727$ sudo chmod +x INSTALL 
~/PI_drivers/Linux/PI_E727-1.3.0.0-INSTALL/PI_E727$ sudo ./INSTALL

- NOTE: to look for libpi_pi_gcs2.so -> https://www.physikinstrumente.com/fileadmin/user_upload/web_files/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf

### PI handshake commands

    >>> from pipython import GCSDevice
    >>> pidevice = GCSDevice()
    >>> devices = pidevice.EnumerateUSB()
    >>> pidevice.ConnectUSB(devices[0]) # connect to the first device
    
    descriptor->bLength:    18
    descriptor->bDescriptorType:    1
    descriptor->bcdUSB:     512
    descriptor->bDeviceClass:       0
    descriptor->bDeviceSubClass:    0
    descriptor->bDeviceProtocol:    0
    descriptor->bMaxPacketSize0:    64
    descriptor->idVendor:   6770
    descriptor->idProduct:  4126
    descriptor->bcdDevice:  256
    descriptor->iManufacturer:      1
    descriptor->iProduct:   2
    descriptor->iSerialNumber:      3
    descriptor->bNumConfigurations: 1

    Config 0
            bLength:        9
            bDescriptorType:        2
            wTotalLength:   32
            bNumInterfaces: 1
            bConfigurationValue:    1
            iConfiguration: 0
            bmAttributes:   192
            MaxPower:       32

            Interface 0 - 1 alt settigns

                    setting 0
    :               bLength:        9
                    bDescriptorType:        4
                    bInterfaceNumber:       0
                    bAlternateSetting:      0
                    bNumEndpoints:  2
                    bInterfaceClass:        255
                    bInterfaceSubClass:     0
                    bInterfaceProtocol:     0
                    iInterface:     0

                            Endpoint 0
                            bLength:        7
                            bDescriptorType:        5
                            bEndpointAddress:       1
                            bmAttributes:   2
                            wMaxPacketSize: 64
                            bInterval:      0
                            bRefresh:       0
                            bSynchAddress:  0

                            Endpoint 1
                            bLength:        7
                            bDescriptorType:        5
                            bEndpointAddress:       130
                            bmAttributes:   2
                            wMaxPacketSize: 64
                            bInterval:      0
                            bRefresh:       0
                            bSynchAddress:  0

    >>> print('connected: {}'.format(pidevice.qIDN().strip()))

    connected: (c)2015-2018 Physik Instrumente (PI) GmbH & Co. KG, E-727.3CDA, 120040681, 14.11.01.05

    >>> pidevice.qPOS()
    OrderedDict([('1', 18.83114052), ('2', 17.47277641), ('3', 0.0)])
    
    >>> pidevice.read('POS?')
    '1=1.883246040e+01 \n2=1.747353172e+01 \n3=0.000000000e+00\n'

    >>> pidevice.qVER()
    'libpi_pi_gcs2.so.3.15.3.1 \nFirmware=14.11 \nDriver=01.05 \nFW_STATUS:RELEASE \nPIPython: 2.10.0.2\n'
    
    >>> from pipython import pitools

    >>> len(pidevice.axes[:2])
    2

    >>> STAGES = []  # connect stages to axes
    
    >>> REFMODE = []  # reference the connected stages

    >>> pitools.startup(pidevice,[],[])
 
    >>> pidevice.MOV(pidevice.axes[:2],(20,20))

    >>> pidevice.qPOS()
    OrderedDict([('1', 20.00016403), ('2', 19.99985313), ('3', 0.0)]) 

    >>> from pipython.datarectools import getservotime

    >>> servotime=pgetservotime(pidevice)
    
    >>> servotime
    4.999999874e-05

    >>> import time

    >>> for i in range(20):
            pidevice.MOV(pidevice.axes[:2],(9+i,9+i))
            time.sleep(0.05)
            pidevice.qPOS()
            
        OrderedDict([('1', 8.999832153), ('2', 9.001206398), ('3', 0.0)])
        OrderedDict([('1', 10.00001335), ('2', 9.99992466), ('3', 0.0)])
        OrderedDict([('1', 11.00018692), ('2', 10.99958515), ('3', 0.0)])
        OrderedDict([('1', 11.99965286), ('2', 11.99977303), ('3', 0.0)])
        OrderedDict([('1', 13.00049782), ('2', 13.00060844), ('3', 0.0)])
        OrderedDict([('1', 14.00112629), ('2', 14.00066376), ('3', 0.0)])
        OrderedDict([('1', 15.00018311), ('2', 15.00057602), ('3', 0.0)])
        OrderedDict([('1', 16.00040245), ('2', 15.99970722), ('3', 0.0)])
        OrderedDict([('1', 17.00052261), ('2', 16.99988556), ('3', 0.0)])
        OrderedDict([('1', 18.00056267), ('2', 17.99916267), ('3', 0.0)])
        OrderedDict([('1', 19.00052261), ('2', 19.00024796), ('3', 0.0)])
        OrderedDict([('1', 19.99989128), ('2', 19.99978447), ('3', 0.0)])
        OrderedDict([('1', 21.00043488), ('2', 21.00011063), ('3', 0.0)])
        OrderedDict([('1', 22.00015259), ('2', 22.00050354), ('3', 0.0)])
        OrderedDict([('1', 23.00047493), ('2', 23.00077248), ('3', 0.0)])
        OrderedDict([('1', 24.00079155), ('2', 24.00088692), ('3', 0.0)])
        OrderedDict([('1', 25.00130653), ('2', 25.00071144), ('3', 0.0)])
        OrderedDict([('1', 26.00027275), ('2', 26.00078392), ('3', 0.0)])
        OrderedDict([('1', 27.0018158), ('2', 27.00029755), ('3', 0.0)])
        OrderedDict([('1', 28.00032997), ('2', 28.00071716), ('3', 0.0)])

    >>> for i in range(20):
            pidevice.MOV(pidevice.axes[:2],(28-i,28-i))
            time.sleep(0.25)
            pidevice.qPOS()

        OrderedDict([('1', 27.99976158), ('2', 27.99914932), ('3', 0.0)])
        OrderedDict([('1', 26.99955177), ('2', 27.00034714), ('3', 0.0)])
        OrderedDict([('1', 25.99904442), ('2', 25.99917412), ('3', 0.0)])
        OrderedDict([('1', 24.99968147), ('2', 24.99934578), ('3', 0.0)])
        OrderedDict([('1', 23.99954224), ('2', 24.0005455), ('3', 0.0)])
        OrderedDict([('1', 22.99941635), ('2', 23.00009918), ('3', 0.0)])
        OrderedDict([('1', 21.99959564), ('2', 21.99974632), ('3', 0.0)])
        OrderedDict([('1', 20.99940872), ('2', 21.00028419), ('3', 0.0)])
        OrderedDict([('1', 19.99869537), ('2', 19.99899292), ('3', 0.0)])
        OrderedDict([('1', 18.99982452), ('2', 19.00021172), ('3', 0.0)])
        OrderedDict([('1', 17.99996948), ('2', 17.9993515), ('3', 0.0)])
        OrderedDict([('1', 16.99900818), ('2', 16.99897194), ('3', 0.0)])
        OrderedDict([('1', 15.99912453), ('2', 15.9992981), ('3', 0.0)])
        OrderedDict([('1', 14.99906826), ('2', 14.99956226), ('3', 0.0)])
        OrderedDict([('1', 13.99954033), ('2', 13.99994469), ('3', 0.0)])
        OrderedDict([('1', 12.99962521), ('2', 12.99977207), ('3', 0.0)])
        OrderedDict([('1', 11.99876785), ('2', 11.99949837), ('3', 0.0)])
        OrderedDict([('1', 10.99907684), ('2', 10.99946785), ('3', 0.0)])
        OrderedDict([('1', 9.998705864), ('2', 10.00048923), ('3', 0.0)])
        OrderedDict([('1', 8.999074936), ('2', 8.999601364), ('3', 0.0)])

        >>> pidevice.MOV(pidevice.axes[:2],(45,45)) # max position in absoulte coordinates
        >>> pidevice.qPOS()
        OrderedDict([('1', 44.9998436), ('2', 44.9990654), ('3', 0.0)])

        >>> pidevice.MOV(pidevice.axes[:2],(0.1,0.1))
        >>> pidevice.qPOS()
        OrderedDict([('1', 7.110321045), ('2', 6.996693611), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.820139408), ('2', 6.710417747), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.773382664), ('2', 6.664360046), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.722932816), ('2', 6.614255905), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.693023682), ('2', 6.585497856), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.671704292), ('2', 6.562428474), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.649555206), ('2', 6.54163456), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.63082552), ('2', 6.522785187), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.617462158), ('2', 6.509446144), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.602602005), ('2', 6.494898796), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.591478825), ('2', 6.483504295), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.579800129), ('2', 6.471986771), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.56956768), ('2', 6.461724281), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.560307503), ('2', 6.452710152), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.550625801), ('2', 6.44343853), ('3', 0.0)])
        >>> pidevice.qPOS()
        OrderedDict([('1', 6.541518688), ('2', 6.434470177), ('3', 0.0)])
        >>> 