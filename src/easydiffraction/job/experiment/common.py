# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from typing import TypeVar

from easyscience.Objects.core import ComponentSerializer

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
