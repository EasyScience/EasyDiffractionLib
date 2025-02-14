# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import gemmi
import numpy as np


def value_from_loop_by_another_column(
    block: gemmi.cif.Block, category: str, desired_column: str, another_column: str, another_value: str
) -> str | None:
    """
    Retrieve a value from the desired column in a loop by matching another column's value.

    Parameters:
        block (gemmi.cif.Block): CIF block.
        category (str): CIF category name.
        desired_column (str): Desired column name.
        another_column (str): Column name to match the value.
        another_value (str): Value to match in another column.

    Returns:
        str: The value from the desired column if found, otherwise None.
    """
    table = block.find(f'{category}.', [another_column, desired_column])
    if not table:
        return None

    another_column_idx = list(table.tags).index(f'{category}.{another_column}')
    another_column_array = np.array(table.column(another_column_idx))
    another_value_indices = np.where(another_column_array == another_value)[0]

    if not another_value_indices.size:
        return None

    desired_column_idx = list(table.tags).index(f'{category}.{desired_column}')
    desired_column_array = np.array(table.column(desired_column_idx))
    desired_values = desired_column_array[another_value_indices]

    if not desired_values.size:
        return None

    return str(desired_values[0])


def pattern_from_cif_block(block) -> dict:
    # Check the experiment type and create the corresponding pattern
    pattern = {}
    value = block.find_value('_diffrn_radiation_polarization') or block.find_value('_diffrn_radiation.polarization')
    if value is not None:
        pattern['beam.polarization'] = float(value)
    value = block.find_value('_diffrn_radiation_efficiency') or block.find_value('_diffrn_radiation.efficiency')
    if value is not None:
        pattern['beam.efficiency'] = float(value)
    value = (
        block.find_value('_setup_offset_2theta')
        or block.find_value('_setup.offset_2theta')
        or block.find_value('_pd_calib.2theta_offset')
        or block.find_value('_pd_instr.zero')
        or value_from_loop_by_another_column(
            block, category='_pd_calib_d_to_tof', desired_column='coeff', another_column='power', another_value='0'
        )
    )
    if value is not None:
        pattern['zero_shift'] = {}
        pattern['zero_shift']['value'], pattern['zero_shift']['error'] = parse_with_error(value)
    value = block.find_value('_setup_field') or block.find_value('_setup.field')
    if value is not None:
        pattern['field'] = float(value)
    value = block.find_value('_diffrn_radiation_probe') or block.find_value('_diffrn_radiation.probe')
    if value is not None:
        pattern['radiation'] = value

    return pattern


def parameters_from_cif_block(block) -> dict:
    # Various instrumental parameters
    parameters = {}
    # CW
    value = (
        block.find_value('_setup_wavelength')
        or block.find_value('_setup.wavelength')
        or block.find_value('_diffrn_radiation.wavelength')
        or block.find_value('_diffrn_radiation_wavelength.wavelength')
    )
    if value is not None:
        parameters['wavelength'] = {}
        parameters['wavelength']['value'], parameters['wavelength']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_resolution_u') or block.find_value('_pd_instr.resolution_u')
    if value is not None:
        parameters['resolution_u'] = {}
        parameters['resolution_u']['value'], parameters['resolution_u']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_resolution_v') or block.find_value('_pd_instr.resolution_v')
    if value is not None:
        parameters['resolution_v'] = {}
        parameters['resolution_v']['value'], parameters['resolution_v']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_resolution_w') or block.find_value('_pd_instr.resolution_w')
    if value is not None:
        parameters['resolution_w'] = {}
        parameters['resolution_w']['value'], parameters['resolution_w']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_resolution_x') or block.find_value('_pd_instr.resolution_x')
    if value is not None:
        parameters['resolution_x'] = {}
        parameters['resolution_x']['value'], parameters['resolution_x']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_resolution_y') or block.find_value('_pd_instr.resolution_y')
    if value is not None:
        parameters['resolution_y'] = {}
        parameters['resolution_y']['value'], parameters['resolution_y']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_reflex_asymmetry_p1') or block.find_value('_pd_instr.reflex_asymmetry_p1')
    if value is not None:
        parameters['reflex_asymmetry_p1'] = {}
        parameters['reflex_asymmetry_p1']['value'], parameters['reflex_asymmetry_p1']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_reflex_asymmetry_p2') or block.find_value('_pd_instr.reflex_asymmetry_p2')
    if value is not None:
        parameters['reflex_asymmetry_p2'] = {}
        parameters['reflex_asymmetry_p2']['value'], parameters['reflex_asymmetry_p2']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_reflex_asymmetry_p3') or block.find_value('_pd_instr.reflex_asymmetry_p3')
    if value is not None:
        parameters['reflex_asymmetry_p3'] = {}
        parameters['reflex_asymmetry_p3']['value'], parameters['reflex_asymmetry_p3']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_reflex_asymmetry_p4') or block.find_value('_pd_instr.reflex_asymmetry_p4')
    if value is not None:
        parameters['reflex_asymmetry_p4'] = {}
        parameters['reflex_asymmetry_p4']['value'], parameters['reflex_asymmetry_p4']['error'] = parse_with_error(value)
    value = block.find_value('_pd_calib_2theta_offset') or block.find_value('_pd_calib.2theta_offset')
    if value is not None:
        parameters['zero_shift'] = {}
        parameters['zero_shift']['value'], parameters['zero_shift']['error'] = parse_with_error(value)

    # ToF
    value = (
        block.find_value('_pd_instr_dtt1')
        or block.find_value('_pd_instr.dtt1')
        or value_from_loop_by_another_column(
            block, category='_pd_calib_d_to_tof', desired_column='coeff', another_column='power', another_value='1'
        )
    )
    if value is not None:
        parameters['dtt1'] = {}
        parameters['dtt1']['value'], parameters['dtt1']['error'] = parse_with_error(value)
    value = (
        block.find_value('_pd_instr_dtt2')
        or block.find_value('_pd_instr.dtt2')
        or value_from_loop_by_another_column(
            block, category='_pd_calib_d_to_tof', desired_column='coeff', another_column='power', another_value='2'
        )
    )
    if value is not None:
        parameters['dtt2'] = {}
        parameters['dtt2']['value'], parameters['dtt2']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_2theta_bank') or block.find_value('_pd_instr.2theta_bank')
    if value is not None:
        parameters['2theta_bank'] = {}
        parameters['2theta_bank']['value'], parameters['2theta_bank']['error'] = parse_with_error(value)

    value = block.find_value('_pd_instr.zero') or block.find_value('_pd_instr_zero')
    if value is not None:
        parameters['zero'] = {}
        parameters['zero']['value'], parameters['zero']['error'] = parse_with_error(value)

    value = block.find_value('_pd_instr_peak_shape') or block.find_value('_pd_instr.peak_shape')
    if value is not None:
        parameters['peak_shape'] = value
    value = block.find_value('_pd_instr_alpha0') or block.find_value('_pd_instr.alpha0')
    if value is not None:
        parameters['alpha0'] = {}
        parameters['alpha0']['value'], parameters['alpha0']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_alpha1') or block.find_value('_pd_instr.alpha1')
    if value is not None:
        parameters['alpha1'] = {}
        parameters['alpha1']['value'], parameters['alpha1']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_beta0') or block.find_value('_pd_instr.beta0')
    if value is not None:
        parameters['beta0'] = {}
        parameters['beta0']['value'], parameters['beta0']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_beta1') or block.find_value('_pd_instr.beta1')
    if value is not None:
        parameters['beta1'] = {}
        parameters['beta1']['value'], parameters['beta1']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_gamma0') or block.find_value('_pd_instr.gamma0')
    if value is not None:
        parameters['gamma0'] = {}
        parameters['gamma0']['value'], parameters['gamma0']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_gamma1') or block.find_value('_pd_instr.gamma1')
    if value is not None:
        parameters['gamma1'] = {}
        parameters['gamma1']['value'], parameters['gamma1']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_gamma2') or block.find_value('_pd_instr.gamma2')
    if value is not None:
        parameters['gamma2'] = {}
        parameters['gamma2']['value'], parameters['gamma2']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_sigma0') or block.find_value('_pd_instr.sigma0')
    if value is not None:
        parameters['sigma0'] = {}
        parameters['sigma0']['value'], parameters['sigma0']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_sigma1') or block.find_value('_pd_instr.sigma1')
    if value is not None:
        parameters['sigma1'] = {}
        parameters['sigma1']['value'], parameters['sigma1']['error'] = parse_with_error(value)
    value = block.find_value('_pd_instr_sigma2') or block.find_value('_pd_instr.sigma2')
    if value is not None:
        parameters['sigma2'] = {}
        parameters['sigma2']['value'], parameters['sigma2']['error'] = parse_with_error(value)
    return parameters


def phase_parameters_from_cif_block(block) -> dict:
    # Get phase parameters
    phase_parameters = {}
    experiment_phase_labels = list(block.find_loop('_phase_label'))
    experiment_phase_scales = np.fromiter(block.find_loop('_phase_scale'), float)
    if not experiment_phase_labels:
        experiment_phase_labels = list(block.find_loop('_pd_phase_block.id'))
        scales = np.fromiter(block.find_loop('_pd_phase_block.scale'), dtype=('S20'))
        experiment_phase_scales = []
        for scale in scales:
            experiment_phase_scales.append(scale.decode('ascii'))

    for phase_label, phase_scale in zip(experiment_phase_labels, experiment_phase_scales):
        phase_parameters[phase_label] = {}
        phase_parameters[phase_label]['value'], phase_parameters[phase_label]['error'] = parse_with_error(phase_scale)

    return phase_parameters


def data_from_cif_block(block):
    # data points
    data = {}

    # v 1.x
    is_v1 = len(block.find_loop('_pd_meas_2theta')) > 0
    # tof
    is_tof = len(block.find_loop('_pd_meas.time_of_flight')) > 0
    # assure we actually have data
    if not (is_v1 or is_tof) and block.find_loop('_pd_meas.2theta_scan') is None:
        return
    if is_v1:
        str_theta = '_pd_meas_2theta'
        str_up = '_pd_meas_intensity_up'
        str_down = '_pd_meas_intensity_down'
        str_up_sigma = '_pd_meas_intensity_up_sigma'
        str_down_sigma = '_pd_meas_intensity_down_sigma'
        str_intensity = '_pd_meas_intensity'
        str_intensity_sigma = '_pd_meas_intensity_sigma'
    elif not is_tof:
        str_theta = '_pd_meas.2theta_scan'
        str_up = '_pd_meas.intensity_up'
        str_down = '_pd_meas.intensity_down'
        str_up_sigma = '_pd_meas.intensity_up_sigma'
        str_down_sigma = '_pd_meas.intensity_down_sigma'
        str_intensities = ['_pd_meas.intensity_total', '_pd_proc.intensity_norm']
        str_intensity_sigmas = ['_pd_meas.intensity_total_su', '_pd_proc.intensity_norm_su']
    else:
        str_theta = '_pd_meas.time_of_flight'
        str_up = '_pd_meas.intensity_up'
        str_down = '_pd_meas.intensity_down'
        str_up_sigma = '_pd_meas.intensity_up_sigma'
        str_down_sigma = '_pd_meas.intensity_down_sigma'
        str_intensities = ['_pd_meas.intensity_total', '_pd_proc.intensity_norm']
        str_intensity_sigmas = ['_pd_meas.intensity_total_su', '_pd_proc.intensity_norm_su']

    # Those values are NOT fittable, so no (error) is expected
    data_x = np.fromiter(block.find_loop(str_theta), float)
    data_y = []
    data_e = []
    if len(block.find_loop(str_up)) != 0:
        data_y.append(np.fromiter(block.find_loop(str_up), float))
        data_e.append(np.fromiter(block.find_loop(str_up_sigma), float))
        data_y.append(np.fromiter(block.find_loop(str_down), float))
        data_e.append(np.fromiter(block.find_loop(str_down_sigma), float))
    # Unpolarized case
    else:
        for str_intensity in str_intensities:
            loop = block.find_loop(str_intensity)
            if loop.get_loop() is not None:
                data_y.append(np.fromiter(loop, float))
                continue
        for str_intensity_sigma in str_intensity_sigmas:
            loop = block.find_loop(str_intensity_sigma)
            if loop.get_loop() is not None:
                data_e.append(np.fromiter(loop, float))
                continue
    data['x'] = data_x
    data['y'] = data_y
    data['e'] = data_e
    return data


def background_from_cif_block(block):
    # v 1.x
    is_v1 = len(block.find_loop('_pd_background_2theta')) > 0
    is_tof = len(block.find_loop('_tof_background_time')) > 0

    if is_tof:
        x_label = '_tof_background_time'
        y_label = '_tof_background_intensity'
    elif is_v1:
        x_label = '_pd_background_2theta'
        y_label = '_pd_background_intensity'
    else:
        x_label = '_pd_background.line_segment_X'
        y_label = '_pd_background.line_segment_intensity'

    bg_x_values = np.fromiter(block.find_loop(x_label), float)
    bg_y_label = np.fromiter(block.find_loop(y_label), dtype=('S20'))
    bg_y_values = []
    for val in bg_y_label:
        bg_y_values.append(val.decode('ascii'))

    y = {}
    for x, y_repr in zip(bg_x_values, bg_y_values):
        y[x] = {}
        y[x]['value'], y[x]['error'] = parse_with_error(y_repr)

    return bg_x_values, y


def parse_with_error(value: str) -> tuple:
    if '(' in value:
        value, error = value.split('(')
        error = error.strip(')')
        if '.' in value:
            # float
            if not error:
                return float(value), 0.0  # 1.23()
            else:
                err = (10 ** -(len(f'{value}'.split('.')[1]) - 1)) * int(error)
                return float(value), err
        else:
            # int
            if not error:
                return int(value), 0
            else:
                err = 10 ** (len(str(error)) - 1)
                return int(value), err

    return float(value), None  # 1.23
