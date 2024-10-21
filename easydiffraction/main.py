# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

from easydiffraction.interface import InterfaceFactory


def main():
    interface = InterfaceFactory()
    print(f"Available interfaces: {interface.available_interfaces}")

if __name__ == '__main__':
    main()
