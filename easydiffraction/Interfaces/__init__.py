# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

try:
    from easydiffraction.Interfaces.cryspyV2 import CryspyBase  # noqa: F401
except ImportError:
    print('Warning: CrysPy is not installed')

# Temporarily disabling the CrysFML and GSASII interfaces
# try:
#     from easydiffraction.Interfaces.CFML import CFML  # noqa: F401
# except ImportError:
#     print('Warning: CrysFML is not installed')

# try:
#     from easydiffraction.Interfaces.GSASII import GSASII  # noqa: F401
# except ImportError:
#     print('Warning: GSAS-2 is not installed')

try:
    from easydiffraction.Interfaces.pdffit2 import Pdffit2  # noqa: F401
except ImportError:
    pass
    #print('Warning: PdfFit2 is not installed')

from easydiffraction.Interfaces.interfaceTemplate import InterfaceTemplate as InterfaceTemplate  # noqa: F401
