import pytest

from easydiffraction.Profiles.JobType import JobType


def test_JobType():
    job_type = JobType("pd-cwl-unp-1d-neut")
    assert job_type.is_pd
    assert not job_type.is_sc
    assert job_type.is_cwl
    assert not job_type.is_tof
    assert job_type.is_1d
    assert not job_type.is_2d
    assert job_type.type_str == "pd-cwl-unp-1d-neut"
    assert job_type.type == "pd-cwl-unp-1d-neut"
    assert not job_type.is_pol

    job_type = JobType("sc-tof")
    assert not job_type.is_pd
    assert job_type.is_sc
    assert not job_type.is_cwl
    assert job_type.is_tof 
    assert job_type.is_1d 
    assert not job_type.is_2d 
    assert job_type.type_str == "sc-tof-unp-1d-neut"
    assert job_type.type == "sc-tof-unp-1d-neut"
    assert not job_type.is_pol

    job_type = JobType("pd-cwl-pol-2d-neut")
    assert job_type.is_pd 
    assert not job_type.is_sc 
    assert job_type.is_cwl 
    assert not job_type.is_tof 
    assert not job_type.is_1d 
    assert job_type.is_2d 
    assert job_type.type_str == "pd-cwl-pol-2d-neut"
    assert job_type.type == "pd-cwl-pol-2d-neut"
    assert job_type.is_pol

    job_type = JobType("sc-tof")
    assert not job_type.is_pd 
    assert job_type.is_sc 
    assert not job_type.is_cwl 
    assert job_type.is_tof 
    assert job_type.is_1d 
    assert not job_type.is_2d 
    assert job_type.type_str == "sc-tof-unp-1d-neut"
    assert job_type.type == "sc-tof-unp-1d-neut"
    assert not job_type.is_pol

    job_type = JobType("xray")
    assert job_type.is_pd
    assert not job_type.is_sc
    assert job_type.type_str == "pd-cwl-unp-1d-xray"
    assert job_type.type == "pd-cwl-unp-1d-xray"
    assert job_type.is_xray

def test_Validate():
    job_type = JobType("")
    job_type._is_sc = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType()
    job_type._is_tof = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType()
    job_type._is_2d = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType()
    job_type._is_sc = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType()
    job_type._is_tof = True
    with pytest.raises(ValueError):
        job_type.validate()

def test_Convert():
    job_type = JobType()
    job_type.type = "sc"
    assert job_type.is_sc

    job_type.type = "tOF"
    assert job_type.is_tof

    job_type.type = "2D-Pol"
    assert job_type.is_2d
    assert job_type.is_pol

    # finally assure the final type
    assert job_type.type_str == "sc-tof-pol-2d-neut"
 

