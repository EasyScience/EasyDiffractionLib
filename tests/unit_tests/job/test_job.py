import copy

import numpy as np
import pytest

import easydiffraction as ed
from easydiffraction.calculators.wrapper_factory import WrapperFactory
from easydiffraction.job.analysis.analysis import Analysis
from easydiffraction.job.experiment.experiment import Experiment
from easydiffraction.job.experiment.experiment_type import ExperimentType
from easydiffraction.job.experiment.pd_1d import Instrument1DCWParameters
from easydiffraction.job.experiment.pd_1d import Instrument1DTOFParameters
from easydiffraction.job.experiment.pd_1d import PolPowder1DParameters
from easydiffraction.job.experiment.pd_1d import Powder1DParameters
from easydiffraction.job.job import DiffractionJob as Job
from easydiffraction.job.old_sample.old_sample import Sample


def test_job_init():
    j = Job()
    assert j.name == 'sim_'
    assert isinstance(j.interface, WrapperFactory)
    assert isinstance(j.sample, Sample)
    assert isinstance(j.experiment, Experiment)
    assert isinstance(j.analysis, Analysis)
    assert j.type.type_str == 'pd-cwl-unp-1d-neut'


def test_job_with_name():
    j = Job('test')
    assert j.name == 'test'


def test_job_direct_import():
    j = ed.Job()
    assert j.name == 'sim_'


def test_powder1dcw():
    j = Job(type=ExperimentType())
    assert j.type.is_pd
    assert j.type.is_cwl
    assert j.type.is_1d


def test_switch_job_TOF():
    j = Job(type='pd-cwl-unp')
    j.type.type = 'tof'
    assert j.type.is_tof
    assert j.type.is_pd
    assert j.type.is_1d


def test_switch_job_TOF_2():
    j = Job(type=ExperimentType('pd-cwl-unp'))
    j.type.is_tof = True
    assert j.type.is_tof
    assert j.type.is_pd
    assert j.type.is_1d
    assert isinstance(j.parameters, Instrument1DCWParameters)
    assert isinstance(j.sample.pattern, Powder1DParameters)


def test_job_tof():
    j = Job(type='pol-tof')
    assert j.type.is_tof
    assert not j.type.is_cwl
    assert j.type.is_pol
    assert isinstance(j.parameters, Instrument1DTOFParameters)
    assert isinstance(j.experiment.pattern, PolPowder1DParameters)


def test_get_job_from_file():
    j = Job()
    j.set_job_from_file('tests/data/d1a.cif')
    assert j.name == 'd1a'
    assert j.type.type_str == 'pd-cwl-unp-1d-neut'
    assert j.type.is_pd
    assert j.type.is_cwl
    assert j.type.is_1d
    assert j.type.is_unp


def test_get_pol_job_from_file():
    j = Job('test')
    j.set_job_from_file('tests/data/PolNPD5T.cif')
    assert j.name == 'PolNPD5T'
    assert j.type.type_str == 'pd-cwl-pol-1d-neut'
    assert j.type.is_pol
    assert not j.type.is_unp


def test_add_experiment_from_file():
    j = Job('test')
    j.add_experiment_from_file('tests/data/d1a.cif')
    assert j.experiment._name == 'd1a'
    assert isinstance(j.experiment, Experiment)


def test_add_sample_from_file():
    j = Job('test')
    j.add_sample_from_file('tests/data/PbSO4.cif')
    assert j.sample._name == 'easySample'
    assert isinstance(j.sample, Sample)


# FAILED tests/unit_tests/test_Job.py::test_add_analysis_from_file -
# ValueError: Object name Analysis_1 already exists in the graph.
def _test_add_analysis_from_file():
    j = Job('test')
    j.add_analysis_from_file('tests/data/d1a.cif')
    assert j.analysis._name == 'Analysis'
    assert isinstance(j.analysis, Analysis)


def test_wrong_type_passed():
    experiment = Experiment('test')
    # test that Job throws
    with pytest.raises(ValueError):
        _ = Job('test', experiment=experiment, type='pd-cwl-unp-1d-neut')


def test_sample_assignment():
    # assure that sample is deep copied
    sample = Sample('test_sample')
    j = Job('test', sample=sample)
    # assert id(j.sample) != id(sample) # TODO fix after fixing deepcopy
    assert j.sample._name == sample.name

    j2 = Job('test')
    j2.sample = sample
    # assert id(j2.sample) != id(sample) # TODO fix after fixing deepcopy
    assert j2.sample._name == sample.name


def test_experiment_assignment():
    # assure that experiment is deep copied
    experiment = Experiment('test')
    j = Job('test', experiment=experiment)
    assert id(j.experiment) != id(experiment)

    j2 = Job('test')
    j2.experiment = experiment
    assert id(j2.experiment) != id(experiment)


# FAILED tests/unit_tests/test_Job.py::test_analysis_assignment -
# ValueError: Object name Analysis_4 already exists in the graph.
def _test_analysis_assignment():
    # assure that analysis is deep copied
    analysis = Analysis('analysis')
    j = Job('test', analysis=analysis)
    assert id(j.analysis) != id(analysis)

    j2 = Job('test')
    j2.analysis = analysis
    assert id(j2.analysis) != id(analysis)


def test_calculate_profile():
    j = Job('test')
    j.add_sample_from_file('tests/data/PbSO4.cif')
    x_data = np.linspace(20, 170, 500)
    y = j.calculate_profile(x=x_data)
    assert len(y) == len(x_data)
    assert y[0] == pytest.approx(0.0, abs=1e-5)
    assert np.max(y) == pytest.approx(11206, abs=1)


# FAILED tests/unit_tests/test_Job.py::test_copy - ValueError: Object name Analysis_6 already exists in the graph.
def _test_copy():
    j = Job('test')
    j.add_sample_from_file('tests/data/PbSO4.cif')
    j2 = copy.copy(j)
    assert id(j) != id(j2)
    assert j2.name == j.name
    assert j2.sample._name == j.sample._name
    assert j2.experiment._name == j.experiment._name
    assert j2.analysis._name == j.analysis._name
    assert j2.type.type_str == j.type.type_str
    assert j2.parameters == j.parameters
