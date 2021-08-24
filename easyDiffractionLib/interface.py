__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import Callable, List

from easyDiffractionLib.Interfaces import InterfaceTemplate
from easyCore.Objects.Inferface import InterfaceFactoryTemplate


class InterfaceFactory(InterfaceFactoryTemplate):
    def __init__(self):
        super(InterfaceFactory, self).__init__(InterfaceTemplate._interfaces)

    def get_hkl(self, x_array=None, idx=None) -> dict:
        return self().get_hkl(x_array)

    def interface_compatability(self, check_str: str) -> List[str]:
        compatible_interfaces = []
        for interface in self._interfaces:
            if interface.feature_checker(test_str=check_str):
                compatible_interfaces.append(self.return_name(interface))
        return compatible_interfaces
