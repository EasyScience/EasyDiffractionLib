__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.Base import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder

_decoder = MontyDecoder()


class Pattern(BaseObj):
    _name = 'Instrument'
    _defaults = {
        'u_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'u_resolution',
            'value':    0.0002,
            'fixed': True
        },
        'v_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'v_resolution',
            'value':    -0.0002,
            'fixed': True

        },
        'w_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'w_resolution',
            'value':    0.012,
            'fixed': True

        },
        'x_resolution': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'x_resolution',
            'value':    0.012,
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

        }
    }

    def __init__(self,
                 u_resolution: Parameter, v_resolution: Parameter, w_resolution: Parameter, x_resolution: Parameter,
                 wavelength: Parameter, interface=None):
        super().__init__(self.__class__.__name__,
                         u_resolution=u_resolution, v_resolution=v_resolution,
                         w_resolution=w_resolution, x_resolution=x_resolution, wavelength=wavelength)
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  u_resolution: float = _defaults['u_resolution']['value'],
                  v_resolution: float = _defaults['v_resolution']['value'],
                  w_resolution: float = _defaults['w_resolution']['value'],
                  x_resolution: float = _defaults['x_resolution']['value'],
                  wavelength: float = _defaults['wavelength']['value']):
        defaults = deepcopy(cls._defaults)
        defaults['u_resolution']['value'] = u_resolution
        u_resolution = _decoder.process_decoded(defaults['u_resolution'])
        defaults['v_resolution']['value'] = v_resolution
        v_resolution = _decoder.process_decoded(defaults['v_resolution'])
        defaults['w_resolution']['value'] = w_resolution
        w_resolution = _decoder.process_decoded(defaults['w_resolution'])
        defaults['x_resolution']['value'] = x_resolution
        x_resolution = _decoder.process_decoded(defaults['x_resolution'])
        defaults['wavelength']['value'] = wavelength
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        return cls(u_resolution=u_resolution, v_resolution=v_resolution,
                   w_resolution=w_resolution, x_resolution=x_resolution, wavelength=wavelength)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        u_resolution = _decoder.process_decoded(defaults['u_resolution'])
        v_resolution = _decoder.process_decoded(defaults['v_resolution'])
        w_resolution = _decoder.process_decoded(defaults['w_resolution'])
        x_resolution = _decoder.process_decoded(defaults['x_resolution'])
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        return cls(u_resolution=u_resolution, v_resolution=v_resolution,
                   w_resolution=w_resolution, x_resolution=x_resolution, wavelength=wavelength)
