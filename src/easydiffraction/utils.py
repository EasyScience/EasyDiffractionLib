# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import pooch


def download_from_repository(file_name: str, branch: str = 'master', destination: str = 'data'):
    """
    This function downloads a file from the EasyDiffraction repository
    on GitHub.
    :param file_name: The name of the file to download
    :param branch: The branch of the repository to download from
    :param destination: The destination folder to save the file
    :return: None
    """
    prefix = 'https://raw.githubusercontent.com'
    organisation = 'EasyScience'
    repository = 'EasyDiffractionLib'
    source = 'examples/data'
    url = f'{prefix}/{organisation}/{repository}/refs/heads/{branch}/{source}/{file_name}'
    pooch.retrieve(
        url=url,
        known_hash=None,
        fname=file_name,
        path=destination,
    )
