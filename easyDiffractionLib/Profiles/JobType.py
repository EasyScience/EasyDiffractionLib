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
    a.is_pol = False
    a.is_upol = False
    """
    STR_POWDER = "Powder"
    STR_SINGLE_CRYSTAL = "Crystal"
    STR_CW = "CW"
    STR_TOF = "TOF"
    STR_1D = "1D"
    STR_2D = "2D"
    STR_POL = "Pol"
    STR_UPOL = "" #unique

    def __init__(self, job_type: str):
        self.type_str = job_type
        self.parse_job_type(job_type)

    @property
    def type(self):
        return self.type_str

    @type.setter
    def type(self, value):
        self.type_str = value
        self.parse_job_type(value)

    @property
    def is_powder(self):
        return self._is_powder
    
    @is_powder.setter
    def is_powder(self, value):
        self._is_powder = value
        self._is_single_crystal = not value
        self.validate()
    
    @property
    def is_single_crystal(self):
        return self._is_single_crystal
    
    @is_single_crystal.setter
    def is_single_crystal(self, value):
        self._is_single_crystal = value
        self._is_powder = not value
        self.validate()

    @property
    def is_cw(self):
        return self._is_cw
    
    @is_cw.setter
    def is_cw(self, value):
        self._is_cw = value
        self._is_tof = not value
        self.validate()

    @property
    def is_tof(self):
        return self._is_tof

    @is_tof.setter
    def is_tof(self, value):
        self._is_tof = value
        self._is_cw = not value
        self.validate()

    @property
    def is_1d(self):
        return self._is_1d

    @is_1d.setter
    def is_1d(self, value):
        self._is_1d = value
        self._is_2d = not value
        self.validate()

    @property
    def is_2d(self):
        return self._is_2d
    
    @is_2d.setter
    def is_2d(self, value):
        self._is_2d = value
        self._is_1d = not value
        self.validate()

    @property
    def is_pol(self):
        return self._is_pol
    
    @is_pol.setter
    def is_pol(self, value):
        self._is_pol = value
        self._is_upol = not value
        self.validate()

    @property
    def is_upol(self):
        return self._is_upol
    
    @is_upol.setter
    def is_upol(self, value):
        self._is_upol = value
        self._is_pol = not value
        self.validate()


    def parse_job_type(self, job_type: str):
        """
        Convert the job type string to a JobType object
        """
        self._is_powder = self.STR_POWDER in job_type
        self._is_single_crystal = not self.is_powder
        self._is_cw = self.STR_CW in job_type
        self._is_tof = self.STR_TOF in job_type
        self._is_1d = self.STR_1D in job_type
        self._is_2d = self.STR_2D in job_type
        self._is_pol = self.STR_POL in job_type
        self._is_upol = not self.is_pol
        self.validate()

    def type_to_typestr(self) -> None:
        """
        Convert the job type to a string
        """
        powder_flag = self.STR_POWDER if self._is_powder else self.STR_SINGLE_CRYSTAL
        cw_flag = self.STR_CW if self._is_cw else self.STR_TOF
        dim_flag = self.STR_1D if self._is_1d else self.STR_2D
        pol_flag = self.STR_POL if self._is_pol else self.STR_UPOL
        self.type_str = f"{pol_flag}{powder_flag}{dim_flag}{cw_flag}"

    def validate(self):
        """
        Validate the job type
        """
        if self._is_powder and self._is_single_crystal:
            raise ValueError("Job type can not be both powder and single crystal")
        if self._is_cw and self._is_tof:
            raise ValueError("Job type can not be both CW and TOF")
        if self._is_1d and self._is_2d:
            raise ValueError("Job type can not be both 1D and 2D")
        if self._is_pol and self._is_upol:
            raise ValueError("Job type can not be both polarized and unpolarized")
        self.type_to_typestr()

    def __str__(self):
        return f"Job type: {self.type_str}"