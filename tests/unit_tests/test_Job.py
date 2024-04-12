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
    j = Job.from_file("examples/PbSO4.cif")
    assert j.name == "PbSO4"
    assert j.job_type.type_str == "Powder1DCW"
    assert j.job_type.is_powder
    assert j.job_type.is_cw
    assert j.job_type.is_1d
