# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>


class ExperimentType:
    """
    Specification of the diffraction job type.

    Available types are:
    sample type:
        powder: pd (Default)
        single crystal: sc
    beam type:
        continuous wave: cwl (Default)
        time-of-flight: tof
    dimensionality:
        1D: 1d (Default)
        2D: 2d
    radiation type:
        neutrons: neut (Default)
        x-ray: xray
    polarization:
        unpolarized: unp (Default)
        polarized: pol
        longitudinal polarized: lpa
        spherical polarimetry: snp

    String-based specification can be provided in any order, in any combination.
    Example:
    a = ExperimentType("pd-cwl-unp-1d-xray")
    b = ExperimentType("cwl-unp-neut")
    c = ExperimentType("tof")

    """

    # Sample type
    STR_POWDER = 'pd'
    STR_SINGLE_CRYSTAL = 'sc'
    # Beam type
    STR_CW = 'cwl'
    STR_TOF = 'tof'
    # Dimensionality
    STR_1D = '1d'
    STR_2D = '2d'
    # Radiation type
    STR_XRAYS = 'xray'
    STR_NEUTRONS = 'neut'
    # Polarization
    STR_POL = 'pol'
    STR_UPOL = 'unp'
    STR_LPOL = 'lpa'
    STR_SPOL = 'snp'

    # Default values
    DEFAULT_TYPE = 'pd-cwl-unp-1d-neut'

    def __init__(self, experiment_type: str = ''):
        # Initialize the job type flags
        self.init_flags()
        # initialize the job type with defaults
        self.parse_experiment_type(self.DEFAULT_TYPE)
        # Modify the job type if a string is provided
        if experiment_type:
            self.parse_experiment_type(experiment_type)

    @property
    def type(self):
        return self.type_str

    @type.setter
    def type(self, value):
        self.parse_experiment_type(value)

    def init_flags(self):
        """
        Initialize the job type flags
        """
        self._is_pd = False
        self._is_sc = False
        self._is_cwl = False
        self._is_tof = False
        self._is_1d = False
        self._is_2d = False
        self._is_xray = False
        self._is_neut = False
        self._is_pol = False
        self._is_unp = False
        self._is_lpa = False
        self._is_snp = False

    @property
    def is_pd(self):
        return self._is_pd

    @is_pd.setter
    def is_pd(self, value):
        self._is_pd = value
        self._is_sc = not value
        self.validate()

    @property
    def is_sc(self):
        return self._is_sc

    @is_sc.setter
    def is_sc(self, value):
        self._is_sc = value
        self._is_pd = not value
        self.validate()

    @property
    def is_cwl(self):
        return self._is_cwl

    @is_cwl.setter
    def is_cwl(self, value):
        self._is_cwl = value
        self._is_tof = not value
        self.validate()

    @property
    def is_tof(self):
        return self._is_tof

    @is_tof.setter
    def is_tof(self, value):
        self._is_tof = value
        self._is_cwl = not value
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
        self._is_unp = not value
        self.validate()

    @property
    def is_xray(self):
        return self._is_xray

    @is_xray.setter
    def is_xray(self, value):
        self._is_xray = value
        self._is_neut = not value
        self.validate()

    @property
    def is_neut(self):
        return self._is_neut

    @is_neut.setter
    def is_neut(self, value):
        self._is_neut = value
        self._is_xray = not value
        self.validate()

    @property
    def is_unp(self):
        return self._is_unp

    @is_unp.setter
    def is_unp(self, value):
        self._is_unp = value
        self._is_pol = not value
        self.validate()

    @property
    def is_lpa(self):
        return self._is_lpa

    @is_lpa.setter
    def is_lpa(self, value):
        self._is_lpa = value
        self._is_snp = not value
        self.validate()

    @property
    def is_snp(self):
        return self._is_snp

    @is_snp.setter
    def is_snp(self, value):
        self._is_snp = value
        self._is_lpa = not value
        self.validate()

    def parse_experiment_type(self, experiment_type: str):
        # this will parse the substrings of the job type
        # and amend the existing job type

        # split the string into a list of flags
        tokens = experiment_type.split('-')
        # check for the presence of each flag
        for token in tokens:
            token = token.lower()
            if hasattr(self, f'_is_{token}'):
                setattr(self, f'is_{token}', True)
            else:
                raise ValueError(f'Invalid job type flag: {token}')
        self.validate()

    def to_typestr(self) -> None:
        """
        Convert the job type to a string
        """
        sample_flag = self.STR_POWDER if self._is_pd else self.STR_SINGLE_CRYSTAL
        beam_flag = self.STR_CW if self._is_cwl else self.STR_TOF
        dim_flag = self.STR_1D if self._is_1d else self.STR_2D
        radiation_flag = self.STR_XRAYS if self._is_xray else self.STR_NEUTRONS
        pol_flag = self.STR_UPOL
        if self._is_pol:
            pol_flag = self.STR_POL
        elif self._is_lpa:
            pol_flag = self.STR_LPOL
        elif self._is_snp:
            pol_flag = self.STR_SPOL
        self.type_str = f'{sample_flag}-{beam_flag}-{pol_flag}-{dim_flag}-{radiation_flag}'

    def validate(self):
        """
        Validate the job type
        """
        if self._is_pd and self._is_sc:
            raise ValueError('Job type can not be both powder and single crystal')
        if self._is_cwl and self._is_tof:
            raise ValueError('Job type can not be both CWL and TOF')
        if self._is_1d and self._is_2d:
            raise ValueError('Job type can not be both 1D and 2D')
        if self._is_pol and self._is_unp:
            raise ValueError('Job type can not be both polarized and unpolarized')
        if self._is_xray and self._is_neut:
            raise ValueError('Job type can not be both X-rays and Neutrons')
        self.to_typestr()

    def __str__(self):
        return f'Job type: {self.type_str}'
