#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors <support@easydiffraction.org>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easyDiffraction project <https://github.com/easyScience/easyDiffraction

class JobType():
    """
    Specification of the diffraction job type
    Example:
    a = JobType("Powder1DCW")
    a.is_powder = True
    a.is_single_crystal = False
    a.is_cw = True
    a.is_tof = False
    a.is_1d = True
    a.is_2d = False
    """
    STR_POWDER = "Powder"
    STR_SINGLE_CRYSTAL = "Crystal"
    STR_CW = "CW"
    STR_TOF = "TOF"
    STR_1D = "1D"
    STR_2D = "2D"

    def __init__(self, job_type: str):
        self.type_str = job_type
        self.parse_job_type(job_type)

    @property
    def job_type(self):
        return self._job_type

    @job_type.setter
    def job_type(self, value):
        self._job_type = value

    def parse_job_type(self, job_type: str):
        """
        Convert the job type string to a JobType object
        """
        self.is_powder = self.STR_POWDER in job_type.lower()
        self.is_single_crystal = not self.is_powder
        self.is_cw = self.STR_CW in job_type
        self.is_tof = self.STR_TOF in job_type
        self.is_1d = self.STR_1D in job_type
        self.is_2d = self.STR_2D in job_type
        self.validate()

    def type_to_string(self):
        """
        Convert the job type to a string
        """
        powder_flag = self.STR_POWDER if self.is_powder else self.STR_SINGLE_CRYSTAL
        cw_flag = self.STR_CW if self.is_cw else self.STR_TOF
        dim_flag = self.STR_1D if self.is_1d else self.STR_2D
        self.type_str = f"{powder_flag}{dim_flag}{cw_flag}"
        return self.type_str

    def validate(self):
        """
        Validate the job type
        """
        if self.is_powder and self.is_single_crystal:
            raise ValueError("Job type can not be both powder and single crystal")
        if self.is_cw and self.is_tof:
            raise ValueError("Job type can not be both CW and TOF")
        if self.is_1d and self.is_2d:
            raise ValueError("Job type can not be both 1D and 2D")

    def __str__(self):
        return f"Job type: {self.type_str}"