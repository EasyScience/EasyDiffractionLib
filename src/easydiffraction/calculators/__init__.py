# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

try:
    from easydiffraction.calculators.cryspy.wrapper import CryspyWrapper  # noqa: F401
except ImportError:
    print('Warning: CrysPy is not installed')

# Temporarily disabling the PyCrysFML interface
# try:
#     from easydiffraction.calculators.pycrysfml.wrapper import PycrysfmlWrapper  # noqa: F401
# except ImportError:
#     print('Warning: CrysFML is not installed')

try:
    from easydiffraction.calculators.pdffit2.wrapper import Pdffit2Wrapper  # noqa: F401
except ImportError:
    pass
    # print('Warning: PdfFit2 is not installed')

from easydiffraction.calculators.wrapper_base import WrapperBase  # noqa: F401
