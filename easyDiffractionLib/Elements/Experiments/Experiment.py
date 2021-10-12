__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.Base import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder

_decoder = MontyDecoder()


class Pars1D(BaseObj):
    _name = 'Instrument'
    _defaults = {
        'wavelength':   {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            'name':     'wavelength',
            'units':    'angstrom',
            'value':    1.54056,
            'fixed': True,
            'min': 0
        },
        'resolution_u': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            'name':     'resolution_u',
            'value':    0.0002,
            'fixed': True
        },
        'resolution_v': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            'name':     'resolution_v',
            'value':    -0.0002,
            'fixed': True

        },
        'resolution_w': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            'name':     'resolution_w',
            'value':    0.012,
            'fixed': True

        },
        'resolution_x': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            'name':     'resolution_x',
            'value':    0.0,
            'fixed': True
        },
        'resolution_y': {
            '@module': 'easyCore.Objects.Base',
            '@class': 'Parameter',
            'name': 'resolution_y',
            'value': 0.0,
            'fixed': True
        }
    }

    def __init__(self,
                 wavelength: Parameter,
                 resolution_u: Parameter, resolution_v: Parameter, resolution_w: Parameter,
                 resolution_x: Parameter, resolution_y: Parameter,
                 interface=None):
        super().__init__(self.__class__.__name__,
                         wavelength=wavelength,
                         resolution_u=resolution_u, resolution_v=resolution_v, resolution_w=resolution_w,
                         resolution_x=resolution_x, resolution_y=resolution_y)
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  wavelength: float = _defaults['wavelength']['value'],
                  resolution_u: float = _defaults['resolution_u']['value'],
                  resolution_v: float = _defaults['resolution_v']['value'],
                  resolution_w: float = _defaults['resolution_w']['value'],
                  resolution_x: float = _defaults['resolution_x']['value'],
                  resolution_y: float = _defaults['resolution_y']['value']
                  ):
        defaults = deepcopy(cls._defaults)
        defaults['wavelength']['value'] = wavelength
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        defaults['resolution_u']['value'] = resolution_u
        resolution_u = _decoder.process_decoded(defaults['resolution_u'])
        defaults['resolution_v']['value'] = resolution_v
        resolution_v = _decoder.process_decoded(defaults['resolution_v'])
        defaults['resolution_w']['value'] = resolution_w
        resolution_w = _decoder.process_decoded(defaults['resolution_w'])
        defaults['resolution_x']['value'] = resolution_x
        resolution_x = _decoder.process_decoded(defaults['resolution_x'])
        defaults['resolution_y']['value'] = resolution_y
        resolution_y = _decoder.process_decoded(defaults['resolution_y'])
        return cls(wavelength=wavelength,
                   resolution_u=resolution_u, resolution_v=resolution_v, resolution_w=resolution_w,
                   resolution_x=resolution_x, resolution_y=resolution_y)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        resolution_u = _decoder.process_decoded(defaults['resolution_u'])
        resolution_v = _decoder.process_decoded(defaults['resolution_v'])
        resolution_w = _decoder.process_decoded(defaults['resolution_w'])
        resolution_x = _decoder.process_decoded(defaults['resolution_x'])
        resolution_y = _decoder.process_decoded(defaults['resolution_y'])
        return cls(wavelength=wavelength,
                   resolution_u=resolution_u, resolution_v=resolution_v, resolution_w=resolution_w,
                   resolution_x=resolution_x, resolution_y=resolution_y)
