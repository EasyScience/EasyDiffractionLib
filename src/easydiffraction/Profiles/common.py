# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import os
import tempfile
from typing import TypeVar
from typing import Union

from easyscience.Datasets.xarray import xr
from easyscience.global_object.undo_redo import property_stack_deco
from easyscience.Objects.core import ComponentSerializer
from easyscience.Objects.ObjectClasses import BaseObj

from easydiffraction import Phase
from easydiffraction import Phases

DataClassBaseType = TypeVar('DataClassBaseType', bound='_DataClassBase')


class _DataClassBase:
    def __init__(self, dataset):
        self._dataset = dataset


class DataContainer(ComponentSerializer):
    def __init__(self, sim_store: DataClassBaseType, exp_store: DataClassBaseType):
        self._simulations = sim_store
        self._experiments = exp_store
        self.store = sim_store._dataset
        self._relations = {}
        self.coordinate_labels = []
        self.coordinate_units = []

    @classmethod
    def prepare(cls, dataset, simulation_class, experiment_class):
        class Simulation(simulation_class):
            def __init__(self):
                super(Simulation, self).__init__(dataset)

            def as_dict(self, skip=None):
                """
                :return: Json-able dictionary representation.
                """
                d = {'@module': self.__class__.__module__, '@class': self.__class__.__name__}
                d['simulations'] = self._dataset.as_dict()
                return d

        class Experiment(experiment_class):
            def __init__(self, sim_prefix):
                super(Experiment, self).__init__(dataset, sim_prefix)

            def as_dict(self, skip=None):
                """
                :return: Json-able dictionary representation.
                """
                d = {'@module': self.__class__.__module__, '@class': self.__class__.__name__}
                d['simulations'] = self._dataset.as_dict()
                return d

        s = Simulation()
        e = Experiment(s._simulation_prefix)

        return cls(s, e)

    def add_coordinate(self, coordinate_name, coordinate_values):
        self.store.easyscience.add_coordinate(coordinate_name, coordinate_values)

    def add_variable(self, variable_name, variable_coordinates, values):
        if variable_name in self.store.easyscience.variables:
            self.store.easyscience.remove_variable(variable_name)
        self.store.easyscience.add_variable(variable_name, variable_coordinates, values)

    def as_dict(self, skip=None):
        """
        :return: Json-able dictionary representation.
        """
        d = {'@module': self.__class__.__module__, '@class': self.__class__.__name__}
        d['simulations'] = self._simulations.as_dict()
        d['experiments'] = self._experiments.as_dict()
        return d

    @classmethod
    def from_dict(cls, d):
        """
        :param d: Dict representation.
        :return: Species.
        """
        return cls(d['simulations'], d['experiments'])


class JobSetup:
    def __init__(self, datastore_classes, instrumental_parameter_class, pattern_class):
        self.datastore_classes = datastore_classes
        self.instrumental_parameter_class = instrumental_parameter_class
        self.pattern_class = pattern_class


class _PowderBase(BaseObj):
    def __init__(
        self,
        name: str = '',
        job_type=None,
        datastore: xr.Dataset = None,
        phases: Union[Phase, Phases] = None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        if isinstance(phases, Phase):
            phases = Phases('Phases', phases)
        elif phases is None:
            phases = Phases('Phases')

        if not isinstance(phases, Phases):
            raise AttributeError('`phases` must be a Crystal or Crystals')

        if parameters is None:
            parameters = job_type.pattern_class()

        if pattern is None:
            pattern = job_type.instrumental_parameter_class()

        super(_PowderBase, self).__init__(name, _phases=phases, _parameters=parameters, _pattern=pattern)

        from easydiffraction.calculators.wrapper_types import Neutron
        from easydiffraction.calculators.wrapper_types import Powder
        from easydiffraction.Profiles.P1D import Instrument1DCWParameters
        from easydiffraction.Profiles.P1D import Instrument1DTOFParameters
        from easydiffraction.Profiles.P1D import PolPowder1DParameters as Pattern1D_Pol
        from easydiffraction.Profiles.P1D import Powder1DParameters as Pattern1D

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

        self.__constituting_classes = job_type
        self.__dataset = datastore
        self.datastore = DataContainer.prepare(self.__dataset, *job_type.datastore_classes)

        self.filename = os.path.join(tempfile.gettempdir(), 'easydiffraction_temp.cif')
        self.output_index = None
        self.interface = interface

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)

    def remove_background(self, background):
        if background.linked_experiment.raw_value in self._pattern.backgrounds.linked_experiments:
            del self._pattern.backgrounds[background.linked_experiment.raw_value]
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
            value = Phases('Phases', value)
        if not isinstance(value, Phases):
            raise ValueError
        self._phases = value
        self._global_object.map.add_edge(self, value)
        self._phases.interface = self.interface

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    @property_stack_deco
    def parameters(self, value):
        self._parameters = value
        self._parameters.interface = self._interface

    @property
    def pattern(self):
        return self._pattern

    def as_dict(self, skip: list = []) -> dict:
        this_dict = super(_PowderBase, self).as_dict(skip=skip)
        return this_dict

    def _update_bases(self, new_base):
        base_class = getattr(self, '__old_class__', self.__class__)
        old_bases = set(self.__class__.__bases__)
        old_bases = old_bases - {
            base_class,
            *new_base.__mro__,
        }  # This should fix multiple inheritance
        self.__class__.__bases__ = (new_base, *old_bases, base_class)
