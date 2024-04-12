#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction


from easyCore.Objects.Job.Theory import TheoryBase as coreSample


class Sample(coreSample):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, name: str, *args, **kwargs):
        super(Sample, self).__init__(name, *args, **kwargs)
        self._name = name

    # required dunder methods
    def __str__(self):
        return f"Experiment: {self._name}"
    
    def as_dict(self, skip: list = []) -> dict:
        this_dict = super(Sample, self).as_dict(skip=skip)
        return this_dict
