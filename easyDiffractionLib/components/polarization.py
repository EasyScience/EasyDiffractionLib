__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.ObjectClasses import BaseObj, Parameter


class PolarizedBeam(BaseObj):
    def __init__(self, polarization: Parameter, efficiency: Parameter, interface=None):
        super().__init__('polarized_beam', polarization=polarization, efficiency=efficiency, interface=interface)

    @classmethod
    def from_pars(cls, polarization: float = 1.0, efficiency: float = 1.0):
        return cls(polarization=Parameter('polarization', polarization, min=0., max=1.),
                   efficiency=Parameter('efficency', efficiency, min=0., max=1.)
                   )
