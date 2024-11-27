import easydiffraction as ed
import numpy as np
from numpy.testing import assert_array_equal


def test_read_tof_cif_from_scipp() -> None:
    job = ed.Job(type="pd-neut-tof")
    job.add_experiment_from_file("tests/resources/scipp.cif")

    assert job.experiment.name == 'test_data'

    assert job.pattern.zero_shift.raw_value == 3.4
    assert job.parameters.dtt1.raw_value == 0.2
    assert job.parameters.dtt2.raw_value == -0.8

    assert_array_equal(job.experiment.x.data, np.array([1.2, 1.4, 2.3]))
    assert_array_equal(job.experiment.y.data, np.array([13.6, 26.0, 9.7]))
    assert_array_equal(job.experiment.e.data, np.array([0.8366600265340756, 1.0488088481701516, 0.7071067811865476]))
