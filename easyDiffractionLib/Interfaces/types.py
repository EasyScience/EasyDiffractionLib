__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from abc import abstractmethod
from typing import List, Any, Callable, Union


class _Type:
    _internal_type = True
    calculator: Any
    _identify: Callable[[Any], Union[str, int]]

    @abstractmethod
    def create(self, model) -> List:
        pass


class Neutron(_Type):
    pass


class XRay(_Type):
    pass


class Powder(_Type):
    pass


class SingleCrystal(_Type):
    pass


class CW(_Type):
    pass


class TOF(_Type):
    pass


class Pol(_Type):
    pass


class UPol(_Type):
    pass
