#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction
import numpy as np
from easyscience.Datasets.xarray import xr
from easyscience.Objects.Job.Experiment import ExperimentBase as coreExperiment
from easyscience.Objects.ObjectClasses import Descriptor
from easyscience.Objects.ObjectClasses import Parameter
from gemmi import cif

from easydiffraction.elements.Backgrounds.Point import BackgroundPoint
from easydiffraction.elements.Backgrounds.Point import PointBackground
from easydiffraction.io.cif_reader import background_from_cif_block as background_from_cif
from easydiffraction.io.cif_reader import data_from_cif_block as data_from_cif
from easydiffraction.io.cif_reader import parameters_from_cif_block as parameters_from_cif
from easydiffraction.io.cif_reader import pattern_from_cif_block as pattern_from_cif
from easydiffraction.io.cif_reader import phase_parameters_from_cif_block as phase_parameters_from_cif
from easydiffraction.Jobs import background_as_cif
from easydiffraction.Jobs import cw_param_as_cif
from easydiffraction.Jobs import exp_data_as_cif

# from easydiffraction.Jobs import phases_as_cif
from easydiffraction.Jobs import polar_param_as_cif
from easydiffraction.Jobs import tof_param_as_cif
from easydiffraction.Profiles.P1D import Instrument1DCWParameters
from easydiffraction.Profiles.P1D import Instrument1DTOFParameters
from easydiffraction.Profiles.P1D import PolPowder1DParameters
from easydiffraction.Profiles.P1D import Powder1DParameters

_DEFAULT_DATA_BLOCK_NO_MEAS = """data_pnd

_diffrn_radiation.probe neutron
_diffrn_radiation_wavelength.wavelength 1.9

_pd_calib.2theta_offset 0.0

_pd_instr.resolution_u 0.04
_pd_instr.resolution_v -0.05
_pd_instr.resolution_w 0.06
_pd_instr.resolution_x 0
_pd_instr.resolution_y 0

_pd_instr.reflex_asymmetry_p1 0
_pd_instr.reflex_asymmetry_p2 0
_pd_instr.reflex_asymmetry_p3 0
_pd_instr.reflex_asymmetry_p4 0

loop_
_pd_phase_block.id
_pd_phase_block.scale
ph 1.0

loop_
_pd_background.line_segment_X
_pd_background.line_segment_intensity
0 100
180 100

loop_
_pd_meas.2theta_scan
_pd_meas.intensity_total
_pd_meas.intensity_total_su
"""


class Experiment(coreExperiment):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, job_name: str, datastore: xr.Dataset = None, *args, **kwargs):
        super(Experiment, self).__init__(job_name, *args, **kwargs)
        self.job_name = job_name

        self.is_tof = False
        self.is_polarized = False
        self.is_single_crystal = False
        self.is_2d = False
        self._simulation_prefix = "sim_"
        self._datastore = datastore if datastore is not None else xr.Dataset()
        self._x_axis_name = "tth"
        self._y_axis_prefix = "Intensity_"
        self.job_number = 0
        self.cif_string = ""
        self.name = job_name
        # local references to pattern and parameters
        if hasattr(self._datastore, "_simulations"):
            self.pattern = self._datastore._simulations.pattern
            self.parameters = self._datastore._simulations.parameters

    def add_experiment_data(self, x, y, e, experiment_name="None"):

        coord_name = self.job_name + "_" + experiment_name + "_" + self._x_axis_name
        self._datastore.store.easyscience.add_coordinate(coord_name, x)

        j = 0
        for i in range(0, len(y)):
            data_y = y[i]
            data_e = e[i]
            self._datastore.store.easyscience.add_variable(
                self.job_name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self._datastore.store.easyscience.sigma_attach(
                self.job_name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1

    def add_experiment(self, experiment_name, file_path):
        data = np.loadtxt(file_path, unpack=True)
        coord_name = self.job_name + "_" + experiment_name + "_" + self._x_axis_name

        self._datastore.store.easyscience.add_coordinate(coord_name, data[0])

        j = 0
        for i in range(1, len(data), 2):
            data_y = data[i]
            data_e = data[i + 1]
            self._datastore.store.easyscience.add_variable(
                self.job_name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self._datastore.store.easyscience.sigma_attach(
                self.job_name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1

    def pattern_from_cif_block(self, block, experiment_name="None"):
        p = pattern_from_cif(block)
        self.is_polarized = False
        pattern = Powder1DParameters() # default
        if 'beam.polarization' in p or 'beam.efficiency' in p:
            self.is_polarized = True
            pattern = PolPowder1DParameters()
            pattern.beam_polarization = p.get('beam.polarization', 0.0)
            pattern.beam_efficiency = p.get('beam.efficiency', 0.0)
            pattern.field = p.get('field', 0.0)
        if 'zero_shift' in p:
            pattern.zero_shift = p['zero_shift'].get('value', 0.0)
            if p['zero_shift'].get('error') is not None:
                pattern.zero_shift.error = p['zero_shift'].get('error')
                pattern.zero_shift.fixed = False
        bkg = self.background_from_cif_block(block, experiment_name=experiment_name)
        pattern.backgrounds.append(bkg)
        # modify the pattern on the datastore
        self.pattern = pattern
        # self._datastore._simulations._pattern = pattern
        # let the interface know we changed the pattern
        #if hasattr(self.interface._InterfaceFactoryTemplate__interface_obj,"set_pattern"):
        #    self.interface._InterfaceFactoryTemplate__interface_obj.set_pattern(self.pattern)

    def parameters_from_cif_block(self, block):
       # Various instrumental parameters
        p = parameters_from_cif(block)
        if 'wavelength' in p:
            self.is_tof = False
            self.cw_parameters_from_dict(p)
        elif 'dtt1' in p:
            self.is_tof = True
            self.tof_parameters_from_dict(p)
        else:
            raise ValueError("Unknown instrumental parameters in CIF file")

    def cw_parameters_from_dict(self, p: dict):
        # Constant Wavelength instrumental parameters
        parameters = Instrument1DCWParameters()
        if 'wavelength' in p:
            parameters.wavelength = p['wavelength'].get('value', 0.0)
            if p['wavelength'].get('error') is not None:
                parameters.wavelength.error = p['wavelength'].get('error')
                parameters.wavelength.fixed = False
        if 'resolution_u' in p:
            parameters.resolution_u = p['resolution_u'].get('value', 0.0)
            if p['resolution_u'].get('error') is not None:
                parameters.resolution_u.error = p['resolution_u'].get('error')
                parameters.resolution_u.fixed = False

        if 'resolution_v' in p:
            parameters.resolution_v = p['resolution_v'].get('value', 0.0)
            if p['resolution_v'].get('error') is not None:
                parameters.resolution_v.error = p['resolution_v'].get('error')
                parameters.resolution_v.fixed = False

        if 'resolution_w' in p:
            parameters.resolution_w = p['resolution_w'].get('value', 0.0)
            if p['resolution_w'].get('error') is not None:
                parameters.resolution_w.error = p['resolution_w'].get('error')
                parameters.resolution_w.fixed = False


        if 'resolution_x' in p:
            parameters.resolution_x = p['resolution_x'].get('value', 0.0)
            if p['resolution_x'].get('error') is not None:
                parameters.resolution_x.error = p['resolution_x'].get('error')
                parameters.resolution_x.fixed = False

        if 'resolution_y' in p:
            parameters.resolution_y = p['resolution_y'].get('value', 0.0)
            if p['resolution_y'].get('error') is not None:
                parameters.resolution_y.error = p['resolution_y'].get('error')
                parameters.resolution_y.fixed = False

        if 'reflex_asymmetry_p1' in p:
            parameters.reflex_asymmetry_p1 = p['reflex_asymmetry_p1'].get('value', 0.0)
            if p['reflex_asymmetry_p1'].get('error') is not None:
                parameters.reflex_asymmetry_p1.error = p['reflex_asymmetry_p1'].get('error')
                parameters.reflex_asymmetry_p1.fixed = False

        if 'reflex_asymmetry_p2' in p:
            parameters.reflex_asymmetry_p2 = p['reflex_asymmetry_p2'].get('value', 0.0)
            if p['reflex_asymmetry_p2'].get('error') is not None:
                parameters.reflex_asymmetry_p2.error = p['reflex_asymmetry_p2'].get('error')
                parameters.reflex_asymmetry_p2.fixed = False

        if 'reflex_asymmetry_p3' in p:
            parameters.reflex_asymmetry_p3 = p['reflex_asymmetry_p3'].get('value', 0.0)
            if p['reflex_asymmetry_p3'].get('error') is not None:
                parameters.reflex_asymmetry_p3.error = p['reflex_asymmetry_p3'].get('error')
                parameters.reflex_asymmetry_p3.fixed = False

        if 'reflex_asymmetry_p4' in p:
            parameters.reflex_asymmetry_p4 = p['reflex_asymmetry_p4'].get('value', 0.0)
            if p['reflex_asymmetry_p4'].get('error') is not None:
                parameters.reflex_asymmetry_p4.error = p['reflex_asymmetry_p4'].get('error')
                parameters.reflex_asymmetry_p4.fixed = False

        self.parameters = parameters

    def tof_parameters_from_dict(self, p: dict):
       # Time of Flight instrumental parameters
        parameters = Instrument1DTOFParameters()
        if 'dtt1' in p:
            parameters.dtt1 = p['dtt1'].get('value', 0.0)
            if p['dtt1'].get('error') is not None:
                parameters.dtt1.error = p['dtt1'].get('error')
                parameters.dtt1.fixed = False
        if 'dtt2' in p:
            parameters.dtt2 = p['dtt2'].get('value', 0.0)
            if p['dtt2'].get('error') is not None:
                parameters.dtt2.error = p['dtt2'].get('error')
                parameters.dtt2.fixed = False
        if '2theta_bank' in p:
            parameters.ttheta_bank = p['2theta_bank'].get('value', 0.0)
            if p['2theta_bank'].get('error') is not None:
                parameters.ttheta_bank.error = p['2theta_bank'].get('error')
                parameters.ttheta_bank.fixed = False
        if 'alpha0' in p:
            parameters.alpha0 = p['alpha0'].get('value', 0.0)
            if p['alpha0'].get('error') is not None:
                parameters.alpha0.error = p['alpha0'].get('error')
                parameters.alpha0.fixed = False
        if 'alpha1' in p:
            parameters.alpha1 = p['alpha1'].get('value', 0.0)
            if p['alpha1'].get('error') is not None:
                parameters.alpha1.error = p['alpha1'].get('error')
                parameters.alpha1.fixed = False
        if 'beta0' in p:
            parameters.beta0 = p['beta0'].get('value', 0.0)
            if p['beta0'].get('error') is not None:
                parameters.beta0.error = p['beta0'].get('error')
                parameters.beta0.fixed = False
        if 'beta1' in p:
            parameters.beta1 = p['beta1'].get('value', 0.0)
            if p['beta1'].get('error') is not None:
                parameters.beta1.error = p['beta1'].get('error')
                parameters.beta1.fixed = False
        if 'gamma0' in p:
            parameters.gamma0 = p['gamma0'].get('value', 0.0)
            if p['gamma0'].get('error') is not None:
                parameters.gamma0.error = p['gamma0'].get('error')
                parameters.gamma0.fixed = False
        if 'gamma1' in p:
            parameters.gamma1 = p['gamma1'].get('value', 0.0)
            if p['gamma1'].get('error') is not None:
                parameters.gamma1.error = p['gamma1'].get('error')
                parameters.gamma1.fixed = False
        if 'gamma2' in p:
            parameters.gamma2 = p['gamma2'].get('value', 0.0)
            if p['gamma2'].get('error') is not None:
                parameters.gamma2.error = p['gamma2'].get('error')
                parameters.gamma2.fixed = False
        if 'sigma0' in p:
            parameters.sigma0 = p['sigma0'].get('value', 0.0)
            if p['sigma0'].get('error') is not None:
                parameters.sigma0.error = p['sigma0'].get('error')
                parameters.sigma0.fixed = False
        if 'sigma1' in p:
            parameters.sigma1 = p['sigma1'].get('value', 0.0)
            if p['sigma1'].get('error') is not None:
                parameters.sigma1.error = p['sigma1'].get('error')
                parameters.sigma1.fixed = False
        if 'sigma2' in p:
            parameters.sigma2 = p['sigma2'].get('value', 0.0)
            if p['sigma2'].get('error') is not None:
                parameters.sigma2.error = p['sigma2'].get('error')
                parameters.sigma2.fixed = False

        self.parameters = parameters

    def phase_parameters_from_cif_block(self, block):
        # Get phase parameters
        p = phase_parameters_from_cif(block)
        phases = self._datastore._simulations.phases
        for phase in phases:
            pname = phase.name.lower()
            if pname not in p:
                continue
            phase.scale = p[pname].get('value', 0.0)
            if p[pname].get('error') is not None:
                phase.scale.error = p[pname].get('error', 0.0)
                phase.scale.fixed = False
        pass

    def data_from_cif_block(self, block, experiment_name):
        # data points
        data = data_from_cif(block)
        data_x = data['x']
        data_y = data['y']
        data_e = data['e']

        coord_name = self.job_name + "_" + experiment_name + "_" + self._x_axis_name

        self._datastore.store.easyscience.add_coordinate(coord_name, data_x)
        self.is_polarized = False if len(data_y) == 1 else True

        for i in range(0, len(data_y)):
            self._datastore.store.easyscience.add_variable(
                self.job_name + "_" + experiment_name + f"_I{i}", [coord_name], data_y[i]
            )
            self._datastore.store.easyscience.sigma_attach(
                self.job_name + "_" + experiment_name + f"_I{i}", data_e[i]
            )

    def background_from_cif_block(self, block, experiment_name=None):
        # The background
        background_2thetas, background_intensities = background_from_cif(block)

        bkg = PointBackground(linked_experiment=experiment_name)
        for (x, y) in zip(background_2thetas, background_intensities):
            bg_x = Descriptor('x', x)
            intensity = background_intensities[y]['value']
            error = background_intensities[y]['error']
            fixed = error is None
            error = 0.0 if error is None else error
            bg_y = Parameter('intensity', intensity, error=error, fixed=fixed)
            bkg.append(BackgroundPoint(x=bg_x, y=bg_y))
        return bkg

    def from_xye_file(self, file_url, experiment_name=None):
        """
        Load an xye file into the experiment.
        All instrumental parameters are set to default values, defined in the
        Instrument1DCWParameters class.
        """
        with open(file_url, "r") as f:
            data = f.read()

        if experiment_name is None:
            experiment_name = self.name
        string = _DEFAULT_DATA_BLOCK_NO_MEAS + "\n" + data
        self.from_cif_string(string)
        pass

    def from_cif_file(self, file_url, experiment_name=None):
            """
            Load a CIF file into the experiment.
            """
            # content
            # update the reference to parameters and pattern
            # self.pattern = self._datastore._simulations.pattern
            # self.parameters = self._datastore._simulations.parameters
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
            self.name = experiment_name
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
            self.name = experiment_name
        self.pattern_from_cif_block(block, experiment_name=experiment_name)
        self.parameters_from_cif_block(block)
        self.phase_parameters_from_cif_block(block)
        self.data_from_cif_block(block, experiment_name)

    def as_cif(self):
        '''
        Returns a CIF representation of the experiment.
        (pattern, background, instrument, data points etc.)
        '''
        # header
        #is_tof = isinstance(self, Powder1DTOF)
        #is_pol = isinstance(self, PolPowder1DCW)
        is_tof = False
        is_pol = False
        cif = "data_" + self.job_name + "\n\n"
        if is_tof:
            cif += tof_param_as_cif(pattern=self.pattern, parameters=self.parameters) + "\n\n"
        else:
            cif += cw_param_as_cif(parameters=self.parameters, pattern=self.pattern)+  "\n\n"

        if is_pol:
            cif += polar_param_as_cif(pattern=self.pattern) + "\n\n"

        background = self.pattern.backgrounds[0]
        # cif += phases_as_cif(phases=self.phases) + "\n\n"
        cif += background_as_cif(background=background, is_tof=is_tof) + "\n\n"
        cif += exp_data_as_cif(data=self._datastore, is_tof=is_tof, is_pol=is_pol) + "\n\n"
        return cif

    def update_bindings(self):
        self.generate_bindings()

    #
    # vanity methods for querying the datastore
    #
    @property
    def x(self):
        '''
        Returns the x-axis data as xarray
        '''
        coord = self.job_name + "_" + self.name + "_tth"
        if coord in self._datastore.store:
            return self._datastore.store[coord]
        return None

    @property
    def y(self):
        '''
        Returns the y-axis experimental data as xarray
        '''
        coord = self.job_name + "_" + self.name + "_I0"
        if coord in self._datastore.store:
            return self._datastore.store[coord]
        return None

    @property
    def y_alpha(self):
        '''
        Returns the y-axis experimental data as xarray
        '''
        return self.y

    @property
    def y_beta(self):
        '''
        Returns the y-axis experimental data as xarray
        '''
        coord = self.job_name + "_" + self.name + "_I1"
        if coord in self._datastore.store:
            return self._datastore.store[coord]
        return None

    @property
    def e(self):
        '''
        Returns the error data as xarray
        '''
        coord = self.job_name + "_" + self.name + "_I0"
        if coord in self._datastore.store:
            return self._datastore.store[coord]
        return None
 
    @staticmethod
    def from_cif(cif_file: str):
        """
        Load the experiment from a CIF file
        """
        # TODO: Implement this
        return Experiment("Experiment")

    @staticmethod
    def from_cif_strig(cif_string: str):
        """
        Load the experiment from a string
        """
        # TODO: Implement this
        return Experiment("Experiment")

    # required dunder methods
    def __str__(self):
        return f"Experiment: {self._name}"
    
    def as_dict(self, skip: list = []) -> dict:
        this_dict = super(Experiment, self).as_dict(skip=skip)
        return this_dict

    def __copy__(self):
        return Experiment(self.job_name, datastore=self._datastore)
    
    def __deepcopy__(self, memo):
        return Experiment(self.job_name, datastore=self._datastore)