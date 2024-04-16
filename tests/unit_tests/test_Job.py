import pytest

from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Job import DiffractionJob as Job
from easyDiffractionLib.Profiles.Analysis import Analysis
from easyDiffractionLib.Profiles.Experiment import Experiment
from easyDiffractionLib.Profiles.JobType import JobType
from easyDiffractionLib.Profiles.Sample import Sample


def test_job_init():
    j = Job("test")
    assert j.name == "test"
    assert isinstance(j.interface, InterfaceFactory)
    assert isinstance(j.sample, Sample)
    assert isinstance(j.experiment, Experiment)
    assert isinstance(j.analysis, Analysis)
    assert j.job_type.type_str == "Powder1DCW"


def test_powder1dcw():
    j = Job("test", job_type=JobType("Powder1DCW"))
    assert j.job_type.is_powder
    assert j.job_type.is_cw
    assert j.job_type.is_1d

def test_switch_job_TOF():
    j = Job("test", job_type=JobType("Powder1DCW"))
    j.job_type = JobType("Powder1DTOF")
    assert j.job_type.is_tof
    assert j.job_type.is_powder
    assert j.job_type.is_1d

def test_switch_job_TOF_2():
    j = Job("test", job_type=JobType("Powder1DCW"))
    j.job_type.is_tof = True
    assert j.job_type.is_tof
    assert j.job_type.is_powder
    assert j.job_type.is_1d

def test_get_job_from_file():
    j = Job("test")
    j.set_job_from_file("examples/d1a.cif")
    assert j.name == "d1a"
    assert j.job_type.type_str == "Powder1DCW"
    assert j.job_type.is_powder
    assert j.job_type.is_cw
    assert j.job_type.is_1d

def test_add_experiment_from_file():
    j = Job("test")
    j.add_experiment_from_file("examples/d1a.cif")
    assert j.experiment._name == "Experiment"
    assert isinstance(j.experiment, Experiment)

def test_add_sample_from_file():
    j = Job("test")
    j.add_sample_from_file("examples/d1a.cif")
    assert j.sample._name == "Sample"
    assert isinstance(j.sample, Sample)

def test_add_analysis_from_file():
    j = Job("test")
    j.add_analysis_from_file("examples/d1a.cif")
    assert j.analysis._name == "Analysis"
    assert isinstance(j.analysis, Analysis)

def test_wrong_type_passed():
    experiment = Experiment("test")
    # test that Job throws
    with pytest.raises(ValueError):
        _ = Job("test", experiment=experiment, job_type=JobType("Powder1DCW"))

def test_sample_assignment():
    # assure that sample is deep copied
    sample = Sample("test_sample")
    j = Job("test", sample=sample)
    assert id(j.sample) != id(sample)
    assert j.sample._name == sample.name

    j2 = Job("test")
    j2.sample = sample
    assert id(j2.sample) != id(sample)
    assert j2.sample._name == sample.name

def test_experiment_assignment():
    # assure that experiment is deep copied
    experiment = Experiment("test")
    j = Job("test", experiment=experiment)
    assert id(j.experiment) != id(experiment)

    j2 = Job("test")
    j2.experiment = experiment
    assert id(j2.experiment) != id(experiment)

def test_analysis_assignment():
    # assure that analysis is deep copied
    analysis = Analysis("test")
    j = Job("test", analysis=analysis)
    assert id(j.analysis) != id(analysis)

    j2 = Job("test")
    j2.analysis = analysis
    assert id(j2.analysis) != id(analysis)

