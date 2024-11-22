# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from copy import deepcopy

from easyscience.Objects.ObjectClasses import BaseObj
from easyscience.Objects.ObjectClasses import Parameter
from easyscience.Utils.json import MontyDecoder

_decoder = MontyDecoder()


class Pars1D(BaseObj):
    _name = 'Instrument'
    _defaults = {
        'wavelength': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'wavelength',
            'units': 'angstrom',
            'value': 1.54056,
            'fixed': True,
            'min': 0,
        },
        'resolution_u': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'resolution_u',
            'value': 0.0002,
            'fixed': True,
        },
        'resolution_v': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'resolution_v',
            'value': -0.0002,
            'fixed': True,
        },
        'resolution_w': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'resolution_w',
            'value': 0.012,
            'fixed': True,
        },
        'resolution_x': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'resolution_x',
            'value': 0.0,
            'fixed': True,
        },
        'resolution_y': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'resolution_y',
            'value': 0.0,
            'fixed': True,
        },
        'reflex_asymmetry_p1': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'reflex_asymmetry_p1',
            'value': 0.0,
            'fixed': True,
        },
        'reflex_asymmetry_p2': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'reflex_asymmetry_p2',
            'value': 0.0,
            'fixed': True,
        },
        'reflex_asymmetry_p3': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'reflex_asymmetry_p3',
            'value': 0.0,
            'fixed': True,
        },
        'reflex_asymmetry_p4': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            'name': 'reflex_asymmetry_p4',
            'value': 0.0,
            'fixed': True,
        },
    }

    def __init__(
        self,
        wavelength: Parameter,
        resolution_u: Parameter,
        resolution_v: Parameter,
        resolution_w: Parameter,
        resolution_x: Parameter,
        resolution_y: Parameter,
        reflex_asymmetry_p1: Parameter,
        reflex_asymmetry_p2: Parameter,
        reflex_asymmetry_p3: Parameter,
        reflex_asymmetry_p4: Parameter,
        interface=None,
    ):
        super().__init__(
            self.__class__.__name__,
            wavelength=wavelength,
            resolution_u=resolution_u,
            resolution_v=resolution_v,
            resolution_w=resolution_w,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            reflex_asymmetry_p1=reflex_asymmetry_p1,
            reflex_asymmetry_p2=reflex_asymmetry_p2,
            reflex_asymmetry_p3=reflex_asymmetry_p3,
            reflex_asymmetry_p4=reflex_asymmetry_p4,
        )
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(
        cls,
        wavelength: float = _defaults['wavelength']['value'],
        resolution_u: float = _defaults['resolution_u']['value'],
        resolution_v: float = _defaults['resolution_v']['value'],
        resolution_w: float = _defaults['resolution_w']['value'],
        resolution_x: float = _defaults['resolution_x']['value'],
        resolution_y: float = _defaults['resolution_y']['value'],
        reflex_asymmetry_p1: float = _defaults['reflex_asymmetry_p1']['value'],
        reflex_asymmetry_p2: float = _defaults['reflex_asymmetry_p2']['value'],
        reflex_asymmetry_p3: float = _defaults['reflex_asymmetry_p3']['value'],
        reflex_asymmetry_p4: float = _defaults['reflex_asymmetry_p4']['value'],
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
        defaults['reflex_asymmetry_p1']['value'] = reflex_asymmetry_p1
        reflex_asymmetry_p1 = _decoder.process_decoded(defaults['reflex_asymmetry_p1'])
        defaults['reflex_asymmetry_p2']['value'] = reflex_asymmetry_p2
        reflex_asymmetry_p2 = _decoder.process_decoded(defaults['reflex_asymmetry_p2'])
        defaults['reflex_asymmetry_p3']['value'] = reflex_asymmetry_p3
        reflex_asymmetry_p3 = _decoder.process_decoded(defaults['reflex_asymmetry_p3'])
        defaults['reflex_asymmetry_p4']['value'] = reflex_asymmetry_p4
        reflex_asymmetry_p4 = _decoder.process_decoded(defaults['reflex_asymmetry_p4'])
        return cls(
            wavelength=wavelength,
            resolution_u=resolution_u,
            resolution_v=resolution_v,
            resolution_w=resolution_w,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            reflex_asymmetry_p1=reflex_asymmetry_p1,
            reflex_asymmetry_p2=reflex_asymmetry_p2,
            reflex_asymmetry_p3=reflex_asymmetry_p3,
            reflex_asymmetry_p4=reflex_asymmetry_p4,
        )

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        resolution_u = _decoder.process_decoded(defaults['resolution_u'])
        resolution_v = _decoder.process_decoded(defaults['resolution_v'])
        resolution_w = _decoder.process_decoded(defaults['resolution_w'])
        resolution_x = _decoder.process_decoded(defaults['resolution_x'])
        resolution_y = _decoder.process_decoded(defaults['resolution_y'])
        reflex_asymmetry_p1 = _decoder.process_decoded(defaults['reflex_asymmetry_p1'])
        reflex_asymmetry_p2 = _decoder.process_decoded(defaults['reflex_asymmetry_p2'])
        reflex_asymmetry_p3 = _decoder.process_decoded(defaults['reflex_asymmetry_p3'])
        reflex_asymmetry_p4 = _decoder.process_decoded(defaults['reflex_asymmetry_p4'])
        return cls(
            wavelength=wavelength,
            resolution_u=resolution_u,
            resolution_v=resolution_v,
            resolution_w=resolution_w,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            reflex_asymmetry_p1=reflex_asymmetry_p1,
            reflex_asymmetry_p2=reflex_asymmetry_p2,
            reflex_asymmetry_p3=reflex_asymmetry_p3,
            reflex_asymmetry_p4=reflex_asymmetry_p4,
        )
