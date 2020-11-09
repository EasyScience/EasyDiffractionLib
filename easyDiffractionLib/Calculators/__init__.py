__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import sys

if 'darwin' in sys.platform:
    import libsDarwin
    libs_path = list(libsDarwin.__path__)[0]
elif 'linux' in sys.platform:
    import libsLinux
    libs_path = list(libsLinux.__path__)[0]
elif 'win32' in sys.platform:
    import libsWin32
    libs_path = list(libsWin32.__path__)[0]
else:
    raise NotImplementedError(f"Platform '{sys.platform}' is not supported")

sys.path.append(libs_path)
