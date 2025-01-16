import os
import tempfile
from unittest.mock import MagicMock

import numpy as np
import numpy.testing as npt
import pytest

from easydiffraction.job.experiment.experiment import Experiment


@pytest.fixture
def setup_experiment():
    # Create a mock datastore
    mock_datastore = MagicMock()
    mock_datastore.store.easyscience.add_coordinate = MagicMock()
    mock_datastore.store.easyscience.add_variable = MagicMock()
    mock_datastore.store.easyscience.sigma_attach = MagicMock()

    # Initialize the Experiment class with the mock datastore
    experiment = Experiment(job_name='test_job', datastore=mock_datastore)
    return experiment, mock_datastore


def test_add_experiment_data(setup_experiment):
    experiment, mock_datastore = setup_experiment
    x = [1, 2, 3]
    y = [[10, 20, 30], [40, 50, 60]]
    e = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    experiment_name = 'exp1'

    experiment.add_experiment_data(x, y, e, experiment_name)

    coord_name = 'test_job_exp1_tth'
    mock_datastore.store.easyscience.add_coordinate.assert_called_with(coord_name, x)

    for j in range(len(y)):
        var_name = f'test_job_exp1_I{j}'
        mock_datastore.store.easyscience.add_variable.assert_any_call(var_name, [coord_name], y[j])
        mock_datastore.store.easyscience.sigma_attach.assert_any_call(var_name, e[j])


def test_add_experiment(setup_experiment):
    experiment, mock_datastore = setup_experiment
    data = np.array([[1, 10, 0.1], [2, 20, 0.2], [3, 30, 0.3]])
    experiment_name = 'exp2'

    # Create a temporary file with test data
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        np.savetxt(tmpfile.name, data)
        file_path = tmpfile.name

    experiment.add_experiment(experiment_name, file_path)

    coord_name = 'test_job_exp2_tth'
    # Manually check the call arguments
    add_coordinate_call = mock_datastore.store.easyscience.add_coordinate.call_args
    assert add_coordinate_call[0][0] == coord_name
    npt.assert_array_equal(add_coordinate_call[0][1], data[:, 0])

    for j in range(1, len(data), 2):
        var_name = f'test_job_exp2_I{j // 2}'
        add_variable_call = mock_datastore.store.easyscience.add_variable.call_args_list[j // 2]
        assert add_variable_call[0][0] == var_name
        assert add_variable_call[0][1] == [coord_name]
        npt.assert_array_equal(add_variable_call[0][2], data[:, j])

        sigma_attach_call = mock_datastore.store.easyscience.sigma_attach.call_args_list[j // 2]
        assert sigma_attach_call[0][0] == var_name
        npt.assert_array_equal(sigma_attach_call[0][1], data[:, j + 1])

    # Clean up the temporary file
    os.remove(file_path)
