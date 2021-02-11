__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Datasets.xarray import xr, np
from easyDiffractionLib.Profiles.common import _PowderBase
from easyDiffractionLib.interface import InterfaceFactory
from easyCore.Fitting.Fitting import Fitter

class Powder1D(_PowderBase):
    def __init__(self, name: str, datastore: xr.Dataset, phases=None, parameters=None, pattern=None):
        from easyDiffractionLib.Profiles.P1D import Unpolarized1DClasses
        interface = InterfaceFactory()
        super(Powder1D, self).__init__(name, Unpolarized1DClasses, datastore, phases, parameters, pattern, interface=interface)
        self._x_axis_name = 'tth'
        self._y_axis_prefix = 'Intensity_'

    def create_simulation(self, tth, simulation_name=None):
        if not isinstance(tth, xr.DataArray):
            coord_name = self.datastore._simulations._simulation_prefix + self.name + '_tth'
            self.datastore.add_coordinate(coord_name, tth)
            self.datastore.store[coord_name].name = self._x_axis_name
        else:
            coord_name = tth.name
        x, f = self.datastore.store[coord_name].easyCore.fit_prep(self.interface.fit_func,
                                                                  bdims=xr.broadcast(self.datastore.store[coord_name].transpose()))
        y = xr.apply_ufunc(f, *x)
        y.name = self._y_axis_prefix + self.name + '_sim'
        if simulation_name is None:
            simulation_name = self.name
        self.datastore._simulations.add_simulation(simulation_name, y)
        return y

    def plot_simulation(self, simulation_name=None):
        if simulation_name is None:
            sim_name = self.datastore._simulations._simulation_prefix + self.name
        else:
            sim_name = self.datastore._simulations._simulation_prefix + self.name + '_' + simulation_name
        return self.datastore.store[sim_name].plot()

    def add_experiment(self, experiment_name, file_path):
        data_x, data_y, data_e = np.loadtxt(file_path, unpack=True)
        coord_name = self.name + '_' + experiment_name + '_tth'

        self.datastore.store.easyCore.add_coordinate(coord_name, data_x)
        self.datastore.store.easyCore.add_variable(self.name + '_' + experiment_name + '_I', [coord_name], data_y)
        self.datastore.store.easyCore.sigma_attach(self.name + '_' + experiment_name + '_I', data_e)
        # self._experiments[]

    def simulate_experiment(self, experiment_name=None):
        tth_name = self.name + '_' + experiment_name + '_tth'
        tth = self.datastore.store[tth_name]
        return self.create_simulation(tth, simulation_name=self.name + '_' + experiment_name)

    def plot_experiment(self, experiment_name=None):
        dataarray_name = self.name + '_' + experiment_name + '_I'
        return self.datastore.store[dataarray_name].plot()

    def fit_experiment(self, experiment_name, fitter=None):
        dataarray_name = self.name + '_' + experiment_name + '_I'
        if fitter is None:
            fitter = Fitter(self, self.interface.fit_func)
        return self.datastore.store[dataarray_name].easyCore.fit(fitter)
