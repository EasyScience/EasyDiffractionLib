__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.Base import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder

_decoder = MontyDecoder()


class Pattern(BaseObj):
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
        'wavelength':   {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'wavelength',
            'units':    'angstrom',
            'value':    1.54056,
            'fixed': True
        },
        'u_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_u',
            'value':    0.0002,
            'fixed': True
        },
        'v_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_v',
            'value':    -0.0002,
            'fixed': True

        },
        'w_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_w',
            'value':    0.012,
            'fixed': True

        },
        'x_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_x',
            'value':    0.0,
            'fixed': True
        },
        'y_resolution': {
            '@module': 'easyCore.Objects.Base',
            '@class': 'Parameter',
            '@version': '0.0.1',
            'name': 'resolution_y',
            'value': 0.0,
            'fixed': True
        }
    }

    def __init__(self,
                 zero_shift: Parameter, wavelength: Parameter,
                 u_resolution: Parameter, v_resolution: Parameter, w_resolution: Parameter,
                 x_resolution: Parameter, y_resolution: Parameter,
                 interface=None):
        super().__init__(self.__class__.__name__,
                         zero_shift=zero_shift, wavelength=wavelength,
                         u_resolution=u_resolution, v_resolution=v_resolution, w_resolution=w_resolution,
                         x_resolution=x_resolution, y_resolution=y_resolution)
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  zero_shift: float = _defaults['zero_shift']['value'],
                  wavelength: float = _defaults['wavelength']['value'],
                  u_resolution: float = _defaults['u_resolution']['value'],
                  v_resolution: float = _defaults['v_resolution']['value'],
                  w_resolution: float = _defaults['w_resolution']['value'],
                  x_resolution: float = _defaults['x_resolution']['value'],
                  y_resolution: float = _defaults['y_resolution']['value']
                  ):
        defaults = deepcopy(cls._defaults)
        defaults['zero_shift']['value'] = zero_shift
        zero_shift = _decoder.process_decoded(defaults['zero_shift'])
        defaults['wavelength']['value'] = wavelength
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        defaults['u_resolution']['value'] = u_resolution
        u_resolution = _decoder.process_decoded(defaults['u_resolution'])
        defaults['v_resolution']['value'] = v_resolution
        v_resolution = _decoder.process_decoded(defaults['v_resolution'])
        defaults['w_resolution']['value'] = w_resolution
        w_resolution = _decoder.process_decoded(defaults['w_resolution'])
        defaults['x_resolution']['value'] = x_resolution
        x_resolution = _decoder.process_decoded(defaults['x_resolution'])
        defaults['y_resolution']['value'] = y_resolution
        y_resolution = _decoder.process_decoded(defaults['y_resolution'])
        return cls(zero_shift=zero_shift, wavelength=wavelength,
                   u_resolution=u_resolution, v_resolution=v_resolution, w_resolution=w_resolution,
                   x_resolution=x_resolution, y_resolution=y_resolution)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        zero_shift = _decoder.process_decoded(defaults['zero_shift'])
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        u_resolution = _decoder.process_decoded(defaults['u_resolution'])
        v_resolution = _decoder.process_decoded(defaults['v_resolution'])
        w_resolution = _decoder.process_decoded(defaults['w_resolution'])
        x_resolution = _decoder.process_decoded(defaults['x_resolution'])
        y_resolution = _decoder.process_decoded(defaults['y_resolution'])
        return cls(zero_shift=zero_shift, wavelength=wavelength,
                   u_resolution=u_resolution, v_resolution=v_resolution, w_resolution=w_resolution,
                   x_resolution=x_resolution, y_resolution=y_resolution)
