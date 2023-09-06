#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Install the PIPython library."""
# Unnecessary parens after u'print' keyword pylint: disable=C0325

import os
import sys
from setuptools import setup
import pathlib

__version__ = '2.10.0.2'
__signature__ = 0x2c3f0c145b8126ab88ec8ba6e27e3b8

here = pathlib.Path(__file__).parent.resolve()

try:
    # Redefining built-in 'input' pylint: disable=W0622
    # Invalid constant name "input" pylint: disable=C0103
    input = raw_input
except NameError:
    pass


def setwinreg():
    """Write __version__ to windows registry for the PI UpdateFinder."""
    if sys.platform not in ('win32', 'cygwin'):
        return
    try:
        import winreg  # Python 3
    except ImportError:
        import _winreg as winreg  # Python 2
    print('Updating Windows registry...')
    if 'PROCESSOR_ARCHITEW6432' in os.environ:
        key = r'SOFTWARE\Wow6432Node\PI\PIPython'
    else:
        key = r'SOFTWARE\PI\PIPython'
    reghandle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    keyhandle = winreg.CreateKey(reghandle, key)
    winreg.SetValueEx(keyhandle, 'KeyValue', None, winreg.REG_SZ, 'PIPython')
    winreg.SetValueEx(keyhandle, 'Version', None, winreg.REG_SZ, __version__)
    winreg.SetValueEx(keyhandle, 'Path', None, winreg.REG_SZ, sys.prefix)
    winreg.CloseKey(keyhandle)
    winreg.CloseKey(reghandle)


if __name__ == '__main__':
    try:
        setwinreg()
    except:  # exception can be different, No exception type(s) specified pylint: disable=W0702
        print("\nWARNING: It's recommended to run this setup with administrator permissions.")
        print('You can install PIPython with user permissions but then PIUpdateFinder will')
        print('not notify you about updates.\n')
        input('Press ENTER to install PIPython with user permissions or CTRL+C to cancel...')
    setup(name='PIPython',
          version=__version__,
          long_description_content_type='text/markdown',
          python_requires='>=3.6',
          package_data={
              'pipython.pidevice.gcs30': ['CustomError.json'],
          },
          zip_safe=False)
