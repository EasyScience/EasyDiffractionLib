#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction


from easyCore.Objects.Job.Analysis import AnalysisBase as coreAnalysis


class Analysis(coreAnalysis):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, name: str, *args, **kwargs):
        super(Analysis, self).__init__(name, *args, **kwargs)
        self.name = name

    # required dunder methods
    def __str__(self):
        return f"Experiment: {self.name}"
    
    