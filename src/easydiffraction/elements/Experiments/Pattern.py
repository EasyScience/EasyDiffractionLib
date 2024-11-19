# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from typing import ClassVar
from typing import Optional
from typing import Union

from easyscience.Objects.ObjectClasses import BaseObj
from easyscience.Objects.ObjectClasses import Parameter

from easydiffraction.elements.Backgrounds.Background import BackgroundContainer


class Pattern1D(BaseObj):
    _name = 'Instrument'
    _defaults = {
        'zero_shift': {
            '@module': 'easyscience.Objects.Base',
            '@class': 'Parameter',
            '@version': '0.0.1',
            'name': 'zero_shift',
            'units': 'degree',
            'value': 0.0,
            'fixed': True
        },
        'scale':   {
            '@module':  'easyscience.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'scale',
            'value':    1,
            'fixed': True
        },
        'backgrounds': {
            '@module': 'easydiffraction.elements.Backgrounds.Background',
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

        return self.__class__(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)
