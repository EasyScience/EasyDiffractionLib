__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import Callable, List

from easyDiffractionLib.Interfaces import InterfaceTemplate
from easyCore.Objects.Inferface import InterfaceFactoryTemplate


class InterfaceFactory(InterfaceFactoryTemplate):
    def __init__(self, *args, **kwargs):
        super(InterfaceFactory, self).__init__(InterfaceTemplate._interfaces, *args, **kwargs)

    def get_hkl(self, x_array=None, idx=None, phase_name=None) -> dict:
        return self().get_hkl(x_array, idx=idx, phase_name=phase_name)

    def get_phase_components(self, phase_name):
        return self().get_phase_components(phase_name)

    def interface_compatability(self, check_str: str) -> List[str]:
        compatible_interfaces = []
        for interface in self._interfaces:
            if interface.feature_checker(test_str=check_str):
                compatible_interfaces.append(self.return_name(interface))
        return compatible_interfaces
