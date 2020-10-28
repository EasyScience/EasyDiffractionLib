__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import os, sys

try:
    from easyDiffractionLib.Interfaces.cryspy import Cryspy  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('CrysPy is not installed')

from easyDiffractionLib.Interfaces.CFML import CFML  # noqa: F401

try:
    from easyDiffractionLib.Interfaces.CFML import CFML  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('CFML is not installed')

try:
    import GSASII
    sys.path.insert(0, GSASII.__path__[0])
    if 'darwin' in sys.platform:
        import libsDarwin
        sys.path.insert(0, os.path.join(libsDarwin.__path__[0], "GSASII"))
    elif 'linux' in sys.platform:
        import libsLinux
        sys.path.insert(0, os.path.join(libsLinux.__path__[0], "GSASII"))
    elif 'win32' in sys.platform:
        import libsWin32
        sys.path.insert(0, os.path.join(libsWin32.__path__[0], "GSASII"))
    from easyDiffractionLib.Interfaces.GSASII import GSASII  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('GSAS-II is not installed')

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
