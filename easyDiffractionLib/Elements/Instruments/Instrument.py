__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Objects.Base import BaseObj
from easyCore.Utils.json import MontyDecoder

_decoder = MontyDecoder()


class Pattern(BaseObj):
    _name = 'instrument'
    _defaults = [
        {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'u_resolution',
            'value':    0.0002
        },
        {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'v_resolution',
            'value':    -0.0002
        },
        {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'w_resolution',
            'value':    0.012
        },
        {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'x_resolution',
            'value':    0.012
        },
        {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'wavelength',
            'units':    'angstrom',
            'value':    1.54056
        },
    ]

    def __init__(self, interface=None):
        super().__init__(self.__class__.__name__, *[_decoder.process_decoded(default) for default in self._defaults])
        self.name = self._name
        self.interface = interface

    def __repr__(self):
        return f'{self.__class__.__name__}: x_shift={self.zero_point}, ' \
               f'y_shift={self.background} '
