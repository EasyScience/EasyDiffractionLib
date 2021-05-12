__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import os, sys
import traceback


try:
    from easyDiffractionLib.Interfaces.cryspy import Cryspy  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('Warning: CrysPy is not installed')

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
