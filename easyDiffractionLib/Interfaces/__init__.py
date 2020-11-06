__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import os, sys
import traceback


try:
    from easyDiffractionLib.Interfaces.cryspy import Cryspy  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('Warning: CrysPy is not installed')

try:
    from easyDiffractionLib.Interfaces.CFML import CFML
except Exception:
    traceback.print_exc()
    print('Warning: CFML is not installed')
    
try:
    import GSASII
    gsasii_path = list(GSASII.__path__)[0]
    sys.path.insert(0, gsasii_path)
    if 'darwin' in sys.platform:
        import libsDarwin
        libs_path = list(libsDarwin.__path__)[0]
    elif 'linux' in sys.platform:
        import libsLinux
        libs_path = list(libsLinux.__path__)[0]
    elif 'win32' in sys.platform:
        import libsWin32
        libs_path = list(libsWin32.__path__)[0]
    sys.path.insert(0, os.path.join(libs_path, "GSASII"))
    from easyDiffractionLib.Interfaces.GSASII import GSASII  # noqa: F401
except Exception:
    traceback.print_exc()    
    print('Warning: GSAS-II is not installed')

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
