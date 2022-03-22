__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.Base import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder
from easyDiffractionLib.elements.Backgrounds.Background import BackgroundContainer
_decoder = MontyDecoder()


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

    def __init__(self,
                 zero_shift: Parameter, scale: Parameter,
                 backgrounds: BackgroundContainer,
                 interface=None):
        super().__init__(self.__class__.__name__,
                         zero_shift=zero_shift, scale=scale,
                         backgrounds=backgrounds)
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  zero_shift: float = _defaults['zero_shift']['value'],
                  scale: float = _defaults['scale']['value']
                  ):
        defaults = deepcopy(cls._defaults)
        defaults['zero_shift']['value'] = zero_shift
        zero_shift = _decoder.process_decoded(defaults['zero_shift'])
        defaults['scale']['value'] = scale
        scale = _decoder.process_decoded(defaults['scale'])
        backgrounds = BackgroundContainer()
        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        zero_shift = _decoder.process_decoded(defaults['zero_shift'])
        scale = _decoder.process_decoded(defaults['scale'])
        backgrounds = BackgroundContainer()

        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)

