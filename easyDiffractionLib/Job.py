#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors <support@easydiffraction.org>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easyDiffraction project <https://github.com/easyScience/easyDiffraction


# easyScience
from easyCore.Datasets.xarray import xr
from easyCore.Objects.Job.Job import Job as easyCoreJob

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
        profileClass,
        job_type: JobType,
        datastore: xr.Dataset,
        phases=None,
        parameters=None,
        pattern=None,
        interface=None,
    ):
        if interface is None:
            interface = InterfaceFactory()
        super(DiffractionJob, self).__init__(
            name,
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

        # components
        self._sample = Sample()
        self._experiment = Experiment()
        self._analysis = Analysis()
        self._summary = None  # TODO: implement
        self._info = None # TODO: implement


        # Instead of creating separate classes for all techniques,
        # as in old EDL (Powder1DCW, PolPowder1DCW, Powder1DTOF, etc)
        # let's have these as attributes of the Job class
        self.job_type = job_type
        

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



