__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.ObjectClasses import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder
_decoder = MontyDecoder()


class PolarizedBeam(BaseObj):
    _name = 'polarized_beam'
    _defaults = {
        'polarization': {
            '@module': 'easyCore.Objects.Variable',
            '@class': 'Parameter',
            '@version': '0.0.1',
            'name': 'polarization',
            'value': 1.0,
            'min': 0.0,
            'max': 1.0,
            "fixed": True,
        },
        'efficiency':   {
            '@module':  'easyCore.Objects.Variable',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'efficiency',
            'value':    1.0,
            'min':      0.0,
            'max':      1.0,
            "fixed": True,
        },
    }

    def __init__(self, polarization: Parameter, efficiency: Parameter, interface=None):
        super().__init__(self._name, polarization=polarization, efficiency=efficiency)
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  polarization: float = _defaults['polarization']['value'],
                  efficiency: float = _defaults['efficiency']['value'],
                  interface=None):
        defaults = deepcopy(cls._defaults)
        defaults['polarization']['value'] = polarization
        polarization = _decoder.process_decoded(defaults['polarization'])
        defaults['efficiency']['value'] = efficiency
        efficiency = _decoder.process_decoded(defaults['efficiency'])
        return cls(polarization=polarization, efficiency=efficiency, interface=interface)

    @classmethod
    def default(cls, interface=None):
        return cls.from_pars(interface=interface)
