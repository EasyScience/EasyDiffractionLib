__author__ = "github.com/wardsimon"
__version__ = "0.1.1"

import numpy as np
from easyscience.Datasets.xarray import xr
from easyscience.Fitting.Fitting import Fitter
from gemmi import cif

from easydiffraction.elements.Backgrounds.Point import BackgroundPoint
from easydiffraction.elements.Backgrounds.Point import PointBackground
from easydiffraction.interface import InterfaceFactory
from easydiffraction.Profiles.common import _PowderBase
from easydiffraction.Profiles.P1D import Instrument1DCWPolParameters
from easydiffraction.Profiles.P1D import Instrument1DTOFParameters


class JobBase_1D(_PowderBase):
    def __init__(
        self,
        name: str,
        profileClass,
        datastore: xr.Dataset,
        phases=None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        if interface is None:
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
        self.job_number = 0
        self.cif_string = ""
        if phases is not None and self.phases != phases:
            self.phases = phases
        # The following assignment is necessary for proper binding
        self.interface = interface

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
            if coord_name in self.datastore.store and \
                len(self.datastore.store[coord_name]) != len(tth):
                self.datastore.store.easyscience.remove_coordinate(coord_name)
                self.job_number += 1
                coord_name = (
                    self.datastore._simulations._simulation_prefix
                    + self.name
                    + str(self.job_number)
                    + "_"
                    + self._x_axis_name
                )
            self.datastore.add_coordinate(coord_name, tth)
            self.datastore.store[coord_name].name = self._x_axis_name
        else:
            coord_name = tth.name
        x, f = self.datastore.store[coord_name].easyscience.fit_prep(
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
        # fitter expects ndarrays
        if isinstance(y, xr.DataArray):
            y = y.values
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
        self.datastore.store.easyscience.add_coordinate(coord_name, x)

        j = 0
        for i in range(0, len(y)):
            data_y = y[i]
            data_e = e[i]
            self.datastore.store.easyscience.add_variable(
                self.name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self.datastore.store.easyscience.sigma_attach(
                self.name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1


    def add_experiment(self, experiment_name, file_path):
        data = np.loadtxt(file_path, unpack=True)
        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self.datastore.store.easyscience.add_coordinate(coord_name, data[0])

        j = 0
        for i in range(1, len(data), 2):
            data_y = data[i]
            data_e = data[i + 1]
            self.datastore.store.easyscience.add_variable(
                self.name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self.datastore.store.easyscience.sigma_attach(
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
        return self.datastore.store[dataarray_name].easyscience.fit(fitter)

    def pattern_from_cif_block(self, block):
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

    def parameters_from_cif_block(self, block):
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

    def phase_parameters_from_cif_block(self, block):
         # Get phase parameters
        sample_phase_labels = self.phases.phase_names 
        experiment_phase_labels = list(block.find_loop("_phase_label"))
        experiment_phase_scales = np.fromiter(block.find_loop("_phase_scale"), float)
        for (phase_label, phase_scale) in zip(experiment_phase_labels, experiment_phase_scales):
            if phase_label in sample_phase_labels:
                self.phases[phase_label].scale = phase_scale

    def data_from_cif_block(self, block, experiment_name):
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
            data_y[1] = np.zeros(len(data_y[0]))
            data_e[1] = np.zeros(len(data_e[0]))

        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self.datastore.store.easyscience.add_coordinate(coord_name, data_x)

        for i in range(0, len(data_y)):
            self.datastore.store.easyscience.add_variable(
                self.name + "_" + experiment_name + f"_I{i}", [coord_name], data_y[i]
            )
            self.datastore.store.easyscience.sigma_attach(
                self.name + "_" + experiment_name + f"_I{i}", data_e[i]
            )

    def background_from_cif_block(self, block, experiment_name):
        # The background
        is_tof = isinstance(self, Powder1DTOF)
        if is_tof:
            x_label = "_tof_background_time"
            y_label = "_tof_background_intensity"
        else:
            x_label = "_pd_background_2theta"
            y_label = "_pd_background_intensity"
        background_2thetas = np.fromiter(block.find_loop(x_label), float)
        background_intensities = np.fromiter(block.find_loop(y_label), float)
        bkg = PointBackground(linked_experiment=experiment_name)
        for (x, y) in zip(background_2thetas, background_intensities):
            bkg.append(BackgroundPoint(x, y))

        self.set_background(bkg)

    def from_cif_file(self, file_url, experiment_name=None):
            """
            Load a CIF file into the experiment.
            """
            # content
            cif_string = ""
            with open(file_url, "r") as f:
                cif_string = f.read()
            self.cif_string = cif_string
            self.from_cif_string(cif_string, experiment_name=experiment_name)
            if hasattr(self.interface._InterfaceFactoryTemplate__interface_obj,"set_exp_cif"):
                self.interface._InterfaceFactoryTemplate__interface_obj.set_exp_cif(self.cif_string)

    def from_cif_string(self, cif_string, experiment_name=None):
        """
        Load a CIF string into the experiment.
        """
        block = cif.read_string(cif_string).sole_block()

        if experiment_name is None:
            experiment_name = block.name
        self.from_cif_block(block, experiment_name=experiment_name)

    def from_cif_block(self, block, experiment_name=None):
        """
        Load a CIF file and extract the experiment data.
        This includes
        - the pattern parameters
        - the instrumental parameters
        - the phase parameters
        - the data points
        - the background
        """
        if experiment_name is None:
            experiment_name = block.name
        self.pattern_from_cif_block(block)
        self.parameters_from_cif_block(block)
        self.phase_parameters_from_cif_block(block)
        self.data_from_cif_block(block, experiment_name)
        self.background_from_cif_block(block, experiment_name)

    def as_cif(self):
        '''
        Returns a CIF representation of the experiment.
        (pattern, background, instrument, data points etc.)
        '''
        # header
        is_tof = isinstance(self, Powder1DTOF)
        is_pol = isinstance(self, PolPowder1DCW)
        cif = "data_" + self.name + "\n\n"
        if is_tof:
            cif += tof_param_as_cif(pattern=self.pattern, parameters=self.parameters) + "\n\n"
        else:
            cif += cw_param_as_cif(parameters=self.parameters, pattern=self.pattern)+  "\n\n"

        if is_pol:
            cif += polar_param_as_cif(pattern=self.pattern) + "\n\n"

        background = self.pattern.backgrounds[0]
        cif += phases_as_cif(phases=self.phases) + "\n\n"
        cif += background_as_cif(background=background, is_tof=is_tof) + "\n\n"
        cif += exp_data_as_cif(data=self.datastore, is_tof=is_tof, is_pol=is_pol) + "\n\n"
        return cif
    
    def update_bindings(self):
        self.generate_bindings()


class Powder1DCW(JobBase_1D):
    def __init__(
        self,
        name: str,
        datastore: xr.Dataset = xr.Dataset(),
        phases=None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        from easydiffraction.Profiles.P1D import Unpolarized1DClasses

        super(Powder1DCW, self).__init__(
            name, Unpolarized1DClasses, datastore, phases, parameters, pattern, interface
        )
        self._x_axis_name = "tth"


class PolPowder1DCW(JobBase_1D):
    def __init__(
        self,
        name: str,
        datastore: xr.Dataset = xr.Dataset(),
        phases=None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        from easydiffraction.Profiles.P1D import Polarized1DClasses

        if parameters is None:
            parameters = Instrument1DCWPolParameters()

        super(PolPowder1DCW, self).__init__(
            name, Polarized1DClasses, datastore, phases, parameters, pattern, interface
        )
        self._x_axis_name = "tth"

    def simulate_experiment(self, experiment_name=None, name_post="", pol_fn=None):
        if pol_fn is None:
            # pol_fn = lambda up, down: up + down
            # the same as above but using def()
            def pol_fn(up, down): return up + down
        return super(PolPowder1DCW, self).simulate_experiment(
            experiment_name, name_post, pol_fn=pol_fn
        )

    def create_simulation(self, tth, simulation_name=None, pol_fn=None, **kwargs):
        if pol_fn is None:
            def pol_fn(up, down): return up + down
        return super(PolPowder1DCW, self).create_simulation(
            tth, simulation_name, pol_fn=pol_fn, **kwargs
        )


class Powder1DTOF(JobBase_1D):
    def __init__(
        self,
        name: str,
        datastore: xr.Dataset = xr.Dataset(),
        phases=None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        from easydiffraction.Profiles.P1D import Unpolarized1DTOFClasses

        if parameters is None:
            parameters = Instrument1DTOFParameters()

        super(Powder1DTOF, self).__init__(
            name, Unpolarized1DTOFClasses, datastore, phases, parameters, pattern, interface
        )
        self._x_axis_name = "time"

    def parameters_from_cif_block(self, block):
       # Various instrumental parameters
        value = block.find_value("_tof_parameters_zero")
        if value is not None:
            self.pattern.zero_shift = float(value)
        value = block.find_value("_setup_wavelength")
        if value is not None:
            self.parameters.wavelength = float(value)
        value = block.find_value("_tof_parameters_dtt1")
        if value is not None:
            self.parameters.dtt1 = float(value)
        value = block.find_value("_tof_parameters_dtt2")
        if value is not None:
            self.parameters.dtt2 = float(value)
        value = block.find_value("_tof_parameters_2theta_bank")
        if value is not None:
            self.parameters.ttheta_bank = float(value)
        value = block.find_value("_tof_profile_sigma0")
        if value is not None:
            self.parameters.sigma0 = float(value)
        value = block.find_value("_tof_profile_sigma1")
        if value is not None:
            self.parameters.sigma1 = float(value)
        value = block.find_value("_tof_profile_sigma2")
        if value is not None:
            self.parameters.sigma2 = float(value)
        value = block.find_value("_tof_profile_gamma0")
        if value is not None:
            self.parameters.gamma0 = float(value)
        value = block.find_value("_tof_profile_gamma1")
        if value is not None:
            self.parameters.gamma1 = float(value)
        value = block.find_value("_tof_profile_gamma2")
        if value is not None:
            self.parameters.gamma2 = float(value)
        value = block.find_value("_tof_profile_alpha0")
        if value is not None:
            self.parameters.alpha0 = float(value)
        value = block.find_value("_tof_profile_alpha1")
        if value is not None:
            self.parameters.alpha1 = float(value)
        value = block.find_value("_tof_profile_beta0")
        if value is not None:
            self.parameters.beta0 = float(value)
        value = block.find_value("_tof_profile_beta1")
        if value is not None:
            self.parameters.beta1 = float(value)


def get_job_type_from_file(file_url):
    '''
    Get the job type from a CIF file.

    Based on keywords in the CIF file, the job type is determined.
    '''
    block = cif.read(file_url).sole_block()
    job_type = "Powder1DCW"
    # Check if powder1DCWpol
    value_cwpol = block.find_value("_diffrn_radiation_polarization")
    # value_tof = block.find_value("_pd_meas_time_of_flight")
    value_tof = block.find_loop("_tof_meas_time")  or block.find_loop("_pd_meas_time_of_flight")
    value_cw = block.find_value("_pd_meas_2theta")

    if value_cwpol is not None:
        job_type = "PolPowder1DCW"
    elif value_tof is not None:
        job_type = "Powder1DTOF"
    elif value_cw is not None:
        job_type = "Powder1DCW"
    else:
        raise ValueError("Could not determine job type from file.")
    return job_type

def get_job_from_file(file_url, exp_name="job", phases=None, interface=None):
    '''
    Get the job from a CIF file.

    Based on keywords in the CIF file, the job type is determined,
    the job is created and the data is loaded from the CIF file.
    '''
    block = cif.read(file_url).sole_block()
    datastore = xr.Dataset()
    # Check if powder1DCWpol
    value_cwpol = block.find_value("_diffrn_radiation_polarization")
    # value_tof = block.find_value("_pd_meas_time_of_flight")
    value_tof = block.find_loop("_tof_meas_time")  or block.find_loop("_pd_meas_time_of_flight")
    value_cw = block.find_value("_setup_wavelength")

    if value_cwpol is not None:
        job = PolPowder1DCW(exp_name, datastore, phases, interface=interface)
    elif value_tof:# is not None:
        job = Powder1DTOF(exp_name, datastore, phases, interface=interface)
    elif value_cw is not None:
        job = Powder1DCW(exp_name, datastore, phases, interface=interface)
    else:
        raise ValueError("Could not determine job type from file.")

    # Load the data
    job.from_cif_file(file_url, exp_name)

    return datastore, job


def phases_as_cif(phases=None):
    '''
    Returns a CIF representation of the phases names and scales.
    '''
    cif_phase = "loop_\n"
    cif_phase += "_phase_label\n"
    cif_phase += "_phase_scale\n"
    cif_phase += "_phase_igsize\n"
    for phase in phases:
        cif_phase += phase.name + " " + str(phase.scale.raw_value) + " 0.0\n"
    return cif_phase

def exp_data_as_cif(data=None, is_tof=False, is_pol=False):
    '''
    Returns a CIF representation of the experimental datapoints x,y,e.
    '''
    if data is None:
        return ""

    # for both sim and exp
    cif_exp_data = "_range_2theta_min " + str(data.x[0]) + "\n"
    cif_exp_data += "_range_2theta_max " + str(data.x[-1]) + "\n"
    cif_exp_data += "_setup_radiation neutrons\n"

    # only when exp present
    cif_exp_data += "\nloop_"

    if is_tof():
        cif_exp_data += "\n_tof_meas_time"
        cif_prefix = "_tof_"
    else:
        cif_exp_data += "\n_pd_meas_2theta"
        cif_prefix = "_pd_"

    if is_pol():
        cif_exp_data += "\n" + \
                        cif_prefix + "meas_intensity_up\n" + \
                        cif_prefix + "meas_intensity_up_sigma\n" + \
                        cif_prefix + "meas_intensity_down\n" + \
                        cif_prefix + "meas_intensity_down_sigma"
    else:
        cif_exp_data += "\n" + \
                        cif_prefix + "meas_intensity\n" + \
                        cif_prefix + "meas_intensity_sigma"

    for i in range(len(data.x)):
        cif_exp_data += "\n" + str(data.x[i]) + " "
        if is_pol():
            cif_exp_data += str(data.y[i]) + " " + \
                str(data.e[i]) + " " + \
                str(data.yb[i]) + " " + \
                str(data.eb[i])
        else:
            cif_exp_data += str(data.y[i]) + " " + \
                str(data.e[i])

    return cif_exp_data

def background_as_cif(background=None, is_tof=False):
    '''
    Returns a CIF representation of the background.
    '''
    cif_background = ""
    if background is None:
        return cif_background

    if is_tof():
        cif_background += "\nloop_\n_tof_background_time\n_tof_background_intensity"
    else:
        cif_background += "\nloop_ \n_pd_background_2theta\n_pd_background_intensity"
    # background = self.parent.l_background._background_as_obj
    for i in range(len(background.data)):
        cif_background += "\n" + str(background.data[i].x.raw_value) + " " + str(background.data[i].y.raw_value)
    return cif_background

def cw_param_as_cif(parameters=None, pattern=None):
    '''
    Returns a CIF representation of the CW instrument parameters
    '''
    cif_ipar_data = ""
    cif_ipar_data += "\n_setup_wavelength " + str(parameters.wavelength.raw_value)
    cif_ipar_data += "\n_setup_offset_2theta  " + str(pattern.zero_shift.raw_value)
    cif_ipar_data += "\n"
    cif_ipar_data += "\n_pd_instr_resolution_u " + str(parameters.resolution_u.raw_value)
    cif_ipar_data += "\n_pd_instr_resolution_v " + str(parameters.resolution_v.raw_value)
    cif_ipar_data += "\n_pd_instr_resolution_w " + str(parameters.resolution_w.raw_value)
    cif_ipar_data += "\n_pd_instr_resolution_x " + str(parameters.resolution_x.raw_value)
    cif_ipar_data += "\n_pd_instr_resolution_y " + str(parameters.resolution_y.raw_value)
    cif_ipar_data += "\n"
    cif_ipar_data += "\n_pd_instr_reflex_asymmetry_p1 " + str(parameters.reflex_asymmetry_p1.raw_value)
    cif_ipar_data += "\n_pd_instr_reflex_asymmetry_p2 " + str(parameters.reflex_asymmetry_p2.raw_value)
    cif_ipar_data += "\n_pd_instr_reflex_asymmetry_p3 " + str(parameters.reflex_asymmetry_p3.raw_value)
    cif_ipar_data += "\n_pd_instr_reflex_asymmetry_p4 " + str(parameters.reflex_asymmetry_p4.raw_value)
    return cif_ipar_data

def polar_param_as_cif(pattern=None):
    cif_pat_data = ""
    cif_pat_data += "\n_diffrn_radiation_polarization " + str(pattern.beam.polarization.raw_value)
    cif_pat_data += "\n_diffrn_radiation_efficiency " + str(pattern.efficiency.raw_value)
    cif_pat_data += "\n_setup_field " + str(pattern.field.raw_value)
    # cif_pat_data += "\n_chi2_sum " + str(self._refine_sum)
    # cif_pat_data += "\n_chi2_diff " + str(self._refine_diff)
    # cif_pat_data += "\n_chi2_up " + str(self._refine_up)
    # cif_pat_data += "\n_chi2_down " + str(self._refine_down)
    return cif_pat_data

def tof_param_as_cif(pattern=None, parameters=None):
    '''
    Returns a CIF representation of the TOF instrument parameters
    '''
    cif_tof_data = ""
    cif_tof_data += "\n_tof_parameters_zero " + str(pattern.zero_shift.raw_value)
    cif_tof_data += "\n_tof_parameters_dtt1 " + str(parameters.dtt1.raw_value)
    cif_tof_data += "\n_tof_parameters_dtt2 " + str(parameters.dtt2.raw_value)
    cif_tof_data += "\n_tof_parameters_2theta_bank " + str(parameters.ttheta_bank.raw_value)
    cif_tof_data += "\n_tof_profile_sigma0 " + str(parameters.sigma0.raw_value)
    cif_tof_data += "\n_tof_profile_sigma1 " + str(parameters.sigma1.raw_value)
    cif_tof_data += "\n_tof_profile_sigma2 " + str(parameters.sigma2.raw_value)
    cif_tof_data += "\n_tof_profile_gamma0 " + str(parameters.gamma0.raw_value)
    cif_tof_data += "\n_tof_profile_gamma1 " + str(parameters.gamma1.raw_value)
    cif_tof_data += "\n_tof_profile_gamma2 " + str(parameters.gamma2.raw_value)
    cif_tof_data += "\n_tof_profile_alpha0 " + str(parameters.alpha0.raw_value)
    cif_tof_data += "\n_tof_profile_alpha1 " + str(parameters.alpha1.raw_value)
    cif_tof_data += "\n_tof_profile_beta0 " + str(parameters.beta0.raw_value)
    cif_tof_data += "\n_tof_profile_beta1 " + str(parameters.beta1.raw_value)
    return cif_tof_data
