# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import os
import tempfile
from typing import ClassVar
from typing import Union

from cryspy.A_functions_base.function_2_space_group import get_default_it_coordinate_system_code_by_it_number
from easycrystallography.Structures.Phase import Phases as ecPhases
from easyscience.Datasets.xarray import xr
from easyscience.global_object.undo_redo import property_stack_deco
from easyscience.Objects.ObjectClasses import BaseObj

from easydiffraction.calculators.wrapper_factory import WrapperFactory
from easydiffraction.calculators.wrapper_types import Neutron
from easydiffraction.calculators.wrapper_types import Powder
from easydiffraction.job.experiment.pd_1d import Instrument1DCWParameters
from easydiffraction.job.experiment.pd_1d import Instrument1DTOFParameters
from easydiffraction.job.experiment.pd_1d import PolPowder1DParameters as Pattern1D_Pol
from easydiffraction.job.experiment.pd_1d import Powder1DParameters as Pattern1D
from easydiffraction.job.model.phase import Phase
from easydiffraction.job.model.phase import Phases


class Sample(BaseObj):
    _REDIRECT = {
        'phases': lambda obj: getattr(obj, '_phases'),
        'parameters': lambda obj: getattr(obj, '_parameters'),
        'pattern': lambda obj: getattr(obj, '_pattern'),
    }

    _phases: ClassVar[Phases]
    _parameters: ClassVar
    _pattern: ClassVar

    def __init__(
        self,
        dataset: Union[xr.Dataset, None] = None,
        phases: Union[Phase, Phases] = None,
        parameters=None,
        pattern=None,
        interface=None,
        name: str = 'easySample',
    ):
        if isinstance(phases, Phase):
            phases = Phases('Phases', phases)
        elif phases is None:
            phases = Phases('Phases')
        elif isinstance(phases, Phases):
            pass
        elif isinstance(phases, list):
            phases = Phases('Phases', phases[0])
        elif isinstance(phases, ecPhases):
            if len(phases) > 0:
                phases = Phases('Phases', phases[0])
        else:
            raise AttributeError('`phases` must be a Crystal or Crystals')

        self._simulation_prefix = 'sim_'
        if dataset is not None:
            self._dataset = dataset
        else:
            self._dataset = xr.Dataset()

        if parameters is None:
            parameters = Instrument1DCWParameters()

        if pattern is None:
            pattern = Pattern1D()

        super(Sample, self).__init__(name, _phases=phases, _parameters=parameters, _pattern=pattern)

        # Set bases for easy identification
        self._update_bases(Powder)
        self._update_bases(Neutron)

        if getattr(pattern, '__old_class__', pattern.__class__) == Pattern1D:
            from easydiffraction.calculators.wrapper_types import UPol

            self._update_bases(UPol)

        elif getattr(pattern, '__old_class__', pattern.__class__) == Pattern1D_Pol:
            from easydiffraction.calculators.wrapper_types import Pol

            self._update_bases(Pol)

        if isinstance(parameters, Instrument1DCWParameters):
            from easydiffraction.calculators.wrapper_types import CW

            self._update_bases(CW)

        elif isinstance(parameters, Instrument1DTOFParameters):
            from easydiffraction.calculators.wrapper_types import TOF

            self._update_bases(TOF)

        self.filename = os.path.join(tempfile.gettempdir(), 'easydiffraction_temp.cif')
        # print(f"Temp CIF: {self.filename}")
        self.output_index = None
        if interface is not None:
            self.interface = interface
        else:
            self.interface = WrapperFactory()

    def add_phase_from_cif(self, cif_file):
        cif_string = ''
        with open(cif_file, 'r') as f:
            cif_string = f.read()
        self.add_phase_from_string(cif_string)

    def add_phase_from_string(self, cif_string):
        phase = Phase.from_cif_string(cif_string)
        # update the settings
        if phase[0].space_group.setting is None:
            group_number = phase[0].space_group.int_number
            default_setting = get_default_it_coordinate_system_code_by_it_number(group_number)
            phase[0].space_group.setting = default_setting
        fixed_cif = phase.cif
        if self._interface is not None:
            self._interface.updateModelCif(fixed_cif)
        for p in phase:
            self.phases.append(p)

    def phases_as_cif(self):
        """
        Returns a CIF representation of the phases names and scales.
        """
        cif_phase = 'loop_\n'
        cif_phase += '_phase_label\n'
        cif_phase += '_phase_scale\n'
        cif_phase += '_phase_igsize\n'
        for phase in self.phases:
            cif_phase += phase.name + ' ' + str(phase.scale.value) + ' 0.0\n'
        return cif_phase

    @property
    def cif(self):
        """
        Returns a CIF representation of the sample.
        """
        return self.phases_as_cif()

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, value):
        self._interface = value
        # This is required so that the type is correctly passes.
        if value is not None:
            self.interface.generate_bindings(self)
            self.generate_bindings()

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)

    def remove_background(self, background):
        if background.linked_experiment.value in self._pattern.backgrounds.linked_experiments:
            del self._pattern.backgrounds[background.linked_experiment.value]
        else:
            raise ValueError

    @property
    def backgrounds(self):
        return self._pattern.backgrounds

    @property
    def phases(self):
        return self._phases

    @phases.setter
    @property_stack_deco
    def phases(self, value):
        if isinstance(value, Phase):
            self._phases.append(value)
        elif isinstance(value, Phases):
            self._phases = value
            self._global_object.map.add_edge(self, value)
            self._phases.interface = self.interface
        else:
            raise ValueError

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    @property_stack_deco
    def parameters(self, value):
        if not isinstance(value, (Instrument1DCWParameters, Instrument1DTOFParameters)):
            raise ValueError
        if isinstance(value, Instrument1DTOFParameters):
            from easydiffraction.calculators.wrapper_types import TOF

            self._update_bases(TOF)
        else:
            from easydiffraction.calculators.wrapper_types import CW

            self._update_bases(CW)
        self._parameters = value
        self._parameters.interface = self._interface

    @property
    def pattern(self):
        return self._pattern

    def _update_bases(self, new_base):
        base_class = getattr(self, '__old_class__', self.__class__)
        old_bases = set(self.__class__.__bases__)
        old_bases = old_bases - {
            base_class,
            *new_base.__mro__,
        }  # This should fix multiple inheritance
        self.__class__.__bases__ = (new_base, *old_bases, base_class)
