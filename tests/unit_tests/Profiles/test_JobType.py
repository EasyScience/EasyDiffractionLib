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
    assert job_type.type_str == "Powder2DCW"
    assert job_type.type == "Powder2DCW"
    assert job_type.type_to_string() == "Powder2DCW"
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
    assert job_type.type_str == "Powder1DTOF"
    assert job_type.type == "Powder1DTOF"
    assert job_type.type_to_string() == "Powder1DTOF"
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
    job_type._is_crystal = True
    try:
        job_type.validate()
    except ValueError as e:
        assert str(e) == "Job type can not be both powder and single crystal"

    job_type = JobType("Powder1DCW")
    job_type._is_tof = True
    try:
        job_type.validate()
    except ValueError as e:
        assert str(e) == "Job type can not be both CW and TOF"

    job_type = JobType("Powder1DCW")
    job_type._is_1d = False
    try:
        job_type.validate()
    except ValueError as e:
        assert str(e) == "Job type can not be both 1D and 2D"

    job_type = JobType("Powder1DCW")
    job_type._is_powder = True
    job_type._is_single_crystal = False
    try:
        job_type.validate()
    except ValueError as e:
        assert str(e) == "Job type can not be both powder and single crystal"

    job_type = JobType("Powder1DCW")
    job_type._is_cw = True
    job_type._is_tof = False
    try:
        job_type.validate()
    except ValueError as e:
        assert str(e) == "Job type can not be both CW and TOF"

    job_type = JobType("PolPowder1DCW")
    job_type._is_upol = True
    try:
        job_type.validate()
    except ValueError as e:
        assert str(e) == "Job type can not be both pol and unpolarized"

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

