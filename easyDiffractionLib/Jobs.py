__author__ = "github.com/wardsimon"
__version__ = "0.1.1"

from gemmi import cif
from easyCore.Datasets.xarray import xr, np
from easyDiffractionLib.Profiles.common import _PowderBase
from easyDiffractionLib.elements.Backgrounds.Point import PointBackground, BackgroundPoint
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
        if phases is not None:
            self.phases = phases

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

    def add_experiment_data(self, x, y, e, experiment_name="None"):

        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name
        self.datastore.store.easyCore.add_coordinate(coord_name, x)

        j = 0
        for i in range(0, len(y)):
            data_y = y[i]
            data_e = e[i]
            self.datastore.store.easyCore.add_variable(
                self.name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self.datastore.store.easyCore.sigma_attach(
                self.name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1


    def add_experiment(self, experiment_name, file_path):
        data = np.loadtxt(file_path, unpack=True)
        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self.datastore.store.easyCore.add_coordinate(coord_name, data[0])

        j = 0
        for i in range(1, len(data), 2):
            data_y = data[i]
            data_e = data[i + 1]
            self.datastore.store.easyCore.add_variable(
                self.name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self.datastore.store.easyCore.sigma_attach(
                self.name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1
        # self._experiments[]

    def simulate_experiment(self, experiment_name=None, name_post="", **kwargs):
        tth_name = self.name + "_" + experiment_name + "_" + self._x_axis_name
        tth = self.datastore.store[tth_name]
        return self.create_simulation(
            tth, simulation_name=self.name + "_" + experiment_name + name_post, **kwargs
        )

    def plot_experiment(self, experiment_name=None, index=0):
        dataarray_name = self.name + "_" + experiment_name + f"_I{index}"
        return self.datastore.store[dataarray_name].plot()

    def fit_experiment(self, experiment_name, fitter=None, **kwargs):
        dataarray_name = self.name + "_" + experiment_name + "_I"
        if fitter is None:
            fitter = Fitter(self, self.interface.fit_func)
        return self.datastore.store[dataarray_name].easyCore.fit(fitter)

    def pattern_from_cif(self, block):
        # Various pattern parameters
        value = block.find_value("_diffrn_radiation_polarization")
        if value is not None:
            self.pattern.beam.polarization = float(value)
        value = block.find_value("_diffrn_radiation_efficiency")
        if value is not None:
            self.pattern.beam.efficiency = float(value)
        value = block.find_value("_setup_offset_2theta")
        if value is not None:
            self.pattern.zero_shift = float(value)
        value = block.find_value("_setup_field")
        if value is not None:
            self.pattern.field = float(value)

    def parameters_from_cif(self, block):
       # Various instrumental parameters
        value = block.find_value("_setup_wavelength")
        if value is not None:
            self.parameters.wavelength = float(value)
        value = block.find_value("_pd_instr_resolution_u")
        if value is not None:
            self.parameters.resolution_u = float(value)
        value = block.find_value("_pd_instr_resolution_v")
        if value is not None:
            self.parameters.resolution_v = float(value)
        value = block.find_value("_pd_instr_resolution_w")
        if value is not None:
            self.parameters.resolution_w = float(value)
        value = block.find_value("_pd_instr_resolution_x")
        if value is not None:
            self.parameters.resolution_x = float(value)
        value = block.find_value("_pd_instr_resolution_y")
        if value is not None:
            self.parameters.resolution_y = float(value)
        value = block.find_value("_pd_instr_reflex_asymmetry_p1")
        if value is not None:
            self.parameters.reflex_asymmetry_p1 = float(value)
        value = block.find_value("_pd_instr_reflex_asymmetry_p2")
        if value is not None:
            self.parameters.reflex_asymmetry_p2 = float(value)
        value = block.find_value("_pd_instr_reflex_asymmetry_p3")
        if value is not None:
            self.parameters.reflex_asymmetry_p3 = float(value)
        value = block.find_value("_pd_instr_reflex_asymmetry_p4")
        if value is not None:
            self.parameters.reflex_asymmetry_p4 = float(value)

    def phase_parameters_from_cif(self, block):
         # Get phase parameters
        sample_phase_labels = self.phases.phase_names 
        experiment_phase_labels = list(block.find_loop("_phase_label"))
        experiment_phase_scales = np.fromiter(block.find_loop("_phase_scale"), float)
        for (phase_label, phase_scale) in zip(experiment_phase_labels, experiment_phase_scales):
            if phase_label in sample_phase_labels:
                self.phases[phase_label].scale = phase_scale

    def data_from_cif(self, block, experiment_name):
        # data points
        data_x = np.fromiter(block.find_loop("_pd_meas_2theta"), float)
        data_y = []
        data_e = []
        data_y.append(np.fromiter(block.find_loop("_pd_meas_intensity_up"), float))
        data_e.append(np.fromiter(block.find_loop("_pd_meas_intensity_up_sigma"), float))
        data_y.append(np.fromiter(block.find_loop("_pd_meas_intensity_down"), float))
        data_e.append(np.fromiter(block.find_loop("_pd_meas_intensity_down_sigma"), float))
        # Unpolarized case
        if not np.any(data_y[0]):
            data_y[0] = np.fromiter(block.find_loop("_pd_meas_intensity"), float)
            data_e[0] = np.fromiter(block.find_loop("_pd_meas_intensity_sigma"), float)
            data_y[1] = np.zeros(len(data_y))
            data_e[1] = np.zeros(len(data_e))

        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self.datastore.store.easyCore.add_coordinate(coord_name, data_x)

        for i in range(0, len(data_y)):
            self.datastore.store.easyCore.add_variable(
                self.name + "_" + experiment_name + f"_I{i}", [coord_name], data_y[i]
            )
            self.datastore.store.easyCore.sigma_attach(
                self.name + "_" + experiment_name + f"_I{i}", data_e[i]
            )

    def background_from_cif(self, block, experiment_name):
        # The background
        background_2thetas = np.fromiter(block.find_loop("_pd_background_2theta"), float)
        background_intensities = np.fromiter(block.find_loop("_pd_background_intensity"), float)
        bkg = PointBackground(linked_experiment=experiment_name)
        for (x, y) in zip(background_2thetas, background_intensities):
            bkg.append(BackgroundPoint.from_pars(x, y))

        self.set_background(bkg)
    def load_cif(self, file_url, experiment_name=None):

        block = cif.read(file_url).sole_block()

        if experiment_name is None:
            experiment_name = block.name
        self.pattern_from_cif(block)
        self.parameters_from_cif(block)
        self.phase_parameters_from_cif(block)
        self.data_from_cif(block, experiment_name)
        self.background_from_cif(block, experiment_name)

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

    def simulate_experiment(self, experiment_name=None, name_post="", pol_fn=None):
        if pol_fn is None:
            pol_fn = lambda up, down: up + down
        return super(PolPowder1DCW, self).simulate_experiment(
            experiment_name, name_post, pol_fn=pol_fn
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


def get_job_class_from_file(file_url):
    block = cif.read(file_url).sole_block()
    job_type = "Powder1DCW"
    # Check if powder1DCWpol
    value = block.find_value("_diffrn_radiation_polarization")
    if value is not None:
        job_type = "PolPowder1DCW"
    # Check if powder1DTOFunp
    # ...
    # Check if powder1DTOFpol
    # ...
    return job_type

