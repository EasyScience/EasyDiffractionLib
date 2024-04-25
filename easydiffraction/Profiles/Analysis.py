#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction


from easyscience.Objects.Job.Analysis import AnalysisBase as coreAnalysis


class Analysis(coreAnalysis):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, name: str, *args, **kwargs):
        super(Analysis, self).__init__(name, *args, **kwargs)
        self.name = name

    @staticmethod
    def from_cif(cif_file: str):
        """
        Load the analysis from a CIF file
        """
        # TODO: Implement this
        return Analysis("Analysis")

    # required dunder methods
    def __str__(self):
        return f"Analysis: {self.name}"
    
    