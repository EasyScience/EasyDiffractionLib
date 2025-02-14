# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Optional
from typing import Union

from easyscience.Objects.ObjectClasses import BaseObj
from easyscience.Objects.variable import Parameter

if TYPE_CHECKING:
    from easyscience.Objects.Inferface import iF


class PolarizedBeam(BaseObj):
    _name = 'polarized_beam'
    _defaults = {
        'polarization': {
            'name': 'polarization',
            'value': 1.0,
            'min': 0.0,
            'max': 1.0,
            'fixed': True,
        },
        'efficiency': {
            'name': 'efficiency',
            'value': 1.0,
            'min': 0.0,
            'max': 1.0,
            'fixed': True,
        },
    }

    polarization: ClassVar[Parameter]
    efficiency: ClassVar[Parameter]

    def __init__(
        self,
        polarization: Optional[Union[Parameter, float]] = None,
        efficiency: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
    ):
        super().__init__(
            self._name,
            polarization=Parameter(**self._defaults['polarization']),
            efficiency=Parameter(**self._defaults['efficiency']),
        )
        if polarization is not None:
            self.polarization = polarization
        if efficiency is not None:
            self.efficiency = efficiency
        self.interface = interface
