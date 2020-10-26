__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import os, sys

try:
    from easyDiffractionLib.Interfaces.CFML import CFML  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('CFML is not installed')
try:
    from easyDiffractionLib.Interfaces.cryspy import Cryspy  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('Cryspy is not installed')
try:
    #sys.path.insert(0, os.path.expanduser("~/gsas2full/GSASII/"))
    from easyDiffractionLib.Interfaces.GSASII import GSASII  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('GSASII is not installed')

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
