__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

try:
    from easyDiffractionLib.Interfaces.CFML import CFML  # noqa: F401
except ImportError:
    # TODO make this a proper message (use logging?)
    print('CFML is not installed')

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
