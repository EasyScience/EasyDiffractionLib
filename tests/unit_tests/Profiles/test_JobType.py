import pytest

from easyDiffractionLib.Profiles.JobType import JobType


def test_JobType():
    job_type = JobType("Powder1DCW")
    assert job_type.is_powder
    assert not job_type.is_single_crystal
    assert job_type.is_cw
    assert not job_type.is_tof
    assert job_type.is_1d
    assert not job_type.is_2d
    assert job_type.type_str == "Powder1DCW"
    assert job_type.type == "Powder1DCW"
    assert job_type.type_to_string() == "Powder1DCW"
    assert not job_type.is_pol

    job_type = JobType("Crystal1DTOF")
    assert not job_type.is_powder 
    assert job_type.is_single_crystal 
    assert not job_type.is_cw 
    assert job_type.is_tof 
    assert job_type.is_1d 
    assert not job_type.is_2d 
    assert job_type.type_str == "Crystal1DTOF"
    assert job_type.type == "Crystal1DTOF"
    assert job_type.type_to_string() == "Crystal1DTOF"
    assert not job_type.is_pol

    job_type = JobType("PolPowder2DCW")
    assert job_type.is_powder 
    assert not job_type.is_single_crystal 
    assert job_type.is_cw 
    assert not job_type.is_tof 
    assert not job_type.is_1d 
    assert job_type.is_2d 
    assert job_type.type_str == "PolPowder2DCW"
    assert job_type.type == "PolPowder2DCW"
    assert job_type.type_to_string() == "PolPowder2DCW"
    assert job_type.is_pol

    job_type = JobType("Crystal2DTOF")
    assert not job_type.is_powder 
    assert job_type.is_single_crystal 
    assert not job_type.is_cw 
    assert job_type.is_tof 
    assert not job_type.is_1d 
    assert job_type.is_2d 
    assert job_type.type_str == "Crystal2DTOF"
    assert job_type.type == "Crystal2DTOF"
    assert job_type.type_to_string() == "Crystal2DTOF"
    assert not job_type.is_pol

    job_type = JobType("PolPowder1DTOF")
    assert job_type.is_powder 
    assert not job_type.is_single_crystal 
    assert not job_type.is_cw 
    assert job_type.is_tof 
    assert job_type.is_1d 
    assert not job_type.is_2d 
    assert job_type.type_str == "PolPowder1DTOF"
    assert job_type.type == "PolPowder1DTOF"
    assert job_type.type_to_string() == "PolPowder1DTOF"
    assert job_type.is_pol

    job_type = JobType("Crystal1DCW")
    assert not job_type.is_powder 
    assert job_type.is_single_crystal 
    assert job_type.is_cw 
    assert not job_type.is_tof 
    assert job_type.is_1d 
    assert not job_type.is_2d 
    assert job_type.type_str == "Crystal1DCW"
    assert job_type.type == "Crystal1DCW"
    assert job_type.type_to_string() == "Crystal1DCW"
    assert not job_type.is_pol

def test_Validate():
    job_type = JobType("Powder1DCW")
    job_type._is_single_crystal = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType("Powder1DCW")
    job_type._is_tof = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType("Powder1DCW")
    job_type._is_2d = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType("Powder1DCW")
    job_type._is_single_crystal = True
    with pytest.raises(ValueError):
        job_type.validate()

    job_type = JobType("Powder1DCW")
    job_type._is_tof = True
    with pytest.raises(ValueError):
        job_type.validate()

def test_Convert():
    job_type = JobType("Powder1DCW")
    job_type.type = "Crystal1DTOF"
    assert job_type.is_single_crystal

    job_type.type = "Crystal1DTOF"
    assert job_type.is_tof

    job_type.type = "Crystal2DTOF"
    assert job_type.is_2d

    job_type.type = "PolCrystal2DTOF"
    assert job_type.is_pol

