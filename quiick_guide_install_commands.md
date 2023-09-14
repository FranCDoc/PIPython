### PI Python install procedure

    Unzip PI_drivers folder in a PC / laptop with Linux OS.

    ~/PI_drivers/Linux/PI_E727-1.3.0.0-INSTALL/PI_E727$ sudo chmod +x INSTALL 
    
    ~/PI_drivers/Linux/PI_E727-1.3.0.0-INSTALL/PI_E727$ sudo ./INSTALL

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

### PI API (controller.py in samples folder)





    