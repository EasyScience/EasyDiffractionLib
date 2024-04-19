#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors <support@easydiffraction.org>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easyDiffraction project <https://github.com/easyScience/easyDiffraction


from copy import deepcopy
from typing import TypeVar
from typing import Union

import numpy as np
from easyCore.Datasets.xarray import xr
from easyCore.Fitting.Fitting import Fitter as CoreFitter
from easyCore.Objects.Job.Job import JobBase
from gemmi import cif

from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Profiles.Analysis import Analysis
from easyDiffractionLib.Profiles.Experiment import Experiment
from easyDiffractionLib.Profiles.JobType import JobType
from easyDiffractionLib.Profiles.Sample import Sample
from easyDiffractionLib.Profiles.Container import DataContainer

# from easyDiffractionLib.sample import Sample as EDLSample

T_ = TypeVar('T_')

class DiffractionJob(JobBase):
    """
    This class is the base class for all diffraction specific jobs
    """
    def __init__(
        self,
        name: str,
        job_type: JobType = None,
        datastore: xr.Dataset = None,
        sample=None,
        experiment=None,
        analysis=None,
        interface=None,
    ):
        super(DiffractionJob, self).__init__(
            name
        )

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
        self.fitter = CoreFitter(self, self.calculate_theory)

        # The following assignment is necessary for proper binding
        if interface is None:
            interface = InterfaceFactory()
        self.interface = interface

        # can't have job_type and experiment together
        if job_type is not None and experiment is not None:
            raise ValueError("Job type and experiment cannot be passed together.")

        # assign Job components
        self.sample = sample # container for phases
        self.experiment = experiment
        self.analysis = analysis

        self._summary = None  # TODO: implement
        self._info = None # TODO: implement

        # Instead of creating separate classes for all techniques,
        # as in old EDL (Powder1DCW, PolPowder1DCW, Powder1DTOF, etc)
        # let's have these as attributes of the Job class
        #
        # determine job_type based on Experiment
        self.job_type = JobType("Powder1DCW") if job_type is None else job_type
        if self._experiment is not None:
            self.update_job_type()

    @property
    def sample(self) -> Sample:
        return self._sample
    
    @sample.setter
    def sample(self, value: Union[Sample, None]) -> None:
        # We need to deepcopy the sample to ensure that it is not shared between jobs
        if value is not None:
            self._sample = deepcopy(value)
        else:
            self._sample = Sample("Sample")

    @property
    def theory(self) -> Sample:
        """
        For diffraction, the theory is the sample
        """
        return self._sample

    @theory.setter
    def theory(self, value: Sample) -> None:
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
            self._experiment = Experiment("Experiment")

    @property
    def analysis(self) -> Union[Analysis, None]:
        return self._analysis

    @analysis.setter
    def analysis(self, value: Union[Analysis, None]) -> None:
        # We need to deepcopy the analysis to ensure that it is not shared between jobs
        if value is not None:
            self._analysis = deepcopy(value)
        else:
            self._analysis = Analysis("Analysis")

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
            self.job_type.is_pol = True
        elif value_tof:
            self.job_type.is_tof = True
        elif value_cw is not None:
            self.job_type.is_cw = True
        else:
            raise ValueError("Could not determine job type from file.")

        self._name = block.name

    # TODO: extend for analysis and info

    def update_job_type(self) -> None:
        '''
        Update the job type based on the experiment.
        '''
        self.job_type.is_pol = self.experiment.is_polarized
        self.job_type.is_tof = self.experiment.is_tof
        self.job_type.is_single_crystal = self.experiment.is_single_crystal

        if self.job_type.is_tof:
            self._x_axis_name = "time"
        else:
            self._x_axis_name = "tth"

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
        self.experiment = Experiment.from_cif(file_url)
        self.update_job_type()

    def add_experiment_from_string(self, cif_string: str) -> None:
        '''
        Add an experiment to the job from a CIF string.
        Just a wrapper around the Experiment class method.
        '''
        self.experiment = Experiment.from_cif_string(cif_string)
        self.update_job_type()

    def add_sample_from_file(self, file_url: str) -> None:
        '''
        Add a sample to the job from a CIF file.
        Just a wrapper around the Sample class method.
        '''
        self.sample = Sample.from_cif(file_url)
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
        sample_cif = self.sample.to_cif()
        experiment_cif = self.experiment.to_cif()
        analysis_cif = self.analysis.to_cif()

        # combine all CIFs
        job_cif = sample_cif + "\n\n" + \
                experiment_cif + "\n\n" + \
                analysis_cif
        return job_cif

    ###### CALCULATE METHODS ######
    @property
    def calculator(self):
        '''
        Get the calculator from the interface.
        '''
        return self.interface.calculator

    @calculator.setter
    def calculator(self, value: str):
        '''
        Set the calculator on the interface.
        '''
        # TODO: check if the calculator is available for the given JobType
        self.interface.switch(value, fitter=self.fitter)
        self.interface.calculator = value

    def calculate_theory(self, tth: Union[xr.DataArray, np.ndarray], simulation_name:str="", **kwargs) -> np.ndarray:
        '''
        Implementation of the abstract method from JobBase.
        Just a wrapper around the profile calculation.
        '''
        return self.calculate_profile(tth, simulation_name, **kwargs)

    def calculate_profile(self, tth: Union[xr.DataArray, np.ndarray], simulation_name:str="", **kwargs) -> np.ndarray:
        '''
        Calculate the profile based on current phase.
        '''
        if not isinstance(tth, xr.DataArray):
            coord_name = (
                self.datastore._simulations._simulation_prefix
                + self._name
                + "_"
                + self._x_axis_name
            )
            if coord_name in self.datastore.store and \
                len(self.datastore.store[coord_name]) != len(tth):
                self.datastore.store.easyCore.remove_coordinate(coord_name)
                self.job_number += 1
                coord_name = (
                    self.datastore._simulations._simulation_prefix
                    + self._name
                    + str(self.job_number)
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
        y.name = self._y_axis_prefix + self._name + "_sim"
        if simulation_name is None:
            simulation_name = self._name
        else:
            simulation_name = self._name + "_" + simulation_name
        self.datastore._simulations.add_simulation(simulation_name, y)
        # fitter expects ndarrays
        if type(y) == xr.DataArray:
            y = y.values
        return y

    def fit(self):
        '''
        Fit the profile based on current phase and experiment.
        '''
        method = self.fitter.available_methods()[0]
        self._fit_finished = False

        data = self.interface.data()._inOutDict[self._name]
        x = data['ttheta']
        y = data['signal_exp'][0]
        e = data['signal_exp'][1]
        weights = 1 / e

        kwargs = {
            'weights': weights,
            'method': method
        }

        local_kwargs = {}
        if method == 'least_squares':
            kwargs['minimizer_kwargs'] = {'diff_step': 1e-5}

        # save some kwargs on the interface object for use in the calculator
        self.interface._InterfaceFactoryTemplate__interface_obj.saved_kwargs = local_kwargs
        try:
            res = self.fitter.fit(x, y, **kwargs)

        except Exception:
            return None
        # Add these in a transparent manner for querying the Job object
        # result.success
        # result.reduced_chi
        self.fitting_results = res

    ###### UTILITY METHODS ######
    def add_datastore(self, datastore: xr.Dataset):
        '''
        Add a datastore to the job.
        '''
        self.datastore = DataContainer.prepare(
            datastore, Experiment, Sample #*job_type.datastore_classes
        )

    ###### DUNDER METHODS ######
    def __deepcopy__(self):
        # Re-create the current object
        return DiffractionJob(
            name=self._name,
            sample=self.sample,
            experiment=self.experiment,
            analysis=self.analysis,
            interface=self.interface
        )

    def __str__(self) -> str:
        return f"Job: {self._name}"

    def __repr__(self) -> str:
        return self.__str__()



