#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors <support@easydiffraction.org>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easyDiffraction project <https://github.com/easyScience/easyDiffraction


# easyScience
from easyCore.Datasets.xarray import xr
from easyCore.Objects.Job.Job import Job as easyCoreJob
from gemmi import cif

from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Profiles.Analysis import Analysis
from easyDiffractionLib.Profiles.Experiment import Experiment
from easyDiffractionLib.Profiles.JobType import JobType
from easyDiffractionLib.Profiles.Sample import Sample


class DiffractionJob(easyCoreJob):
    """
    This class is the base class for all diffraction specific jobs
    """
    def __init__(
        self,
        name: str,
        job_type: JobType = None,
        datastore: xr.Dataset = None,
        phases=None,
        interface=None,
    ):
        if interface is None:
            interface = InterfaceFactory()
        super(DiffractionJob, self).__init__(
            name,
            interface=interface,
        )

        self.cif_string = ""
        self.datastore = datastore if datastore is not None else xr.Dataset()
        self._name = name if name is not None else "Job"

        if phases is not None and self.phases != phases:
            self.phases = phases
        # The following assignment is necessary for proper binding
        self.interface = interface

        # components
        self._sample = Sample()
        self._experiment = Experiment()
        self._analysis = Analysis()

        self._summary = None  # TODO: implement
        self._info = None # TODO: implement

        # Instead of creating separate classes for all techniques,
        # as in old EDL (Powder1DCW, PolPowder1DCW, Powder1DTOF, etc)
        # let's have these as attributes of the Job class
        if job_type is not None:
            self.job_type = job_type
        else: 
            self.job_type = JobType("Powder1DCW") #default
        

    @property
    def sample(self):
        return self._sample
    
    @sample.setter
    def sample(self, value):
        self._sample = value

    @property
    def experiment(self):
        return self._experiment
    
    @experiment.setter
    def experiment(self, value):
        self._experiment = value

    @property
    def analysis(self):
        return self._analysis

    @analysis.setter
    def analysis(self, value):
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

    def get_job_from_file(self, file_url):
        '''
        Get the job from a CIF file.

        Based on keywords in the CIF file, the job type is determined,
        the job is created and the data is loaded from the CIF file.
        '''
        block = cif.read(file_url).sole_block()
        self.cif_string = block.as_string()
        value_cwpol = block.find_value("_diffrn_radiation_polarization")
        value_tof = block.find_loop("_tof_meas_time")  or block.find_loop("_pd_meas_time_of_flight")
        value_cw = block.find_value("_setup_wavelength")

        if value_cwpol is not None:
            self.job_type.is_pol = True
        elif value_tof:
            self.job_type.is_tof = True
        elif value_cw is not None:
            self.job_type.is_cw = True
        else:
            raise ValueError("Could not determine job type from file.")

    def __str__(self):
        return f"Job: {self.name}"

    def __copy__(self):
        raise NotImplementedError("Copy not implemented")

    def __deepcopy__(self, memo):
        raise NotImplementedError("Deepcopy not implemented")

    def __eq__(self, other):
        raise NotImplementedError("Equality not implemented")

    def __ne__(self, other):
        raise NotImplementedError("Equality not implemented")

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Call not implemented")

    def __repr__(self):
        return self.__str__()



