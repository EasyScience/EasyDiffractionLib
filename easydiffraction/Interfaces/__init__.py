# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

try:
    from easydiffraction.calculators.cryspy.wrapper import CryspyBase  # noqa: F401
except ImportError:
    print('Warning: CrysPy is not installed')

# Temporarily disabling the PyCrysFML interface
# try:
#     from easydiffraction.calculators.pycrysfml.wrapper import Pycrysfml  # noqa: F401
# except ImportError:
#     print('Warning: CrysFML is not installed')

try:
    from easydiffraction.Interfaces.pdffit2 import Pdffit2  # noqa: F401
except ImportError:
    pass
    #print('Warning: PdfFit2 is not installed')

from easydiffraction.Interfaces.interfaceTemplate import InterfaceTemplate as InterfaceTemplate  # noqa: F401
