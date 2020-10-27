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
    print('CrysPy is not installed')

try:
    import GSASII
    sys.path.insert(0, GSASII.__path__[0])
    if 'darwin' in platform:
        import somacos
        sys.path.insert(0, os.path.join(somacos.__path__[0], "GSASII"))
    elif 'linux' in platform:
        import solinux
        sys.path.insert(0, os.path.join(solinux.__path__[0], "GSASII"))
    elif 'win32' in platform:
        import sowindows
        sys.path.insert(0, os.path.join(sowindows.__path__[0], "GSASII"))
    from easyDiffractionLib.Interfaces.GSASII import GSASII  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('GSAS-II is not installed')

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
