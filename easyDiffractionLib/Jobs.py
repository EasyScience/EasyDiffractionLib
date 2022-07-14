__author__ = "github.com/wardsimon"
__version__ = "0.1.1"

from easyCore.Datasets.xarray import xr, np
from easyDiffractionLib.Profiles.common import _PowderBase
from easyDiffractionLib.interface import InterfaceFactory
from easyCore.Fitting.Fitting import Fitter

try:
    import hvplot.xarray  # noqa

    USE_HVPLOT = True
except ImportError:
    USE_HVPLOT = False


class JobBase_1D(_PowderBase):
    def __init__(
        self,
        name: str,
        profileClass,
        datastore: xr.Dataset,
        phases=None,
        parameters=None,
        pattern=None,
    ):
        interface = InterfaceFactory()
        super(JobBase_1D, self).__init__(
            name,
            profileClass,
            datastore,
            phases,
            parameters,
            pattern,
            interface=interface,
        )
        self._x_axis_name = ""
        self._y_axis_prefix = "Intensity_"

    @property
    def simulation_data(self):
        sim_name = self.datastore._simulations._simulation_prefix + self.name
        data = None
        if sim_name in self.datastore.store.keys():
            data = self.datastore.store[sim_name]
        return data

    def create_simulation(self, tth, simulation_name=None, **kwargs):
        if not isinstance(tth, xr.DataArray):
            coord_name = (
                self.datastore._simulations._simulation_prefix
                + self.name
                + "_"
                + self._x_axis_name
            )
            self.datastore.add_coordinate(coord_name, tth)
            self.datastore.store[coord_name].name = self._x_axis_name
        else:
            coord_name = tth.name
        x, f = self.datastore.store[coord_name].easyCore.fit_prep(
            self.interface.fit_func,
            bdims=xr.broadcast(self.datastore.store[coord_name].transpose()),
        )
        y = xr.apply_ufunc(f, *x, kwargs=kwargs)
        y.name = self._y_axis_prefix + self.name + "_sim"
        if simulation_name is None:
            simulation_name = self.name
        else:
            simulation_name = self.name + "_" + simulation_name
        self.datastore._simulations.add_simulation(simulation_name, y)
        return y

    def plot_simulation(self, simulation_name=None):
        if simulation_name is None:
            sim_name = self.datastore._simulations._simulation_prefix + self.name
        else:
            sim_name = (
                self.datastore._simulations._simulation_prefix
                + self.name
                + "_"
                + simulation_name
            )
        return self.datastore.store[sim_name].plot()

    def add_experiment(self, experiment_name, file_path):
        data_x, data_y, data_e = np.loadtxt(file_path, unpack=True)
        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self.datastore.store.easyCore.add_coordinate(coord_name, data_x)
        self.datastore.store.easyCore.add_variable(
            self.name + "_" + experiment_name + "_I", [coord_name], data_y
        )
        self.datastore.store.easyCore.sigma_attach(
            self.name + "_" + experiment_name + "_I", data_e
        )
        # self._experiments[]

    def simulate_experiment(self, experiment_name=None, **kwargs):
        tth_name = self.name + "_" + experiment_name + "_" + self._x_axis_name
        tth = self.datastore.store[tth_name]
        return self.create_simulation(
            tth, simulation_name=self.name + "_" + experiment_name, **kwargs
        )

    def plot_experiment(self, experiment_name=None):
        dataarray_name = self.name + "_" + experiment_name + "_I"
        return self.datastore.store[dataarray_name].plot()

    def fit_experiment(self, experiment_name, fitter=None, **kwargs):
        dataarray_name = self.name + "_" + experiment_name + "_I"
        if fitter is None:
            fitter = Fitter(self, self.interface.fit_func)
        return self.datastore.store[dataarray_name].easyCore.fit(fitter)


class Powder1DCW(JobBase_1D):
    def __init__(
        self,
        name: str,
        datastore: xr.Dataset,
        phases=None,
        parameters=None,
        pattern=None,
    ):
        from easyDiffractionLib.Profiles.P1D import Unpolarized1DClasses

        super(Powder1DCW, self).__init__(
            name, Unpolarized1DClasses, datastore, phases, parameters, pattern
        )
        self._x_axis_name = "tth"


class PolPowder1DCW(JobBase_1D):
    def __init__(
        self,
        name: str,
        datastore: xr.Dataset,
        phases=None,
        parameters=None,
        pattern=None,
    ):
        from easyDiffractionLib.Profiles.P1D import Polarized1DClasses

        super(PolPowder1DCW, self).__init__(
            name, Polarized1DClasses, datastore, phases, parameters, pattern
        )
        self._x_axis_name = "tth"

    def simulate_experiment(self, experiment_name=None, pol_fn=None):
        if pol_fn is None:
            pol_fn = lambda up, down: up + down
        return super(PolPowder1DCW, self).simulate_experiment(
            experiment_name, pol_fn=pol_fn
        )

    def create_simulation(self, tth, simulation_name=None, pol_fn=None, **kwargs):
        if pol_fn is None:
            pol_fn = lambda up, down: up + down
        return super(PolPowder1DCW, self).create_simulation(
            tth, simulation_name, pol_fn=pol_fn, **kwargs
        )


class Powder1DTOF(JobBase_1D):
    def __init__(
        self,
        name: str,
        datastore: xr.Dataset,
        phases=None,
        parameters=None,
        pattern=None,
    ):
        from easyDiffractionLib.Profiles.P1D import Unpolarized1DTOFClasses

        super(Powder1DTOF, self).__init__(
            name, Unpolarized1DTOFClasses, datastore, phases, parameters, pattern
        )
        self._x_axis_name = "time"
