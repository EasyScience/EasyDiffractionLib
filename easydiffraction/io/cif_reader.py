import numpy as np


def pattern_from_cif_block(block) -> dict:
    # Check the experiment type and create the corresponding pattern
    pattern = {}
    value = block.find_value("_diffrn_radiation_polarization") or block.find_value("_diffrn_radiation.polarization")
    if value is not None:
        pattern['beam.polarization'] = float(value)
    value = block.find_value("_diffrn_radiation_efficiency") or block.find_value("_diffrn_radiation.efficiency")
    if value is not None:
        pattern['beam.efficiency'] = float(value)
    value = block.find_value("_setup_offset_2theta") or block.find_value("_setup.offset_2theta") or \
        block.find_value("_pd_calib.2theta_offset")
    if value is not None:
        pattern['zero_shift'] = {}
        pattern['zero_shift']['value'], pattern['zero_shift']['error'] = parse_with_error(value)
    value = block.find_value("_setup_field") or block.find_value("_setup.field")
    if value is not None:
        pattern['field'] = float(value)
    value = block.find_value("_diffrn_radiation_probe") or block.find_value("_diffrn_radiation.probe")
    if value is not None:
        pattern['radiation'] = value

    return pattern

def parameters_from_cif_block(block) -> dict:
    # Various instrumental parameters
    parameters = {}
    value = block.find_value("_setup_wavelength") or block.find_value("_setup.wavelength") or \
        block.find_value("_diffrn_radiation.wavelength") or \
        block.find_value("_diffrn_radiation_wavelength.wavelength")
    if value is not None:
        parameters['wavelength'] = {}
        parameters['wavelength']['value'], parameters['wavelength']['error'] = parse_with_error(value)

    value = block.find_value("_pd_instr_resolution_u") or block.find_value("_pd_instr.resolution_u")
    if value is not None:
        parameters['resolution_u'] = {}
        parameters['resolution_u']['value'], parameters['resolution_u']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_resolution_v") or block.find_value("_pd_instr.resolution_v")
    if value is not None:
        parameters['resolution_v'] = {}
        parameters['resolution_v']['value'], parameters['resolution_v']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_resolution_w") or block.find_value("_pd_instr.resolution_w")
    if value is not None:
        parameters['resolution_z'] = {}
        parameters['resolution_z']['value'], parameters['resolution_z']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_resolution_x") or block.find_value("_pd_instr.resolution_x")
    if value is not None:
        parameters['resolution_x'] = {}
        parameters['resolution_x']['value'], parameters['resolution_x']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_resolution_y") or block.find_value("_pd_instr.resolution_y")
    if value is not None:
        parameters['resolution_y'] = {}
        parameters['resolution_y']['value'], parameters['resolution_y']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p1") or block.find_value("_pd_instr.reflex_asymmetry_p1")
    if value is not None:
        parameters['reflex_asymmetry_p1'] = {}
        parameters['reflex_asymmetry_p1']['value'], parameters['reflex_asymmetry_p1']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p2") or block.find_value("_pd_instr.reflex_asymmetry_p2")
    if value is not None:
        parameters['reflex_asymmetry_p2'] = {}
        parameters['reflex_asymmetry_p2']['value'], parameters['reflex_asymmetry_p2']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p3") or block.find_value("_pd_instr.reflex_asymmetry_p3")
    if value is not None:
        parameters['reflex_asymmetry_p3'] = {}
        parameters['reflex_asymmetry_p3']['value'], parameters['reflex_asymmetry_p3']['error'] = parse_with_error(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p4") or block.find_value("_pd_instr.reflex_asymmetry_p4")
    if value is not None:
        parameters['reflex_asymmetry_p3'] = {}
        parameters['reflex_asymmetry_p3']['value'], parameters['reflex_asymmetry_p3']['error'] = parse_with_error(value)
    
    return parameters

def phase_parameters_from_cif_block(block) -> dict:
    # Get phase parameters
    phase_parameters = {}
    experiment_phase_labels = list(block.find_loop("_phase_label"))
    experiment_phase_scales = np.fromiter(block.find_loop("_phase_scale"), float)
    if not experiment_phase_labels:
        experiment_phase_labels = list(block.find_loop("_pd_phase_block.id"))
        scales = np.fromiter(block.find_loop('_pd_phase_block.scale'), dtype=('S20'))
        experiment_phase_scales = []
        for scale in scales:
            experiment_phase_scales.append(scale.decode('ascii'))
            # np.append(experiment_phase_scales, scale.decode('ascii'))

    for (phase_label, phase_scale) in zip(experiment_phase_labels, experiment_phase_scales):
        phase_parameters[phase_label] = {}
        phase_parameters[phase_label]['value'], phase_parameters[phase_label]['error'] = parse_with_error(phase_scale)

    return phase_parameters

def data_from_cif_block(block):
    # data points
    data = {}

    # v 1.x
    is_v1 = block.find_loop("_pd_meas_2theta") is not None
    # assure we actually have data
    if not is_v1 and block.find_loop("_pd_meas.2theta_scan") is None:
        return
    if is_v1:
        str_theta = "_pd_meas_2theta"
        str_up = "_pd_meas_intensity_up"
        str_down = "_pd_meas_intensity_down"
        str_up_sigma = "_pd_meas_intensity_up_sigma"
        str_down_sigma = "_pd_meas_intensity_down_sigma"
        str_intensity = "_pd_meas_intensity"
        str_intensity_sigma = "_pd_meas_intensity_sigma"
    else:
        str_theta = "_pd_meas.2theta_scan"
        str_up = "_pd_meas.intensity_up"
        str_down = "_pd_meas.intensity_down"
        str_up_sigma = "_pd_meas.intensity_up_sigma"
        str_down_sigma = "_pd_meas.intensity_down_sigma"
        str_intensity = "_pd_meas.intensity_total"
        str_intensity_sigma = "_pd_meas.intensity_total_su"

    data_x = np.fromiter(block.find_loop(str_theta), float)
    data_y = []
    data_e = []
    data_y.append(np.fromiter(block.find_loop(str_up), float))
    data_e.append(np.fromiter(block.find_loop(str_up_sigma), float))
    data_y.append(np.fromiter(block.find_loop(str_down), float))
    data_e.append(np.fromiter(block.find_loop(str_down_sigma), float))
    # Unpolarized case
    if not np.any(data_y[0]):
        data_y[0] = np.fromiter(block.find_loop(str_intensity), float)
        data_e[0] = np.fromiter(block.find_loop(str_intensity_sigma), float)
        data_y[1] = np.zeros(len(data_y[0]))
        data_e[1] = np.zeros(len(data_e[0]))
    data['x'] = data_x
    data['y'] = data_y
    data['e'] = data_e
    return data

def parse_with_error(value: str) -> tuple:
    if "(" in value:
        value, error = value.split("(")
        error = error.strip(")")
        return float(value), float(error)
    return float(value), None
