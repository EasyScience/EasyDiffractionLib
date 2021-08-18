__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import Callable

from easyDiffractionLib.Interfaces import InterfaceTemplate
from easyCore.Objects.Inferface import InterfaceFactoryTemplate


class InterfaceFactory(InterfaceFactoryTemplate):
    def __init__(self):
        super(InterfaceFactory, self).__init__(InterfaceTemplate._interfaces)

    def get_hkl(self, x_array=None) -> dict:
        return self().get_hkl(x_array)
