#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction


from easyCore.Datasets.xarray import xr
from easyCore.Objects.Job.Theory import TheoryBase as coreSample

# this really should be easyDiffractionLib.sample.Sample

class Sample(coreSample):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, name: str, dataset: xr.Dataset = None, *args, **kwargs):
        super(Sample, self).__init__(name, *args, **kwargs)
        self._name = name
        self._simulation_prefix = "sim_"
        self._dataset = dataset if dataset is not None else xr.Dataset()

    @staticmethod
    def from_cif(cif_file: str):
        """
        Load the sample from a CIF file
        """
        # TODO: Implement this
        return Sample("Sample")

    # required dunder methods
    def __str__(self):
        return f"Sample: {self._name}"
    
    def as_dict(self, skip: list = []) -> dict:
        this_dict = super(Sample, self).as_dict(skip=skip)
        return this_dict
