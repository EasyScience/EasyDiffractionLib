__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os
import tempfile
from typing import Union, TypeVar

from easyCore.Utils.UndoRedo import property_stack_deco
from easyCore.Objects.ObjectClasses import BaseObj
from easyDiffractionLib import Phases, Phase
from easyCore.Datasets.xarray import xr
from easyCore.Objects.core import ComponentSerializer


DataClassBaseType = TypeVar("DataClassBaseType", bound="_DataClassBase")


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
                d = {"@module": self.__class__.__module__,
                    "@class": self.__class__.__name__}
                d["simulations"] = self._dataset.as_dict()
                return d

        class Experiment(experiment_class):
            def __init__(self, sim_prefix):
                super(Experiment, self).__init__(dataset, sim_prefix)
            def as_dict(self, skip=None):
                """
                :return: Json-able dictionary representation.
                """
                d = {"@module": self.__class__.__module__,
                    "@class": self.__class__.__name__}
                d["simulations"] = self._dataset.as_dict()
                return d

        s = Simulation()
        e = Experiment(s._simulation_prefix)

        return cls(s, e)

    def add_coordinate(self, coordinate_name, coordinate_values):
        self.store.easyCore.add_coordinate(coordinate_name, coordinate_values)

    def add_variable(self, variable_name, variable_coordinates, values):
        if variable_name in self.store.easyCore.variables:
            self.store.easyCore.remove_variable(variable_name)
        self.store.easyCore.add_variable(variable_name, variable_coordinates, values)

    def as_dict(self, skip=None):
        """
        :return: Json-able dictionary representation.
        """
        d = {"@module": self.__class__.__module__,
             "@class": self.__class__.__name__}
        d["simulations"] = self._simulations.as_dict()
        d["experiments"] = self._experiments.as_dict()
        return d

    @classmethod
    def from_dict(cls, d):
        """
        :param d: Dict representation.
        :return: Species.
        """
        return cls(d["simulations"], d["experiments"])

class JobSetup:
    def __init__(self, datastore_classes, instrumental_parameter_class, pattern_class):
        self.datastore_classes = datastore_classes
        self.instrumental_parameter_class = instrumental_parameter_class
        self.pattern_class = pattern_class


class _PowderBase(BaseObj):
    def __init__(
        self,
        name: str = "",
        job_type=None,
        datastore: xr.Dataset = None,
        phases: Union[Phase, Phases] = None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        if isinstance(phases, Phase):
            phases = Phases("Phases", phases)
        elif phases is None:
            phases = Phases("Phases")

        if not isinstance(phases, Phases):
            raise AttributeError("`phases` must be a Crystal or Crystals")

        if parameters is None:
            parameters = job_type.pattern_class()

        if pattern is None:
            pattern = job_type.instrumental_parameter_class()

        super(_PowderBase, self).__init__(
            name, _phases=phases, _parameters=parameters, _pattern=pattern
        )

        from easyDiffractionLib.Profiles.P1D import (
            Instrument1DCWParameters,
            Instrument1DTOFParameters,
        )
        from easyDiffractionLib.Interfaces.types import Powder, Neutron
        from easyDiffractionLib.Profiles.P1D import Powder1DParameters as Pattern1D
        from easyDiffractionLib.Profiles.P1D import (
            PolPowder1DParameters as Pattern1D_Pol,
        )

        # Set bases for easy identification
        self._update_bases(Powder)
        self._update_bases(Neutron)

        if getattr(pattern, "__old_class__", pattern.__class__) == Pattern1D:
            from easyDiffractionLib.Interfaces.types import UPol

            self._update_bases(UPol)
        elif getattr(pattern, "__old_class__", pattern.__class__) == Pattern1D_Pol:
            from easyDiffractionLib.Interfaces.types import Pol

            self._update_bases(Pol)
        if isinstance(parameters, Instrument1DCWParameters):
            from easyDiffractionLib.Interfaces.types import CW

            self._update_bases(CW)
        elif isinstance(parameters, Instrument1DTOFParameters):
            from easyDiffractionLib.Interfaces.types import TOF

            self._update_bases(TOF)

        self.__constituting_classes = job_type
        self.__dataset = datastore
        self.datastore = DataContainer.prepare(
            self.__dataset, *job_type.datastore_classes
        )

        self.filename = os.path.join(tempfile.gettempdir(), "easydiffraction_temp.cif")
        self.output_index = None
        self.interface = interface

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)

    def remove_background(self, background):
        if (
            background.linked_experiment.raw_value
            in self._pattern.backgrounds.linked_experiments
        ):
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
            value = Phases("Phases", value)
        if not isinstance(value, Phases):
            raise ValueError
        self._phases = value
        self._borg.map.add_edge(self, value)
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
        base_class = getattr(self, "__old_class__", self.__class__)
        old_bases = set(self.__class__.__bases__)
        old_bases = old_bases - {
            base_class,
            *new_base.__mro__,
        }  # This should fix multiple inheritance
        self.__class__.__bases__ = (new_base, *old_bases, base_class)
