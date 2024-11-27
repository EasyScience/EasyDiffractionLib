import pytest

from easydiffraction.job.experiment.experiment_type import ExperimentType


def test_ExperimentType():
    experiment_type = ExperimentType('pd-cwl-unp-1d-neut')
    assert experiment_type.is_pd
    assert not experiment_type.is_sc
    assert experiment_type.is_cwl
    assert not experiment_type.is_tof
    assert experiment_type.is_1d
    assert not experiment_type.is_2d
    assert experiment_type.type_str == 'pd-cwl-unp-1d-neut'
    assert experiment_type.type == 'pd-cwl-unp-1d-neut'
    assert not experiment_type.is_pol

    experiment_type = ExperimentType('sc-tof')
    assert not experiment_type.is_pd
    assert experiment_type.is_sc
    assert not experiment_type.is_cwl
    assert experiment_type.is_tof
    assert experiment_type.is_1d
    assert not experiment_type.is_2d
    assert experiment_type.type_str == 'sc-tof-unp-1d-neut'
    assert experiment_type.type == 'sc-tof-unp-1d-neut'
    assert not experiment_type.is_pol

    experiment_type = ExperimentType('pd-cwl-pol-2d-neut')
    assert experiment_type.is_pd
    assert not experiment_type.is_sc
    assert experiment_type.is_cwl
    assert not experiment_type.is_tof
    assert not experiment_type.is_1d
    assert experiment_type.is_2d
    assert experiment_type.type_str == 'pd-cwl-pol-2d-neut'
    assert experiment_type.type == 'pd-cwl-pol-2d-neut'
    assert experiment_type.is_pol

    experiment_type = ExperimentType('sc-tof')
    assert not experiment_type.is_pd
    assert experiment_type.is_sc
    assert not experiment_type.is_cwl
    assert experiment_type.is_tof
    assert experiment_type.is_1d
    assert not experiment_type.is_2d
    assert experiment_type.type_str == 'sc-tof-unp-1d-neut'
    assert experiment_type.type == 'sc-tof-unp-1d-neut'
    assert not experiment_type.is_pol

    experiment_type = ExperimentType('xray')
    assert experiment_type.is_pd
    assert not experiment_type.is_sc
    assert experiment_type.type_str == 'pd-cwl-unp-1d-xray'
    assert experiment_type.type == 'pd-cwl-unp-1d-xray'
    assert experiment_type.is_xray


def test_Validate():
    experiment_type = ExperimentType('')
    experiment_type._is_sc = True
    with pytest.raises(ValueError):
        experiment_type.validate()

    experiment_type = ExperimentType()
    experiment_type._is_tof = True
    with pytest.raises(ValueError):
        experiment_type.validate()

    experiment_type = ExperimentType()
    experiment_type._is_2d = True
    with pytest.raises(ValueError):
        experiment_type.validate()

    experiment_type = ExperimentType()
    experiment_type._is_sc = True
    with pytest.raises(ValueError):
        experiment_type.validate()

    experiment_type = ExperimentType()
    experiment_type._is_tof = True
    with pytest.raises(ValueError):
        experiment_type.validate()


def test_Convert():
    experiment_type = ExperimentType()
    experiment_type.type = 'sc'
    assert experiment_type.is_sc

    experiment_type.type = 'tOF'
    assert experiment_type.is_tof

    experiment_type.type = '2D-Pol'
    assert experiment_type.is_2d
    assert experiment_type.is_pol

    # finally assure the final type
    assert experiment_type.type_str == 'sc-tof-pol-2d-neut'
