#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction

from typing import Any
from typing import List

from easyCore.Objects.Job.Theory import TheoryBase as coreSample
from easyCore.Objects.ObjectClasses import Parameter


class Sample(coreSample):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, name: str, parameters: List[Parameter], *args, **kwargs):
        super(Sample, self).__init__(name, *args, **kwargs)
        self.parameters = parameters
        self.name = name

    # required dunder methods
    def __str__(self):
        return f"Experiment: {self.name}"
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)
    
    def __copy__(self) -> 'Sample':
        # TODO: Implement copy
        return self
    
    def __deepcopy__(self, memo: Any) -> 'Sample':
        # TODO: Implement deepcopy
        return self
    
    def __eq__(self, other: Any) -> bool:
        # TODO Implement equality
        return False
    