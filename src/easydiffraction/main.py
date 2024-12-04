# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from easydiffraction.calculators.wrapper_factory import WrapperFactory


def main():
    calculator_wrapper = WrapperFactory()
    print(f'Available calculators: {calculator_wrapper.available_interfaces}')


if __name__ == '__main__':
    main()
