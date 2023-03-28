__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from copy import deepcopy
from typing import ClassVar, Optional, Union
from easyCore.Objects.ObjectClasses import BaseObj, Parameter
from easyDiffractionLib.elements.Backgrounds.Background import BackgroundContainer


class Pattern1D(BaseObj):
    _name = 'Instrument'
    _defaults = {
        'zero_shift': {
            '@module': 'easyCore.Objects.Base',
            '@class': 'Parameter',
            '@version': '0.0.1',
            'name': 'zero_shift',
            'units': 'degree',
            'value': 0.0,
            'fixed': True
        },
        'scale':   {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'scale',
            'value':    1,
            'fixed': True
        },
        'backgrounds': {
            '@module': 'easyDiffractionLib.elements.Backgrounds.Background',
            '@class': 'BackgroundContainer',
            '@version': '0.0.1',
            'data': [],
        }
    }

    zero_shift: ClassVar[Parameter]
    scale: ClassVar[Parameter]
    backgrounds: ClassVar[BackgroundContainer]

    def __init__(self,
                 zero_shift: Optional[Union[Parameter, float]] = None,
                 scale: Optional[Union[Parameter, float]] = None,
                 backgrounds: Optional[BackgroundContainer] = None,
                 interface=None):
        super().__init__(self.__class__.__name__,
                         zero_shift=Parameter.from_dict(self._defaults['zero_shift']),
                         scale=Parameter.from_dict(self._defaults['scale']),
                         backgrounds=BackgroundContainer())
        self.name = self._name
        self.interface = interface

        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)

