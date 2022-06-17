from __future__ import annotations
__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from typing import ClassVar, Union, Optional, TYPE_CHECKING

from easyCore.Objects.ObjectClasses import BaseObj, Parameter


if TYPE_CHECKING:
    from easyCore.Utils.typing import iF


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

    polarization: ClassVar[Parameter]
    efficiency: ClassVar[Parameter]

    def __init__(self,
                 polarization: Optional[Union[Parameter, float]] = None,
                 efficiency: Optional[Union[Parameter, float]] = None,
                 interface: Optional[iF] = None):
        super().__init__(self._name,
                         polarization=Parameter.from_dict(self._defaults['polarization']),
                         efficiency=Parameter.from_dict(self._defaults['efficiency'])
                         )
        if polarization is not None:
            self.polarization = polarization
        if efficiency is not None:
            self.efficiency = efficiency
        self.interface = interface
