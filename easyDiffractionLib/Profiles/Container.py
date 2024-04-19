__author__ = "github.com/wardsimon"
__version__ = "0.0.1"


from easyCore.Objects.core import ComponentSerializer

from easyDiffractionLib.Profiles.Experiment import Experiment
from easyDiffractionLib.Profiles.Sample import Sample


class DataContainer(ComponentSerializer):

    def __init__(self, sim_store: Sample, exp_store: Experiment):
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

