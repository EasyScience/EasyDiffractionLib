__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import os, sys
import traceback


try:
    from easyDiffractionLib.Interfaces.cryspy import Cryspy  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('Warning: CrysPy is not installed')


# try:
#     from easyDiffractionLib.Interfaces.cryspyV2 import CryspyBase  # noqa: F401
# except ImportError:
#     # TODO make this a proper message (use logging?)
#     print('Warning: CrysPy is not installed')

try:
    from easyDiffractionLib.Interfaces.CFML import CFML  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('Warning: CrysFML is not installed')

try:
    from easyDiffractionLib.Interfaces.GSASII import GSASII  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('Warning: GSAS-2 is not installed')


from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
