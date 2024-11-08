# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

import pooch


def download_from_repository(fname : str, branch : str = 'more-examples', destination : str = 'data'):
    '''
    This function downloads a file from the EasyDiffraction repository on GitHub.
    :param fname: The name of the file to download
    :param destination: The destination folder to save the file
    :return: None
    '''
    organisation = 'EasyScience'
    repository = 'EasyDiffractionLib'
    source = 'examples/data'
    url = f'https://raw.githubusercontent.com/{organisation}/{repository}/refs/heads/{branch}/{source}/{fname}'
    pooch.retrieve(
        url=url,
        known_hash=None,
        fname=fname,
        path=destination,
    )
