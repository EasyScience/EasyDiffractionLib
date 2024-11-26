# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

# Aliases for the main classes and methods to simplify the usage
from .job.job import DiffractionJob as Job
from .job.model.phase import Phase
from .utils import download_from_repository

# Globals, which are imported from easydiffraction by a star import
__all__ = ['Job', 'Phase', 'download_from_repository']
