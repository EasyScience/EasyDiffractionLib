#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors <support@easydiffraction.org>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easyDiffraction project <https://github.com/easyScience/easyDiffraction


# easyScience
from typing import Union

from easyCore.Datasets.xarray import xr
from easyCore.Objects.Job.Job import JobBase
from gemmi import cif

from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Profiles.Analysis import Analysis
from easyDiffractionLib.Profiles.Experiment import Experiment
from easyDiffractionLib.Profiles.JobType import JobType
from easyDiffractionLib.Profiles.Sample import Sample

# from easyDiffractionLib.sample import Sample as EDLSample


class DiffractionJob(JobBase):
    """
    This class is the base class for all diffraction specific jobs
    """
    def __init__(
        self,
        name: str,
        job_type: JobType = None,
        datastore: xr.Dataset = None,
        phases=None, # remove
        sample=None,
        experiment=None,
        analysis=None,
        interface=None,
    ):
        super(DiffractionJob, self).__init__(
            name
        )

        self.cif_string = ""
        self.datastore = datastore if datastore is not None else xr.Dataset()
        self._name = name if name is not None else "Job"

        # phases are hidden inside the Sample object
        # if phases is not None and self.phases != phases:
        #     self.phases = phases

        # The following assignment is necessary for proper binding
        if interface is None:
            interface = InterfaceFactory()
        self.interface = interface

        # components
        self._sample = sample if sample is not None else Sample("Sample") # container for phases
        self._experiment = experiment if experiment is not None else Experiment("Experiment")
        self._analysis = analysis if analysis is not None else Analysis("Analysis")

        self._summary = None  # TODO: implement
        self._info = None # TODO: implement

        # Instead of creating separate classes for all techniques,
        # as in old EDL (Powder1DCW, PolPowder1DCW, Powder1DTOF, etc)
        # let's have these as attributes of the Job class
        #
        # job_type can be directly assigned when it doesn't clash with
        # the content of the Experiment object, if passed.
        #
        # determine job_type based on Experiment
        job_type = JobType("Powder1DCW")
        if self._experiment is not None:
            self.job_type.is_pol = self._experiment.is_pol
            self.job_type.is_tof = self._experiment.is_tof
            self.job_type.is_single_crystal = self._experiment.is_single_crystal

        # check if passed job_type is compatible with the experiment
        if job_type is not None:
            if self.job_type.type != job_type.type:
                raise ValueError("Job type does not match the experiment.")
        

    @property
    def sample(self):
        return self._sample
    
    @sample.setter
    def sample(self, value: Union[Sample, None]):
        self._sample = value

    @property
    def experiment(self):
        return self._experiment
    
    @experiment.setter
    def experiment(self, value: Union[Experiment, None]):
        self._experiment = value

    @property
    def analysis(self):
        return self._analysis

    @analysis.setter
    def analysis(self, value: Union[Analysis, None]):
        self._analysis = value

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

    def set_job_from_file(self, file_url):
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
    @classmethod
    def from_cif_file(cls, phase=None, experiment=None):
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

    def add_experiment_from_files(self, file_url):
        '''
        Add an experiment to the job from a CIF file.
        '''
        self.experiment = Experiment.from_cif(file_url)

    def add_sample_from_file(self, file_url):
        '''
        Add a sample to the job from a CIF file.
        '''
        self.sample = Sample.from_cif(file_url)

    def add_analysis_from_file(self, file_url):
        '''
        Add an analysis to the job from a CIF file.
        '''
        self.analysis = Analysis.from_cif(file_url)

    ###### CIF RELATED METHODS ######

    def __str__(self):
        return f"Job: {self._name}"

    def __repr__(self):
        return self.__str__()



