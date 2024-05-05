import numpy as np

 
def pattern_from_cif_block(block) -> dict:
    pattern = []
    # Various pattern parameters
    value = block.find_value("_diffrn_radiation_polarization") or block.find_value("_diffrn_radiation.polarization")
    if value is not None:
        pattern['beam.polarization'] = float(value)
    value = block.find_value("_diffrn_radiation_efficiency") or block.find_value("_diffrn_radiation.efficiency")
    if value is not None:
        pattern['beam.efficiency'] = float(value)
    value = block.find_value("_setup_offset_2theta") or block.find_value("_setup.offset_2theta")
    if value is not None:
        pattern['zero_shift'] = float(value)
    value = block.find_value("_setup_field") or block.find_value("_setup.field")
    if value is not None:
        pattern['field'] = float(value)
    value = block.find_value("_diffrn_radiation_probe") or block.find_value("_diffrn_radiation.probe")
    if value is not None:
        pattern['radiation'] = value

    return pattern

def parameters_from_cif_block(block) -> dict:
    # Various instrumental parameters
    parameters = []
    value = block.find_value("_setup_wavelength") or block.find_value("_setup.wavelength") or \
        block.find_value("_diffrn_radiation.wavelength")
    if value is not None:
        parameters['wavelength'] = float(value)
    value = block.find_value("_pd_instr_resolution_u") or block.find_value("_pd_instr.resolution_u")
    if value is not None:
        parameters['resolution_u'] = float(value)
    value = block.find_value("_pd_instr_resolution_v") or block.find_value("_pd_instr.resolution_v")
    if value is not None:
        parameters['resolution_v'] = float(value)
    value = block.find_value("_pd_instr_resolution_w") or block.find_value("_pd_instr.resolution_w")
    if value is not None:
        parameters['resolution_w'] = float(value)
    value = block.find_value("_pd_instr_resolution_x") or block.find_value("_pd_instr.resolution_x")
    if value is not None:
        parameters['resolution_x'] = float(value)
    value = block.find_value("_pd_instr_resolution_y") or block.find_value("_pd_instr.resolution_y")
    if value is not None:
        parameters['resolution_y'] = float(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p1") or block.find_value("_pd_instr.reflex_asymmetry_p1")
    if value is not None:
        parameters['reflex_asymmetry_p1'] = float(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p2") or block.find_value("_pd_instr.reflex_asymmetry_p2")
    if value is not None:
        parameters['reflex_asymmetry_p2'] = float(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p3") or block.find_value("_pd_instr.reflex_asymmetry_p3")
    if value is not None:
        parameters['reflex_asymmetry_p3'] = float(value)
    value = block.find_value("_pd_instr_reflex_asymmetry_p4") or block.find_value("_pd_instr.reflex_asymmetry_p4")
    if value is not None:
        parameters['reflex_asymmetry_p4'] = float(value)
    
    return parameters

def phase_parameters_from_cif_block(block) -> dict:
    # Get phase parameters
    phase_parameters = []
    experiment_phase_labels = list(block.find_loop("_phase_label"))
    experiment_phase_scales = np.fromiter(block.find_loop("_phase_scale"), float)

    for (phase_label, phase_scale) in zip(experiment_phase_labels, experiment_phase_scales):
        phase_parameters[phase_label] = phase_scale

    return phase_parameters

# def data_from_cif_block(block, experiment_name):
#     # data points

#     data_x = np.fromiter(block.find_loop("_pd_meas_2theta"), float)
#     data_y = []
#     data_e = []
#     data_y.append(np.fromiter(block.find_loop("_pd_meas_intensity_up"), float))
#     data_e.append(np.fromiter(block.find_loop("_pd_meas_intensity_up_sigma"), float))
#     data_y.append(np.fromiter(block.find_loop("_pd_meas_intensity_down"), float))
#     data_e.append(np.fromiter(block.find_loop("_pd_meas_intensity_down_sigma"), float))
#     # Unpolarized case
#     if not np.any(data_y[0]):
#         data_y[0] = np.fromiter(block.find_loop("_pd_meas_intensity"), float)
#         data_e[0] = np.fromiter(block.find_loop("_pd_meas_intensity_sigma"), float)
#         data_y[1] = np.zeros(len(data_y[0]))
#         data_e[1] = np.zeros(len(data_e[0]))

#     coord_name = self.name + "_" + experiment_name + "_" + self._x_axis_name

#     self._datastore.store.easyscience.add_coordinate(coord_name, data_x)

#     for i in range(0, len(data_y)):
#         self._datastore.store.easyscience.add_variable(
#             self.name + "_" + experiment_name + f"_I{i}", [coord_name], data_y[i]
#         )
#         self._datastore.store.easyscience.sigma_attach(
#             self.name + "_" + experiment_name + f"_I{i}", data_e[i]
#         )