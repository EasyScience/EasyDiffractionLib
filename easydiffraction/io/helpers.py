# SPDX-FileCopyrightText: 2023 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © © 2023 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffractionApp>


def generalizePath(fpath: str) -> str:
    """
    Generalize the filepath to be platform-specific, so all file operations
    can be performed.
    :param URI rcfPath: URI to the file
    :return URI filename: platform specific URI
    """
    return fpath  # NEED FIX: Check on different platforms
    # filename = urlparse(fpath).path
    # if not sys.platform.startswith("win"):
    #     return filename
    # if filename[0] == '/':
    #     filename = filename[1:].replace('/', os.path.sep)
    # return filename

def formatMsg(type, *args):
    types = {'main': '•', 'sub': ' ◦'}
    mark = types[type]
    widths = [22,21,20,10]
    widths[0] -= len(mark)
    msgs = []
    for idx, arg in enumerate(args):
        msgs.append(f'{arg:<{widths[idx]}}')
    msg = ' ▌ '.join(msgs)
    msg = f'{mark} {msg}'
    return msg

