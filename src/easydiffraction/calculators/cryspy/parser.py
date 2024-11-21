# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import numpy as np

try:
    import cryspy
except ImportError:
    print('No CrysPy module found')


class Parameter(dict):

    def __init__(self,
                value,
                permittedValues = None,
                idx = 0,
                error = 0.0,
                min = -np.inf,
                max = np.inf,
                absDelta = None,
                pctDelta = None,
                units = '',
                category = '',
                prettyCategory = '',
                rowName = '',
                name = '',
                prettyName = '',
                shortPrettyName = '',
                icon = '',
                categoryIcon = '',
                url = '',
                cifDict = '',
                optional = False,
                enabled = True,
                fittable = False,
                fit = False):
        self['value'] = value
        self['permittedValues'] = permittedValues
        self['idx'] = idx
        self['optional'] = optional
        self['enabled'] = enabled
        self['fittable'] = fittable
        self['fit'] = fit
        self['error'] = error
        self['group'] = ""
        self['min'] = min
        self['max'] = max
        self['absDelta'] = absDelta
        self['pctDelta'] = pctDelta
        self['category'] = category
        self['prettyCategory'] = prettyCategory
        self['rowName'] = rowName
        self['name'] = name
        self['prettyName'] = prettyName
        self['shortPrettyName'] = shortPrettyName
        self['icon'] = icon
        self['categoryIcon'] = categoryIcon
        self['url'] = url
        self['cifDict'] = cifDict
        self['parentIndex'] = 0
        self['parentName'] = ''
        self['units'] = units


def calcObjAndDictToEdExperiments(calc_obj, calc_dict):
    experiment_names = []
    exp_substrings = ['pd_', 'data_'] # possible experiment prefixes
    # get experiment names from cryspy_dict
    for key in calc_dict.keys():
        for substring in exp_substrings:
            if key.startswith(substring):
                key = key.replace(substring, "").replace("_", "")
                experiment_names.append(key)

    ed_experiments_meas_only = []
    ed_experiments_no_meas = []

    for data_block in calc_obj.items:
        data_block_name = data_block.data_name

        if data_block_name in experiment_names:
            cryspy_experiment = data_block.items
            ed_experiment_no_meas = {'name': '', 'params': {}, 'loops': {}}
            ed_experiment_meas_only = {'name': '', 'loops': {}}

            # DATABLOCK ID

            ed_experiment_no_meas['name'] = dict(Parameter(
                data_block_name,
                icon = 'microscope',
                url = 'https://docs.easydiffraction.org/lib/dictionaries/',
            ))
            ed_experiment_meas_only['name'] = dict(Parameter(
                data_block_name,
                icon = 'microscope',
                url = 'https://docs.easydiffraction.org/lib/dictionaries/',
            ))

            for item in cryspy_experiment:

                # DATABLOCK SINGLES

                # Ranges category
                if isinstance(item, cryspy.C_item_loop_classes.cl_1_range.Range):
                    ed_experiment_no_meas['params']['_pd_meas'] = {}
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_min'] = dict(Parameter(
                        item.ttheta_min,
                        optional = True,
                        category = '_pd_meas',
                        name = '2theta_range_min',
                        prettyName = 'range min',
                        shortPrettyName = 'min',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/',
                        cifDict = 'pd'
                    ))
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_max'] = dict(Parameter(
                        item.ttheta_max,
                        optional = True,
                        category = '_pd_meas',
                        name = '2theta_range_max',
                        prettyName = 'range max',
                        shortPrettyName = 'max',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/',
                        cifDict = 'pd'
                    ))
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_inc'] = dict(Parameter(
                        0.1,  # default value to be updated later
                        optional = True,
                        category = '_pd_meas',
                        name = '2theta_range_inc',
                        prettyName = 'range inc',
                        shortPrettyName = 'inc',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/',
                        cifDict = 'pd'
                    ))

            # Start from the beginnig after reading ranges
            for item in cryspy_experiment:

                # DATABLOCK SINGLES

                # Setup section (cryspy)
                if isinstance(item, cryspy.C_item_loop_classes.cl_1_setup.Setup):
                    if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation']['probe'] = dict(Parameter(
                        item.radiation.replace('neutrons', 'neutron').replace('X-rays', 'x-ray'),  # NEED FIX
                        permittedValues = ['neutron', 'x-ray'],
                        category = '_diffrn_radiation',
                        name = 'probe',
                        shortPrettyName = 'probe',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_diffrn_radiation/',
                        cifDict = 'core'
                    ))
                    if '_diffrn_radiation_wavelength' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation_wavelength'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation_wavelength']['wavelength'] = dict(Parameter(
                        item.wavelength,
                        error = item.wavelength_sigma,
                        category = '_diffrn_radiation_wavelength',
                        prettyCategory = 'radiation',
                        name = 'wavelength',
                        prettyName = 'wavelength',
                        shortPrettyName = 'wavelength',
                        icon = 'radiation',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_diffrn_radiation/',
                        cifDict = 'core',
                        absDelta = 0.01,
                        units = 'Å',
                        fittable = True,
                        fit = item.wavelength_refinement
                    ))
                    if '_pd_calib' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_pd_calib'] = {}
                    ed_experiment_no_meas['params']['_pd_calib']['2theta_offset'] = dict(Parameter(
                        item.offset_ttheta,
                        error = item.offset_ttheta_sigma,
                        category = '_pd_calib',
                        prettyCategory = 'calib',
                        name = '2theta_offset',
                        prettyName = '2θ offset',
                        shortPrettyName = 'offset',
                        icon = 'arrows-alt-h',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_calib/',
                        cifDict = 'pd',
                        absDelta = 0.2,
                        units = '°',
                        fittable = True,
                        fit = item.offset_ttheta_refinement
                    ))

                # Instrument resolution section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_instr_resolution.PdInstrResolution):
                    if '_pd_instr' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_pd_instr'] = {}
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_u'] = dict(Parameter(
                        item.u,
                        error = item.u_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'resolution_u',
                        prettyName = 'resolution u',
                        shortPrettyName = 'u',
                        icon = 'grip-lines-vertical',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.1,
                        fittable = True,
                        fit = item.u_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_v'] = dict(Parameter(
                        item.v,
                        error = item.v_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'resolution_v',
                        prettyName = 'resolution v',
                        shortPrettyName = 'v',
                        icon = 'grip-lines-vertical',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.1,
                        fittable = True,
                        fit = item.v_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_w'] = dict(Parameter(
                        item.w,
                        error = item.w_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'resolution_w',
                        prettyName = 'resolution w',
                        shortPrettyName = 'w',
                        icon = 'grip-lines-vertical',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.1,
                        fittable = True,
                        fit = item.w_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_x'] = dict(Parameter(
                        item.x,
                        error = item.x_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'resolution_x',
                        prettyName = 'resolution x',
                        shortPrettyName = 'x',
                        icon = 'grip-lines-vertical',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.1,
                        fittable = True,
                        fit = item.x_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_y'] = dict(Parameter(
                        item.y,
                        error = item.y_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'resolution_y',
                        prettyName = 'resolution y',
                        shortPrettyName = 'y',
                        icon = 'grip-lines-vertical',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.1,
                        fittable = True,
                        fit = item.y_refinement
                    ))

                # Peak assymetries section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_instr_reflex_asymmetry.PdInstrReflexAsymmetry):
                    if '_pd_instr' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_pd_instr'] = {}
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p1'] = dict(Parameter(
                        item.p1,
                        error = item.p1_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'reflex_asymmetry_p1',
                        prettyName = 'asymmetry p1',
                        shortPrettyName = 'p1',
                        icon = 'balance-scale-left',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.5,
                        fittable = True,
                        fit = item.p1_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p2'] = dict(Parameter(
                        item.p2,
                        error = item.p2_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'reflex_asymmetry_p2',
                        prettyName = 'asymmetry p2',
                        shortPrettyName = 'p2',
                        icon = 'balance-scale-left',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.5,
                        fittable = True,
                        fit = item.p2_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p3'] = dict(Parameter(
                        item.p3,
                        error = item.p3_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'reflex_asymmetry_p3',
                        prettyName = 'asymmetry p3',
                        shortPrettyName = 'p3',
                        icon = 'balance-scale-left',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.5,
                        fittable = True,
                        fit = item.p3_refinement
                    ))
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p4'] = dict(Parameter(
                        item.p4,
                        error = item.p4_sigma,
                        category = '_pd_instr',
                        prettyCategory = 'inst',
                        name = 'reflex_asymmetry_p4',
                        prettyName = 'asymmetry p4',
                        shortPrettyName = 'p4',
                        icon = 'balance-scale-left',
                        url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                        absDelta = 0.5,
                        fittable = True,
                        fit = item.p4_refinement))

                # Phases section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_phase.PhaseL):
                    cryspy_phases = item.items
                    ed_phases = []
                    for idx, cryspy_phase in enumerate(cryspy_phases):
                        ed_phase = {}
                        ed_phase['id'] = dict(Parameter(
                            cryspy_phase.label,
                            idx = idx,
                            category = '_pd_phase_block',
                            name = 'id',
                            shortPrettyName = 'label',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_phase/',
                            cifDict = 'pd'
                        ))
                        ed_phase['scale'] = dict(Parameter(
                            cryspy_phase.scale,
                            error = cryspy_phase.scale_sigma,
                            idx = idx,
                            category = '_pd_phase_block',
                            prettyCategory = 'phase',
                            rowName = cryspy_phase.label,
                            name = 'scale',
                            prettyName = 'scale',
                            shortPrettyName = 'scale',
                            icon = 'weight',
                            categoryIcon = 'layer-group',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_phase/',
                            cifDict = 'pd',
                            pctDelta = 25,
                            fittable = True,
                            fit = cryspy_phase.scale_refinement
                        ))
                        ed_phases.append(ed_phase)
                    ed_experiment_no_meas['loops']['_pd_phase_block'] = ed_phases

                # Background section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_background.PdBackgroundL):
                    cryspy_bkg_points = item.items
                    ed_bkg_points = []
                    for idx, cryspy_bkg_point in enumerate(cryspy_bkg_points):
                        ed_bkg_point = {}
                        ed_bkg_point['line_segment_X'] = dict(Parameter(
                            cryspy_bkg_point.ttheta,
                            idx = idx,
                            category = '_pd_background',
                            name = 'line_segment_X',
                            prettyName = '2θ',
                            shortPrettyName = '2θ',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_background/',
                            cifDict = 'pd'
                        ))
                        ed_bkg_point['line_segment_intensity'] = dict(Parameter(
                            cryspy_bkg_point.intensity,
                            error = cryspy_bkg_point.intensity_sigma,
                            idx = idx,
                            category = '_pd_background',
                            prettyCategory = 'bkg',
                            rowName = f'{cryspy_bkg_point.ttheta:g}°',  # formatting float to str without trailing zeros
                            name = 'line_segment_intensity',
                            prettyName = 'intensity',
                            shortPrettyName = 'Ibkg',
                            icon = 'mountain',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_background/',
                            cifDict = 'pd',
                            pctDelta = 25,
                            fittable = True,
                            fit = cryspy_bkg_point.intensity_refinement
                        ))
                        ed_bkg_point['X_coordinate'] = dict(Parameter(
                            '2theta',
                            idx = idx,
                            category = '_pd_background',
                            name = 'X_coordinate',
                            prettyName = 'X coord',
                            shortPrettyName = 'X coord',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_background/',
                            cifDict = 'pd'
                        ))
                        ed_bkg_points.append(ed_bkg_point)
                    ed_experiment_no_meas['loops']['_pd_background'] = ed_bkg_points

                # Measured data section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_meas.PdMeasL):
                    cryspy_meas_points = item.items
                    ed_meas_points = []
                    for idx, cryspy_meas_point in enumerate(cryspy_meas_points):
                        ed_meas_point = {}
                        ed_meas_point['2theta_scan'] = dict(Parameter(
                            cryspy_meas_point.ttheta,
                            idx = idx,
                            category = '_pd_meas',
                            name = '2theta_scan',
                            shortPrettyName = '2θ',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_point['intensity_total'] = dict(Parameter(
                            cryspy_meas_point.intensity,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'intensity_total',
                            shortPrettyName = 'I',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_point['intensity_total_su'] = dict(Parameter(
                            cryspy_meas_point.intensity_sigma,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'intensity_total_su',
                            shortPrettyName = 'sI',
                            url = 'https://docs.easydiffraction.org/lib/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_points.append(ed_meas_point)
                    ed_experiment_meas_only['loops']['_pd_meas'] = ed_meas_points

                    # Modify range_inc based on the measured data points in _pd_meas loop
                    pd_meas_2theta_range_min = ed_meas_points[0]['2theta_scan']['value']
                    pd_meas_2theta_range_max = ed_meas_points[-1]['2theta_scan']['value']
                    pd_meas_2theta_range_inc = \
                        (pd_meas_2theta_range_max - pd_meas_2theta_range_min) / (len(ed_meas_points) - 1)
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_inc']['value'] = pd_meas_2theta_range_inc

        if ed_experiment_meas_only is not None:
            ed_experiments_meas_only.append(ed_experiment_meas_only)
        if ed_experiment_no_meas is not None:
            ed_experiments_no_meas.append(ed_experiment_no_meas)

    return ed_experiments_meas_only, ed_experiments_no_meas


def cifV2ToV1_tof(edCif):
    rawToEdNamesCif = {
            '_symmetry_space_group_name_H-M': '_space_group.name_H-M_alt',
            '_atom_site_thermal_displace_type': '_atom_site.ADP_type',
            '_atom_site_adp_type': '_atom_site.ADP_type',
            '_atom_site_U_iso_or_equiv': '_atom_site.U_iso_or_equiv',
            '_atom_site_B_iso_or_equiv': '_atom_site.B_iso_or_equiv',
            '_space_group_IT_coordinate_system_code': '_space_group.IT_coordinate_system_code',
    }
    edToCryspyNamesMap = {}
    edToCryspyNamesMap['base'] = {
            '_space_group.name_H-M_alt': '_space_group_name_H-M_alt',
            '_space_group.IT_coordinate_system_code': '_space_group_IT_coordinate_system_code',

            '_cell.length': '_cell_length',
            '_cell.angle': '_cell_angle',

            '_atom_site.label': '_atom_site_label',
            '_atom_site.type_symbol': '_atom_site_type_symbol',
            '_atom_site.fract': '_atom_site_fract',
            '_atom_site.occupancy': '_atom_site_occupancy',
            '_atom_site.ADP_type': '_atom_site_adp_type',
            '_atom_site.B_iso_or_equiv': '_atom_site_B_iso_or_equiv',

            '_atom_site.site_symmetry_multiplicity': '_atom_site_multiplicity',

            '_diffrn_radiation.probe': '_setup_radiation',

            '_pd_phase_block.id': '_phase_label',
            '_pd_phase_block.scale': '_phase_scale',

            '_model.cif_file_name': '_model_cif_file_name',
            '_experiment.cif_file_name': '_experiment_cif_file_name',

            '_audit_contact_author.name': '_audit.contact_author_name',  # Temporary fix for CrysPy to accept CIFs
            '_audit_contact_author.id_orcid': '_audit.contact_author_id_orcid',  # Temporary fix for CrysPy to accept CIFs

    }
    edToCryspyNamesMap['cwl'] = {
            '_diffrn_radiation_wavelength.wavelength': '_setup_wavelength',

            '_pd_calib.2theta_offset': '_setup_offset_2theta',

            '_pd_instr.resolution_u': '_pd_instr_resolution_u',
            '_pd_instr.resolution_v': '_pd_instr_resolution_v',
            '_pd_instr.resolution_w': '_pd_instr_resolution_w',
            '_pd_instr.resolution_x': '_pd_instr_resolution_x',
            '_pd_instr.resolution_y': '_pd_instr_resolution_y',

            '_pd_instr.reflex_asymmetry_p1': '_pd_instr_reflex_asymmetry_p1',
            '_pd_instr.reflex_asymmetry_p2': '_pd_instr_reflex_asymmetry_p2',
            '_pd_instr.reflex_asymmetry_p3': '_pd_instr_reflex_asymmetry_p3',
            '_pd_instr.reflex_asymmetry_p4': '_pd_instr_reflex_asymmetry_p4',

            '_pd_meas.2theta_scan': '_pd_meas_2theta',
            '_pd_meas.intensity_total_su': '_pd_meas_intensity_sigma',  # before _pd_meas.intensity_total!
            '_pd_meas.intensity_total': '_pd_meas_intensity',

            # NEED see if we can hide this as for TOF case
            '_pd_meas.2theta_range_min': '_range_2theta_min',
            '_pd_meas.2theta_range_max': '_range_2theta_max',

            # NEED to remove this and use our handling of a background as for TOF case
            '_pd_background.line_segment_X': '_pd_background_2theta',
            '_pd_background.line_segment_intensity': '_pd_background_intensity',
            '_pd_background.X_coordinate': '_pd_background_X_coordinate',

    }
    edToCryspyNamesMap['tof'] = {
            '_pd_instr.zero': '_tof_parameters_Zero',
            '_pd_instr.dtt1': '_tof_parameters_Dtt1',
            '_pd_instr.dtt2': '_tof_parameters_dtt2',
            '_pd_instr.2theta_bank': '_tof_parameters_2theta_bank',

            '_pd_instr.peak_shape': '_tof_profile_peak_shape',
            '_pd_instr.alpha0': '_tof_profile_alpha0',
            '_pd_instr.alpha1': '_tof_profile_alpha1',
            '_pd_instr.beta0': '_tof_profile_beta0',
            '_pd_instr.beta1': '_tof_profile_beta1',
            '_pd_instr.gamma0': '_tof_profile_gamma0',
            '_pd_instr.gamma1': '_tof_profile_gamma1',
            '_pd_instr.gamma2': '_tof_profile_gamma2',
            '_pd_instr.sigma0': '_tof_profile_sigma0',
            '_pd_instr.sigma1': '_tof_profile_sigma1',
            '_pd_instr.sigma2': '_tof_profile_sigma2',

            ###'_tof_background.time_max': '_tof_background_time_max',
            ###'_tof_background.coeff': '_tof_background_coeff',

            '_pd_background.line_segment_X': '_tof_backgroundpoint_time',
            '_pd_background.line_segment_intensity': '_tof_backgroundpoint_intensity',
            '_pd_background.X_coordinate': '_tof_backgroundpoint.X_coordinate',

            '_pd_meas.time_of_flight': '_tof_meas_time',
            '_pd_meas.intensity_total_su': '_tof_meas_intensity_sigma',  # before _pd_meas.intensity_total!
            '_pd_meas.intensity_total': '_tof_meas_intensity',

            '_pd_data.point_id': '_tof_meas_point_id',
            '_pd_proc.intensity_norm_su': '_tof_meas_intensity_sigma',  # before _pd_proc.intensity_norm!
            '_pd_proc.intensity_norm': '_tof_meas_intensity',

            '_pd_meas.tof_range_min': '_range_time_min',
            '_pd_meas.tof_range_max': '_range_time_max',
    }
    edToCryspyValuesMap = {
            'x-ray': 'X-rays',
            'neutron': 'neutrons',
            'neutronss': 'neutrons',
    }
    cryspyCif = edCif
    diffrn_radiation_type = 'cwl' if '2theta_scan' in cryspyCif else 'tof'
    for rawName, edName in rawToEdNamesCif.items():
        cryspyCif = cryspyCif.replace(rawName, edName)
    for edName, cryspyName in edToCryspyNamesMap['base'].items():
        cryspyCif = cryspyCif.replace(edName, cryspyName)
    for edName, cryspyName in edToCryspyNamesMap[diffrn_radiation_type].items():
        cryspyCif = cryspyCif.replace(edName, cryspyName)
    for edValue, cryspyValue in edToCryspyValuesMap.items():
        cryspyCif = cryspyCif.replace(edValue, cryspyValue)
    return cryspyCif


def cifV2ToV1(edCif):
    cryspyCif = edCif
    edToCryspyNamesMap = {
        '_diffrn_radiation.probe': '_setup_radiation',
        '_diffrn_radiation_wavelength.wavelength': '_setup_wavelength',

        '_pd_calib.2theta_offset': '_setup_offset_2theta',

        '_pd_instr.resolution_u': '_pd_instr_resolution_u',
        '_pd_instr.resolution_v': '_pd_instr_resolution_v',
        '_pd_instr.resolution_w': '_pd_instr_resolution_w',
        '_pd_instr.resolution_x': '_pd_instr_resolution_x',
        '_pd_instr.resolution_y': '_pd_instr_resolution_y',

        '_pd_instr.reflex_asymmetry_p1': '_pd_instr_reflex_asymmetry_p1',
        '_pd_instr.reflex_asymmetry_p2': '_pd_instr_reflex_asymmetry_p2',
        '_pd_instr.reflex_asymmetry_p3': '_pd_instr_reflex_asymmetry_p3',
        '_pd_instr.reflex_asymmetry_p4': '_pd_instr_reflex_asymmetry_p4',

        '_pd_phase_block.id': '_phase_label',
        '_pd_phase_block.scale': '_phase_scale',

        '_pd_meas.2theta_range_min': '_range_2theta_min',
        '_pd_meas.2theta_range_max': '_range_2theta_max',
        '_pd_meas.2theta_scan': '_pd_meas_2theta',

        '_pd_meas.intensity_total_su': '_pd_meas_intensity_sigma',  # before intensity_total!
        '_pd_meas.intensity_total': '_pd_meas_intensity',

        '_pd_background.line_segment_X': '_pd_background_2theta',
        '_pd_background.line_segment_intensity': '_pd_background_intensity',

        '_model.cif_file_name': '_model_cif_file_name',
        '_experiment.cif_file_name': '_experiment_cif_file_name'
    }
    edToCryspyValuesMap = {
        'x-ray': 'X-rays',
        'neutron': 'neutrons',
        'neutronss': 'neutrons',
    }
    for edName, cryspyName in edToCryspyNamesMap.items():
        cryspyCif = cryspyCif.replace(edName, cryspyName)
    for edValue, cryspyValue in edToCryspyValuesMap.items():
        cryspyCif = cryspyCif.replace(edValue, cryspyValue)
    return cryspyCif
