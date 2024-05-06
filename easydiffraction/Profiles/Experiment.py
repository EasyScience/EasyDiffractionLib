#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction
import numpy as np
from easyscience.Datasets.xarray import xr
from easyscience.Objects.Job.Experiment import ExperimentBase as coreExperiment
from gemmi import cif

from easydiffraction.elements.Backgrounds.Point import BackgroundPoint
from easydiffraction.elements.Backgrounds.Point import PointBackground

# from easydiffraction.io.cif_reader import background_from_cif_block as background_from_cif
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
    def __init__(self, name: str, datastore: xr.Dataset = None, *args, **kwargs):
        super(Experiment, self).__init__(name, *args, **kwargs)
        self._name = name

        self.is_tof = False
        self.is_polarized = False
        self.is_single_crystal = False
        self.is_2d = False
        self._simulation_prefix = "sim_"
        self._datastore = datastore if datastore is not None else xr.Dataset()
        self.name = name
        self._x_axis_name = ""
        self._y_axis_prefix = "Intensity_"
        self.job_number = 0
        self.cif_string = ""
        # local references to pattern and parameters
        if hasattr(self._datastore, "_simulations"):
            self.pattern = self._datastore._simulations.pattern
            self.parameters = self._datastore._simulations.parameters

    def add_experiment_data(self, x, y, e, experiment_name="None"):

        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name
        self._datastore.store.easyscience.add_coordinate(coord_name, x)

        j = 0
        for i in range(0, len(y)):
            data_y = y[i]
            data_e = e[i]
            self._datastore.store.easyscience.add_variable(
                self.name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self._datastore.store.easyscience.sigma_attach(
                self.name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1


    def add_experiment(self, experiment_name, file_path):
        data = np.loadtxt(file_path, unpack=True)
        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self._datastore.store.easyscience.add_coordinate(coord_name, data[0])

        j = 0
        for i in range(1, len(data), 2):
            data_y = data[i]
            data_e = data[i + 1]
            self._datastore.store.easyscience.add_variable(
                self.name + "_" + experiment_name + f"_I{j}", [coord_name], data_y
            )
            self._datastore.store.easyscience.sigma_attach(
                self.name + "_" + experiment_name + f"_I{j}", data_e
            )
            j += 1
        # self._experiments[]

    def pattern_from_cif_block(self, block):
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
            pattern.zero_shift.error = p['zero_shift'].get('error', 0.0)
            pattern.zero_shift.fixed = False if p['zero_shift'].get('error') else True
        # modify the pattern on the datastore
        self.pattern = pattern

    def parameters_from_cif_block(self, block):
       # Various instrumental parameters
        p = parameters_from_cif(block)
        parameters = Instrument1DCWParameters() # default
        # test for TOF will be done here, once we know what CIF block to expect
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

    def phase_parameters_from_cif_block(self, block):
        # Get phase parameters
        p = phase_parameters_from_cif(block)

        phases = self._datastore._simulations.phases
        for phase in phases:
            if phase.name not in p:
                continue
            phase.scale = p[phase.name].get('value', 0.0)
            if p[phase.name].get('error') is not None:
                phase.scale.error = p[phase.name].get('error', 0.0)
                phase.scale.fixed = False
        pass

    def data_from_cif_block(self, block, experiment_name):
        # data points
        data_x, data_y, data_e = data_from_cif(block)

        coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

        self._datastore.store.easyscience.add_coordinate(coord_name, data_x)

        for i in range(0, len(data_y)):
            self._datastore.store.easyscience.add_variable(
                self.name + "_" + experiment_name + f"_I{i}", [coord_name], data_y[i]
            )
            self._datastore.store.easyscience.sigma_attach(
                self.name + "_" + experiment_name + f"_I{i}", data_e[i]
            )

    def background_from_cif_block(self, block, experiment_name):
        # The background
        # is_tof = isinstance(self, Powder1DTOF)
        is_tof = False
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
            bkg.append(BackgroundPoint.from_pars(x, y))

        self.set_background(bkg)

    def from_xye_file(self, file_url, experiment_name=None):
        """
        Load an xye file into the experiment.
        """
        #data = np.loadtxt(file_url, unpack=True)
        with open(file_url, "r") as f:
            data = f.read()

        if experiment_name is None:
            experiment_name = "None"
        string = _DEFAULT_DATA_BLOCK_NO_MEAS + "\n" + data
        self.from_cif_string(string, experiment_name=experiment_name)

        # self.add_experiment_data(data[0], data[1:], experiment_name=experiment_name)

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
        #is_tof = isinstance(self, Powder1DTOF)
        #is_pol = isinstance(self, PolPowder1DCW)
        is_tof = False
        is_pol = False
        cif = "data_" + self.name + "\n\n"
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
