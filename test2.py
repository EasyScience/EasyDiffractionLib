__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


from easyDiffractionLib.sample import Sample
from easyDiffractionLib.interface import InterfaceFactory

s = Sample()
interface = InterfaceFactory()
interface.switch('CrysPyV2')
s.interface = interface