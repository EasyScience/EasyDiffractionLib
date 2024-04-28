import pytest

import easydiffraction as ed
from easydiffraction.interface import InterfaceFactory
from easydiffraction.Job import DiffractionJob as Job
from easydiffraction.Profiles.Analysis import Analysis
from easydiffraction.Profiles.Experiment import Experiment
from easydiffraction.Profiles.JobType import JobType

# from easydiffraction.Profiles.Sample import Sample
from easydiffraction.sample import Sample


def test_job_init():
    j = Job()
    assert j.name == "Job"
    assert isinstance(j.interface, InterfaceFactory)
    assert isinstance(j.sample, Sample)
    assert isinstance(j.experiment, Experiment)
    assert isinstance(j.analysis, Analysis)
    assert j.type.type_str == "pd-cwl-unp-1d-neut"

def test_job_with_name():
    j = Job("test")
    assert j.name == "test"

def test_job_direct_import():
    j = ed.Job()
    assert j.name == "Job"

def test_powder1dcw():
    j = Job(type=JobType())
    assert j.type.is_pd
    assert j.type.is_cwl
    assert j.type.is_1d

def test_switch_job_TOF():
    j = Job(type="pd-cwl-unp")
    j.type.type = "tof"
    assert j.type.is_tof
    assert j.type.is_pd
    assert j.type.is_1d

def test_switch_job_TOF_2():
    j = Job(type=JobType("pd-cwl-unp"))
    j.type.is_tof = True
    assert j.type.is_tof
    assert j.type.is_pd
    assert j.type.is_1d

def test_get_job_from_file():
    j = Job()
    j.set_job_from_file("examples/d1a.cif")
    assert j.name == "d1a"
    assert j.type.type_str == "pd-cwl-unp-1d-neut"
    assert j.type.is_pd
    assert j.type.is_cwl
    assert j.type.is_1d
    assert j.type.is_unp

def test_get_pol_job_from_file():
    j = Job("test")
    j.set_job_from_file("examples/PolNPD5T.cif")
    assert j.name == "PolNPD5T"
    assert j.type.type_str == "pd-cwl-pol-1d-neut"
    assert j.type.is_pol
    assert not j.type.is_unp

def test_add_experiment_from_file():
    j = Job("test")
    j.add_experiment_from_file("examples/d1a.cif")
    assert j.experiment._name == "Experiment"
    assert isinstance(j.experiment, Experiment)

def test_add_sample_from_file():
    j = Job("test")
    j.add_sample_from_file("examples/PbSO4.cif")
    assert j.sample._name == "easySample"
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
        _ = Job("test", experiment=experiment, type="pd-cwl-unp-1d-neut")

def test_sample_assignment():
    # assure that sample is deep copied
    sample = Sample("test_sample")
    j = Job("test", sample=sample)
    # assert id(j.sample) != id(sample) # TODO fix after fixing deepcopy
    assert j.sample._name == sample.name

    j2 = Job("test")
    j2.sample = sample
    # assert id(j2.sample) != id(sample) # TODO fix after fixing deepcopy
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

