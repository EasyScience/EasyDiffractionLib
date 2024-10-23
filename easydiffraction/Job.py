# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

import importlib.util
import time
from copy import deepcopy
from typing import TypeVar
from typing import Union
import os

import numpy as np
from easyscience.Datasets.xarray import xr  # type: ignore

# from easyscience.fitting.fitter import Fitter as CoreFitter
from easyscience.Objects.job.job import JobBase
from gemmi import cif
from scipy.signal import find_peaks

from easydiffraction import Phase
from easydiffraction import Phases
from easydiffraction.elements.Backgrounds.Point import BackgroundPoint
from easydiffraction.elements.Backgrounds.Point import PointBackground
from easydiffraction.interface import InterfaceFactory
from easydiffraction.Profiles.Analysis import Analysis
from easydiffraction.Profiles.Container import DataContainer
from easydiffraction.Profiles.Experiment import Experiment
from easydiffraction.Profiles.JobType import JobType
from easydiffraction.Profiles.P1D import Instrument1DCWParameters
from easydiffraction.Profiles.P1D import Instrument1DTOFParameters
from easydiffraction.Profiles.P1D import PolPowder1DParameters
from easydiffraction.Profiles.P1D import Powder1DParameters

# from easydiffraction.Profiles.Sample import Sample
from easydiffraction.sample import Sample

try:
    import darkdetect
except ImportError:
    print("darkdetect not installed")

try:
    # import plotly.express as px # unused
    import plotly.graph_objects as go
    import plotly.io as pio
    if importlib.util.find_spec("darkdetect") is None:
        print("Warning: Darkdetect not installed. Try `pip install darkdetect`.")
    else:
        pio.templates.default = "plotly_dark" if darkdetect.isDark() else "plotly_white"
except ImportError:
    print("plotly not installed")

try:
    import py3Dmol
except ImportError:
    print("py3Dmol not installed")

try:
    import pandas as pd
except ImportError:
    print("pandas not installed")

if 'JPY_PARENT_PID' in os.environ:
    from IPython.display import display

T_ = TypeVar('T_')

class DiffractionJob(JobBase):
    """
    This class is the base class for all diffraction specific jobs
    """
    def __init__(
        self,
        name: str = None,
        type: Union[JobType, str] = None,
        datastore: xr.Dataset = None,
        sample=None,
        experiment=None,
        analysis=None,
        interface=None,
    ):
        super(DiffractionJob, self).__init__(
            name
        )
        # The following assignment is necessary for proper binding
        if interface is None:
            interface = InterfaceFactory()
        self.interface = interface

        # Generate the datastore for this job
        __dataset = datastore if datastore is not None else xr.Dataset()
        self.add_datastore(__dataset)
        self._name = name if name is not None else "Job"

        self.cif_string = ""
        # Dataset specific attributes
        self._x_axis_name = "tth" # default for CW, can be `time` for TOF
        self._y_axis_prefix = "Intensity_" # constant for all techniques
        self.job_number = 0 # for keeping track of multiple simulations within the dataset

        # Fitting related attributes
        self.fitting_results = None

        # can't have type and experiment together
        if type is not None and experiment is not None:
            raise ValueError("Job type and experiment cannot be passed together.")

        # assign Experiment, so potential type assignment can be done
        self.experiment = experiment

        self._summary = None  # TODO: implement
        self._info = None # TODO: implement

        # Instead of creating separate classes for all techniques,
        # as in old EDL (Powder1DCW, PolPowder1DCW, Powder1DTOF, etc)
        # let's have these as attributes of the Job class
        #
        # determine type based on Experiment
        self._type = None
        self._sample = None

        # assign Experiment parameters to Sample
        if self.experiment is not None and self.sample is not None and hasattr(experiment, 'parameters'):
            self.sample.parameters = self.experiment.parameters
        self.type = JobType() if type is None else type
        if isinstance(type, str):
            self.type = JobType(type)
        if type is None:
            self.update_job_type()
        else:
            # update experiment with right type
            self.update_exp_type()

        # assign Job components
        self.sample = sample # container for phases
        self.interface = self.sample._interface
        self.analysis = analysis
        # necessary for the fitter
        # TODO: remove the dependency on kwargs
        self._kwargs = {}
        self._kwargs['_phases'] = self.sample.phases
        self._kwargs['_parameters'] = self.sample.parameters
        self._kwargs['_pattern'] = self.sample.pattern


    @property
    def sample(self) -> Sample:
        return self._sample

    @sample.setter
    def sample(self, value: Union[Sample, None]) -> None:
        # We need to deepcopy the sample to ensure that it is not shared between jobs
        if value is not None:
            self._sample = value
            # self._sample = deepcopy(value) # TODO fix deepcopy on EXC sample
        else:
            # pass the initial parameters, based on type
            if self.type.is_pol:
                pattern = PolPowder1DParameters()
            else:
                pattern = Powder1DParameters()
            if self.type.is_cwl:
                parameters = Instrument1DCWParameters()
            elif self.type.is_tof:
                parameters = Instrument1DTOFParameters()
            self._sample = Sample("Sample", parameters=parameters, pattern=pattern)

    @property
    def theoretical_model(self) -> Sample:
        """
        For diffraction, the theoretical_model is the sample
        """
        return self._sample

    @theoretical_model.setter
    def theoretical_model(self, value: Sample) -> None:
        self.sample = value

    @property
    def experiment(self) -> Union[Experiment, None]:
        return self._experiment

    @experiment.setter
    def experiment(self, value: Union[Experiment, None]) -> None:
        # We need to deepcopy the experiment to ensure that it is not shared between jobs
        if value is not None:
            self._experiment = deepcopy(value)
        else:
            self._experiment = Experiment(job_name=self._name,
                                          datastore=self.datastore,
                                          interface=self.interface)

    @property
    def analysis(self) -> Union[Analysis, None]:
        return self._analysis

    @analysis.setter
    def analysis(self, value: Union[Analysis, None]) -> None:
        # We need to deepcopy the analysis to ensure that it is not shared between jobs
        if value is not None:
            self._analysis = deepcopy(value)
        else:
            self._analysis = Analysis(self._name,
                                      interface=self.interface)

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        self._summary = value

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        self._info = value

    @property
    def type(self) -> JobType:
        return self._type

    @type.setter
    def type(self, value: Union[JobType, str]) -> None:
        if isinstance(value, str):
            self._type = JobType(value)
        else:
            self._type = value
        # we modified the type - this job goes back to the default state
        if hasattr(self, 'sample') and self.sample is not None:
            phases = self.sample.phases
            # recreate the sample based on the current type
            self.sample = None
            self.sample.phases = phases

    ###### VANITY PROPERTIES ######
    @property
    def fitter(self):
        return self.analysis._fitter

    @property
    def parameters(self):
        return self.sample.parameters

    @property
    def pattern(self):
        if hasattr(self.experiment, 'pattern'):
            return self.experiment.pattern
        elif hasattr(self.sample, '_pattern'):
            return self.sample._pattern
        return None

    @property
    def phases(self) -> Phases:
        return self.sample.phases

    @property
    def background(self):
        # calculate background based on the experimental x values
        x = self.experiment.x
        return self.experiment.pattern.backgrounds[0].calculate(x) if x is not None else None

    @property
    def backgrounds(self):
        return self.experiment.pattern.backgrounds

    def set_job_from_file(self, file_url: str) -> None:
        '''
        Set the job from a CIF file.

        Based on keywords in the CIF file, the job type is determined,
        the job is modified and the data is loaded from the CIF file.
        '''
        block = cif.read(file_url).sole_block()
        self.cif_string = block.as_string()
        value_cwpol = block.find_value("_diffrn_radiation_polarization")
        value_tof = block.find_loop("_tof_meas_time")  or block.find_loop("_pd_meas_time_of_flight")
        value_cw = block.find_value("_setup_wavelength") or block.find_value("_diffrn_radiation_wavelength.wavelength")

        if value_cwpol is not None:
            self.type.is_pol = True
        elif value_tof:
            self.type.is_tof = True
        elif value_cw is not None:
            self.type.is_cwl = True
        else:
            raise ValueError("Could not determine job type from file.")

        self._name = block.name

    def add_phase(self, id: str="", phase: Union[Phase, None]=None) -> None:
        '''
        Add a phase to the Sample.
        '''
        if phase is None:
            phase = Phase(id)
        # self.sample.phases.append(phase)
        cif_string = phase.cif
        self.sample.add_phase_from_string(cif_string)

    def remove_phase(self, id: str) -> None:
        '''
        Remove a phase from the Sample.
        '''
        del self.sample.phases[id]

    # TODO: extend for analysis and info

    def update_job_type(self) -> None:
        '''
        Update the job type based on the experiment.
        '''
        self.type.is_pol = self.experiment.is_polarized
        self.type.is_tof = self.experiment.is_tof
        self.type.is_sc = self.experiment.is_single_crystal
        self.type.is_2d = self.experiment.is_2d

        if self.type.is_tof:
            self._x_axis_name = "time"
            if self.pattern is not None:
                self.pattern.zero_shift.unit = "μs"
        else:
            self._x_axis_name = "tth"
            if self.pattern is not None:
                self.pattern.zero_shift.unit = "degree"

    def update_exp_type(self) -> None:
        '''
        Update the experiment type based on the job.
        '''
        self.experiment.is_polarized = self.type.is_pol
        self.experiment.is_tof = self.type.is_tof
        self.experiment.is_single_crystal = self.type.is_sc
        self.experiment.is_2d = self.type.is_2d

    def update_phase_scale(self) -> None:
        '''
        Update the phase scale based on the experiment.
        '''
        for phase in self.sample.phases:
            phase.scale = self.experiment.phase_scale.get(phase.name, phase.scale)

    ###### BACKGROUNDS ######
    def set_background(self, points: list) -> None:
        '''
        Sets a background on the pattern.
        '''
        # extract experiment name so we can link the background to it
        experiment_name = self.experiment.name
        bkg = PointBackground(linked_experiment=experiment_name)
        for point in points:
            # necessary in case points are xarray DataArrays
            point0 = float(point[0])
            point1 = float(point[1])
            bkg.append(BackgroundPoint(point0, point1))
        self.sample.set_background(bkg)
        if len(self.experiment.pattern.backgrounds) == 0:
            self.experiment.pattern.backgrounds.append(bkg)
        else:
            self.experiment.pattern.backgrounds[0] = bkg

    ###### CIF RELATED METHODS ######

    @classmethod
    def from_cif_file(cls, phase: Union[Sample, None]=None, experiment: Union[Experiment, None]=None):
        '''
        Create the job from a CIF file.
        Allows for instatiation of the job with a sample and experiment from CIF files.

        :param phase: URL of the CIF file containing the sample information.
        :param experiment: URL of the CIF file containing the experiment information.
        note: both can be the same file
        e.g.
        job = Job.from_cif_file(phase="d1a_phase.cif", experiment="d1a_exp.cif")
        job = Job.from_cif_file("d1a.cif")
        '''
        job_name = "Job"
        if phase is not None:
            sample = Sample.from_cif(phase)

        if experiment is not None:
            exp = Experiment.from_cif(experiment)
            job_name = exp.name
        # try parsing the phase CIF if the experiment CIF is not available
        if sample is not None and experiment is None:
            exp = Experiment.from_cif(phase)
            job_name = exp.name

        return cls(name=job_name, sample=sample, experiment=exp)

    def add_experiment_from_file(self, file_url: str) -> None:
        '''
        Add an experiment to the job from a CIF file.
        Just a wrapper around the Experiment class method.
        '''
        # experiment can be either xye or cif
        # check the extension first and then call the appropriate method
        if file_url.endswith(".xye"):
            self.experiment.from_xye_file(file_url)
        else:
            self.experiment.from_cif_file(file_url)

        self.update_job_type()
        # re-do the sample in case of type change.
        if self.sample.parameters.name != self.experiment.parameters.name:
            # Different type read in (likely TOF), so re-create the sample
            parameters = self.experiment.parameters
            pattern = self.experiment.pattern
            phases = self.sample.phases
            name = self.sample.name
            self.sample = Sample(name, parameters=parameters, pattern=pattern, phases=phases)
            self.sample.parameters = self.experiment.parameters
            self.update_job_type()
            self.update_interface()

    def add_experiment_from_string(self, cif_string: str) -> None:
        '''
        Add an experiment to the job from a CIF string.
        Just a wrapper around the Experiment class method.
        '''
        self.experiment.from_cif_string(cif_string)
        self.update_job_type()

    def add_sample_from_file(self, file_url: str) -> None:
        '''
        Deprecated. Use add_phase_from_file instead.
        Add a sample to the job from a CIF file.
        Just a wrapper around the Sample class method.
        '''
        self.sample.add_phase_from_cif(file_url)
        # sample doesn't hold any information about the job type
        # so no call to update_job_type
        self.datastore._simulations = self.sample

    # Alias to deprecated add_sample_from_file. This is for consistency with the old EDL.
    add_phase_from_file = add_sample_from_file

    def add_sample_from_string(self, cif_string: str) -> None:
        '''
        Add a sample to the job from a CIF string.
        Just a wrapper around the Sample class method.
        '''
        self.sample.add_phase_from_string(cif_string)
        self.datastore._simulations = self.sample
        # sample doesn't hold any information about the job type
        # so no call to update_job_type

    def add_analysis_from_file(self, file_url: str) -> None:
        '''
        Add an analysis to the job from a CIF file.
        Just a wrapper around the Analysis class method.
        '''
        self.analysis = Analysis.from_cif(file_url)
        # analysis doesn't hold any information about the job type
        # so no call to update_job_type

    def to_cif(self) -> str:
        '''
        Convert the job to a CIF file.
        '''
        phase_cif = self.phases[0].cif # temporarily only one phase
        sample_cif = self.sample.cif
        experiment_cif = self.experiment.cif
        analysis_cif = "" # TODO: implement
        # analysis_cif = self.analysis.to_cif()

        # combine all CIFs
        job_cif = phase_cif + "\n\n" + \
                sample_cif + "\n\n" + \
                experiment_cif + "\n\n" + \
                analysis_cif
        return job_cif

    ###### CALCULATE METHODS ######
    @property
    def calculator(self):
        '''
        Get the calculator from the interface.
        '''
        #return self.interface.current_interface_name
        return self.analysis.calculator

    @calculator.setter
    def calculator(self, value: str):
        '''
        Set the calculator on the interface.
        '''
        self.analysis.calculator = value

    def calculate_theory(self, x: Union[xr.DataArray, np.ndarray], simulation_name:str="", **kwargs) -> np.ndarray:
        '''
        Implementation of the abstract method from JobBase.
        Just a wrapper around the profile calculation.
        '''
        return self.calculate_profile(x, simulation_name, **kwargs)

    def calculate_profile(self, x: Union[xr.DataArray, np.ndarray] = None, simulation_name:str="", **kwargs) -> np.ndarray:
        '''
        Pull out necessary data from the datastore and calculate the profile.
        '''
        if x is None:
            x_coord_name = (
                self._name
                + "_"
                + self.experiment.name
                + "_"
                + self._x_axis_name
            )
            if x_coord_name not in self.datastore.store:
                raise ValueError("x-axis data not found in the datastore.")
            x = self.datastore.store[x_coord_name]
        if not isinstance(x, xr.DataArray):
            coord_name = (
                self.datastore._simulations._simulation_prefix
                + self._name
                + "_"
                + self._x_axis_name
            )
            if coord_name in self.datastore.store and \
                len(self.datastore.store[coord_name]) != len(x):
                self.datastore.store.EasyScience.remove_coordinate(coord_name)
                self.job_number += 1
                coord_name = (
                    self.datastore._simulations._simulation_prefix
                    + self._name
                    + str(self.job_number)
                    + "_"
                    + self._x_axis_name
                )
            self.datastore.add_coordinate(coord_name, x)
            self.datastore.store[coord_name].name = self._x_axis_name
        else:
            coord_name = x.name
        coord = self.datastore.store[coord_name]
        y = self.analysis.calculate_profile(x, coord, **kwargs)

        y.name = self._y_axis_prefix + self._name + "_sim"
        if not simulation_name:
            simulation_name = self._name
        else:
            simulation_name = self._name + "_" + simulation_name
        self.datastore.store[self.datastore._simulations._simulation_prefix + simulation_name] = y
        # fitter expects ndarrays
        if isinstance(y, xr.DataArray):
            y = y.values
        return y

    def fit(self, **kwargs):
        '''
        Fit the profile based on current phase and experiment.
        '''
        x = self.experiment.x
        y = self.experiment.y
        e = self.experiment.e
        # we must have experimental data to fit so the pattern needs to
        # be reset to experimental pattern.
        self._kwargs['_pattern'] = self.experiment.pattern

        kwargs.update(self._kwargs)

        if 'method' in kwargs and 'tolerance' in kwargs:
            kwargs['minimizer_kwargs'] = {'ftol': kwargs['tolerance'], 'xtol': kwargs['tolerance']}
            del kwargs['tolerance']

        start = time.time()
        result = self.analysis.fit(x, y, e, **kwargs)
        end = time.time()

        # Add these in a transparent manner for querying the Job object
        # result.success
        # result.reduced_chi
        if result is None:
            raise ValueError("Fitting failed")

        if result.success:
            print("Fitting successful")
            print(f"Duration: {end - start:.2f} s")
            print(f"Reduced chi: {result.reduced_chi:.2f}")
        else:
            print("Fitting failed.")

        self.fitting_results = result


    ###### UTILITY METHODS ######
    def add_datastore(self, datastore: xr.Dataset):
        '''
        Add a datastore to the job.
        '''
        self.datastore = DataContainer.prepare(
            datastore, Sample, Experiment #*type.datastore_classes
        )

    def update_interface(self):
        '''
        Update the interface based on the current job.
        '''
        if hasattr(self.interface._InterfaceFactoryTemplate__interface_obj,"set_job_type"):
            self.interface._InterfaceFactoryTemplate__interface_obj.set_job_type(tof=self.type.is_tof, pol=self.type.is_pol)
        self.interface.generate_bindings(self)
        self.generate_bindings()

    # Charts

    def show_crystal_structure(self, id=None):
        '''
        Show the crystal structure.
        '''
        if importlib.util.find_spec("py3Dmol") is None:
            print("Warning: py3Dmol not installed. Try `pip install py3Dmol`.")
            return

        if id is None:
            print("Warning: phase id is not given.")
            return

        phase = self.phases[id]
        cif = phase.cif

        structure_view = py3Dmol.view(linked=False)
        structure_view.addModel(cif, 'cif')
        structure_view.setStyle({'sphere': {'colorscheme': 'Jmol', 'scale': .2},
                                 'stick': {'colorscheme': 'Jmol', 'radius': 0.1}})
        if importlib.util.find_spec("darkdetect") is not None and darkdetect.isDark():
            structure_view.setBackgroundColor('#111')
        structure_view.addUnitCell()
        structure_view.replicateUnitCell(2, 2, 2)
        structure_view.zoomTo()
        structure_view.show()

    def print_data(self):
        '''
        Print the datastore.
        '''
        np.set_printoptions(precision=2)
        print('Measured x:  ', self.experiment.x.data)
        print('Measured y:  ', self.experiment.y.data)
        print('Measured sy: ', self.experiment.e.data)
        print('Calculated y:', self.calculate_profile())

    def show_experiment_chart(self):
        '''
        Show the experiment chart.
        '''
        if importlib.util.find_spec("plotly") is None:
            print("Warning: Plotly not installed. Try `pip install plotly`.")
            return

        if self.type.is_pd and self.type.is_cwl:
            x_axis_title = '2θ (degree)'
        elif self.type.is_pd and self.type.is_tof:
            x_axis_title = 'TOF (µs)'
        else:
            x_axis_title = ''

        main_y_range = self.experiment.y.data.max() - self.experiment.y.data.min()
        main_y_min = self.experiment.y.data.min() - main_y_range / 10
        main_y_max = self.experiment.y.data.max() + main_y_range / 10

        trace_bkg = go.Scatter(
            x=self.experiment.x.data,
            y=self.background,
            line=dict(color='gray'),  # default: width=2?
            mode='lines',
            name='Background (Ibkg)'
        )

        trace_meas = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data,
            line=dict(color='rgb(31, 119, 180)'),
            mode='lines',
            name='Measured (Imeas)'
        )

        trace_meas_upper = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data + self.experiment.e.data,
            mode='lines',
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False
        )

        trace_meas_lower = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data - self.experiment.e.data,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(31, 119, 180, 0.3)',
            fill='tonexty',
            hoverinfo="skip",
            showlegend=False
        )

        data = [trace_bkg, trace_meas, trace_meas_lower, trace_meas_upper]

        layout = go.Layout(
            autosize=True,
            margin=dict(autoexpand=True,
                        r=30, t=30, b=45),
            legend=dict(yanchor="top", y=1.0,
                        xanchor="right", x=1.0),
            xaxis=dict(title_text=x_axis_title),
            yaxis=dict(title_text='Imeas, Ibkg', range=[main_y_min, main_y_max]),
        )

        fig = go.Figure(data=data, layout=layout)

        fig.update_xaxes(showline=True, mirror=True, zeroline=False)
        fig.update_yaxes(showline=True, mirror=True, zeroline=False)

        fig.show()

    def show_analysis_chart(self):
        '''
        Show the analysis chart.
        '''
        if importlib.util.find_spec("plotly") is None:
            print("Warning: Plotly not installed. Try `pip install plotly`.")
            return

        if self.type.is_pd and self.type.is_cwl:
            x_axis_title = '2θ (degree)'
        elif self.type.is_pd and self.type.is_tof:
            x_axis_title = 'TOF (µs)'
        else:
            x_axis_title = ''

        main_height = 6
        bragg_height = 1
        resid_height = 2
        full_height = resid_height + bragg_height + main_height

        x_min = self.experiment.x.data.min()
        x_max = self.experiment.x.data.max()

        main_y_range = self.experiment.y.data.max() - self.experiment.y.data.min()
        main_y_min = self.experiment.y.data.min() - main_y_range / 10
        main_y_max = self.experiment.y.data.max() + main_y_range / 10
        resid_y_range = (main_y_max - main_y_min) * resid_height / main_height
        resid_y_min = -resid_y_range / 2
        resid_y_max = resid_y_range / 2

        y_calc = self.calculate_profile()

        peak_idx, _ = find_peaks(y_calc)
        x_bragg = self.experiment.x.data[peak_idx]
        y_bragg = np.zeros_like(x_bragg)

        trace_resid = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data - y_calc,
            xaxis='x',
            yaxis='y',
            line=dict(color='rgb(44, 160, 44)'),
            mode='lines',
            name='Residual (Imeas - Icalc)'
        )

        trace_bragg = go.Scatter(
            x=x_bragg,
            y=y_bragg,
            xaxis='x2',
            yaxis='y2',
            line=dict(color='rgb(230, 171, 2)'),  #color=px.colors.qualitative.Plotly[9]),
            mode='markers',
            marker=dict(
                symbol='line-ns-open',
                size=10,
                line=dict(width=1)
            ),
            name='Bragg peaks'
        )

        trace_bkg = go.Scatter(
            x=self.experiment.x.data,
            y=self.background,
            xaxis='x3',
            yaxis='y3',
            line=dict(color='gray'),
            mode='lines',
            name='Background (Ibkg)'
        )

        trace_calc = go.Scatter(
            x=self.experiment.x.data,
            y=y_calc,
            xaxis='x3',
            yaxis='y3',
            line=dict(color='rgb(214, 39, 40)'),
            mode='lines',
            name='Total calculated (Icalc)'
        )

        trace_meas = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data,
            xaxis='x3',
            yaxis='y3',
            line=dict(color='rgb(31, 119, 180)'),
            mode='lines',
            name='Measured (Imeas)'
        )

        trace_meas_upper = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data + self.experiment.e.data,
            xaxis='x3',
            yaxis='y3',
            mode='lines',
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False
        )

        trace_meas_lower = go.Scatter(
            x=self.experiment.x.data,
            y=self.experiment.y.data - self.experiment.e.data,
            xaxis='x3',
            yaxis='y3',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(31, 119, 180, 0.3)',
            fill='tonexty',
            hoverinfo="skip",
            showlegend=False
        )

        data = [trace_bragg,
                trace_resid,
                trace_bkg, trace_meas, trace_meas_lower, trace_meas_upper, trace_calc]

        layout = go.Layout(
            # autosize = True,
            margin=dict(autoexpand=True,
                        r=30, t=30, b=45),
            legend=dict(yanchor="top", y=1.0,
                        xanchor="right", x=1.0),
            xaxis=dict(
                title_text=x_axis_title,
                anchor='y',
                range=[x_min, x_max],
                showline=True, mirror=True, zeroline=False
            ),
            xaxis2=dict(
                matches='x',
                anchor='y2',
                range=[x_min, x_max],
                showline=True, mirror=True, zeroline=False, showticklabels=False
            ),
            xaxis3=dict(
                matches='x',
                anchor='y3',
                range=[x_min, x_max],
                showline=True, mirror=True, zeroline=False, showticklabels=False
            ),
            yaxis=dict(
                title_text='Imeas - Icalc',
                domain=[0, resid_height / full_height - 0.01],
                range=[resid_y_min, resid_y_max],
                tickvals=[int(resid_y_min), 0, int(resid_y_max)],
                showline=True, mirror=True, showgrid=False
            ),
            yaxis2=dict(
                domain=[resid_height / full_height + 0.01, (resid_height + bragg_height) / full_height - 0.01],
                showline=True, mirror=True, showgrid=False, zeroline=False, showticklabels=False
            ),
            yaxis3=dict(
                title_text='Imeas, Icalc, Ibkg',
                domain=[(resid_height + bragg_height) / full_height + 0.01, 1],
                range=[main_y_min, main_y_max],
                showline=True, mirror=True, zeroline=False
            )
        )

        fig = go.Figure(data=data, layout=layout)
        fig.show()

    def print_free_parameters(self):
        '''
        Print the free parameters.
        '''
        if importlib.util.find_spec("pandas") is not None:
            parameters = {'names': [], 'values': [], 'errors': [], 'units': []}
            for parameter in self.get_fit_parameters():
                parameters['names'].append(parameter.display_name)
                parameters['values'].append(parameter.raw_value)
                parameters['errors'].append(parameter.error)
                parameters['units'].append(f'{parameter.unit:~P}')
            df = pd.DataFrame(parameters)
            df.index += 1
            df.style.format(precision=5)
            if 'JPY_PARENT_PID' in os.environ:
                display(df)
            else:
                print(df)
        else:
            for parameter in self.get_fit_parameters():
                print(parameter)

    ###### DUNDER METHODS ######
    def __copy__(self):
        # Re-create the current object
        return DiffractionJob(
            name=self._name,
            sample=self.sample,
            experiment=self.experiment,
            analysis=self.analysis,
            interface=self.interface
        )

    def __deepcopy__(self, j):
        # Re-create the current object
        return DiffractionJob(
            name=j._name,
            sample=j.sample,
            experiment=j.experiment,
            analysis=j.analysis,
            interface=j.interface
        )

    def __str__(self) -> str:
        return f"Job: {self._name}"

    def __repr__(self) -> str:
        return self.__str__()
