# SPDX-FileCopyrightText: 2023 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © © 2023 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffractionApp>

import numpy as np

try:
    import cryspy
    from cryspy.A_functions_base.function_2_space_group import get_it_coordinate_system_codes_by_it_number
    print('CrysPy module imported')
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


class CryspyParser:

    @staticmethod
    def calcObjAndDictToEdModels(cryspy_obj, cryspy_dict):
        phase_names = [name.replace('crystal_', '') for name in cryspy_dict.keys() if name.startswith('crystal_')]
        ed_phases = []

        for data_block in cryspy_obj.items:
            data_block_name = data_block.data_name

            if data_block_name in phase_names:
                cryspy_phase = data_block.items
                ed_phase = {'name': '', 'params': {}, 'loops': {}}

                # DATABLOCK ID

                ed_phase['name'] = dict(Parameter(
                    data_block_name,
                    icon = 'layer-group',
                    url = 'https://docs.easydiffraction.org/app/project/dictionaries/',
                ))

                for item in cryspy_phase:

                    # DATABLOCK SINGLES

                    # Space group category
                    if type(item) == cryspy.C_item_loop_classes.cl_2_space_group.SpaceGroup:
                        if '_space_group' not in ed_phase['params']:
                            ed_phase['params']['_space_group'] = {}
                        ed_phase['params']['_space_group']['name_H-M_alt'] = dict(Parameter(
                            item.name_hm_alt,
                            category = '_space_group',
                            name = 'name_H-M_alt',
                            shortPrettyName = 'name',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_space_group/',
                            cifDict = 'core'
                        ))
                        ed_phase['params']['_space_group']['IT_coordinate_system_code'] = dict(Parameter(
                            item.it_coordinate_system_code,
                            category = '_space_group',
                            name = 'IT_coordinate_system_code',
                            shortPrettyName = 'code',
                            permittedValues = list(get_it_coordinate_system_codes_by_it_number(item.it_number)),
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_space_group/',
                            cifDict = 'core'
                        ))
                        ed_phase['params']['_space_group']['crystal_system'] = dict(Parameter(
                            item.crystal_system,
                            optional = True,
                            category = '_space_group',
                            name = 'crystal_system',
                            shortPrettyName = 'crystal system',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_space_group/',
                            cifDict = 'core'
                        ))
                        ed_phase['params']['_space_group']['IT_number'] = dict(Parameter(
                            item.it_number,
                            optional = True,
                            category = '_space_group',
                            name = 'IT_number',
                            shortPrettyName = 'number',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_space_group/',
                            cifDict = 'core'
                        ))

                    # Cell category
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_cell.Cell:
                        if '_cell' not in ed_phase['params']:
                            ed_phase['params']['_cell'] = {}
                        ed_phase['params']['_cell']['length_a'] = dict(Parameter(
                            item.length_a,
                            error = item.length_a_sigma,  # NEED FIX: rename 'error' to 'su'
                            category = '_cell',
                            prettyCategory = 'cell',
                            name = 'length_a',
                            prettyName = 'length a',
                            shortPrettyName = 'a',  # NEED FIX: rename 'shortPrettyName' to 'shortName' ???
                            icon = 'ruler',
                            categoryIcon = 'cube',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_cell/',
                            cifDict = 'core',
                            enabled = not item.length_a_constraint,
                            absDelta = 0.1,
                            units = 'Å',
                            fittable = True,
                            fit = item.length_a_refinement
                        ))
                        ed_phase['params']['_cell']['length_b'] = dict(Parameter(
                            item.length_b,
                            error = item.length_b_sigma,
                            category = '_cell',
                            prettyCategory = 'cell',
                            name = 'length_b',
                            prettyName = 'length b',
                            shortPrettyName = 'b',
                            icon = 'ruler',
                            categoryIcon = 'cube',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_cell/',
                            cifDict = 'core',
                            enabled = not item.length_b_constraint,
                            absDelta = 0.1,
                            units = 'Å',
                            fittable = True,
                            fit = item.length_b_refinement
                        ))
                        ed_phase['params']['_cell']['length_c'] = dict(Parameter(
                            item.length_c,
                            error = item.length_c_sigma,
                            category = '_cell',
                            prettyCategory = 'cell',
                            name = 'length_c',
                            prettyName = 'length c',
                            shortPrettyName = 'c',
                            icon = 'ruler',
                            categoryIcon = 'cube',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_cell/',
                            cifDict = 'core',
                            enabled = not item.length_c_constraint,
                            absDelta = 0.1,
                            units = 'Å',
                            fittable = True,
                            fit = item.length_c_refinement
                        ))
                        ed_phase['params']['_cell']['angle_alpha'] = dict(Parameter(
                            item.angle_alpha,
                            error = item.angle_alpha_sigma,
                            category = '_cell',
                            prettyCategory = 'cell',
                            name = 'angle_alpha',
                            prettyName = 'angle α',
                            shortPrettyName = 'α',
                            icon = 'ruler',
                            categoryIcon = 'less-than',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_cell/',
                            cifDict = 'core',
                            enabled = not item.angle_alpha_constraint,
                            absDelta = 1.0,
                            units = '°',
                            fittable = True,
                            fit = item.angle_alpha_refinement
                        ))
                        ed_phase['params']['_cell']['angle_beta'] = dict(Parameter(
                            item.angle_beta,
                            error = item.angle_beta_sigma,
                            category = '_cell',
                            prettyCategory = 'cell',
                            name = 'angle_beta',
                            prettyName = 'angle β',
                            shortPrettyName = 'β',
                            icon = 'ruler',
                            categoryIcon = 'less-than',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_cell/',
                            cifDict = 'core',
                            enabled = not item.angle_alpha_constraint,
                            absDelta = 1.0,
                            units = '°',
                            fittable = True,
                            fit = item.angle_beta_refinement
                        ))
                        ed_phase['params']['_cell']['angle_gamma'] = dict(Parameter(
                            item.angle_gamma,
                            error = item.angle_gamma_sigma,
                            category = '_cell',
                            prettyCategory = 'cell',
                            name = 'angle_gamma',
                            prettyName = 'angle γ',
                            shortPrettyName = 'γ',
                            icon = 'ruler',
                            categoryIcon = 'less-than',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_cell/',
                            cifDict = 'core',
                            enabled = not item.angle_alpha_constraint,
                            absDelta = 1.0,
                            units = '°',
                            fittable = True,
                            fit = item.angle_gamma_refinement
                        ))

                    # DATABLOCK TABLES

                    # Atom site category
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_atom_site.AtomSiteL:
                        cryspy_atoms = item.items
                        ed_atoms = []
                        for idx, cryspy_atom in enumerate(cryspy_atoms):
                            ed_atom = {}
                            ed_atom['label'] = dict(Parameter(
                                cryspy_atom.label,
                                idx = idx,
                                category = '_atom_site',
                                name = 'label',
                                shortPrettyName = 'label',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core'
                            ))
                            ed_atom['type_symbol'] = dict(Parameter(
                                cryspy_atom.type_symbol,
                                idx = idx,
                                category = '_atom_site',
                                name = 'type_symbol',
                                shortPrettyName = 'type',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core'
                            ))
                            ed_atom['fract_x'] = dict(Parameter(
                                cryspy_atom.fract_x,
                                error = cryspy_atom.fract_x_sigma,
                                idx = idx,
                                category = '_atom_site',
                                prettyCategory = 'atom',
                                rowName = cryspy_atom.label,
                                name = 'fract_x',
                                prettyName = 'fract x',
                                shortPrettyName = 'x',
                                icon = 'map-marker-alt',
                                categoryIcon = 'atom',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core',
                                enabled = not cryspy_atom.fract_x_constraint,
                                absDelta = 0.05,
                                fittable = True,
                                fit = cryspy_atom.fract_x_refinement
                            ))
                            ed_atom['fract_y'] = dict(Parameter(
                                cryspy_atom.fract_y,
                                error = cryspy_atom.fract_y_sigma,
                                idx = idx,
                                category = '_atom_site',
                                prettyCategory = 'atom',
                                rowName = cryspy_atom.label,
                                name = 'fract_y',
                                prettyName = 'fract y',
                                shortPrettyName = 'y',
                                icon = 'map-marker-alt',
                                categoryIcon = 'atom',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core',
                                enabled = not cryspy_atom.fract_y_constraint,
                                absDelta = 0.05,
                                fittable = True,
                                fit = cryspy_atom.fract_y_refinement
                            ))
                            ed_atom['fract_z'] = dict(Parameter(
                                cryspy_atom.fract_z,
                                error = cryspy_atom.fract_z_sigma,
                                idx = idx,
                                category = '_atom_site',
                                prettyCategory = 'atom',
                                rowName = cryspy_atom.label,
                                name = 'fract_z',
                                prettyName = 'fract z',
                                shortPrettyName = 'z',
                                icon = 'map-marker-alt',
                                categoryIcon = 'atom',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core',
                                enabled = not cryspy_atom.fract_z_constraint,
                                absDelta = 0.05,
                                fittable = True,
                                fit = cryspy_atom.fract_z_refinement
                            ))
                            ed_atom['occupancy'] = dict(Parameter(
                                cryspy_atom.occupancy,
                                error = cryspy_atom.occupancy_sigma,
                                idx = idx,
                                category = '_atom_site',
                                prettyCategory = 'atom',
                                rowName = cryspy_atom.label,
                                name = 'occupancy',
                                prettyName = 'occ',
                                shortPrettyName = 'occ',
                                icon = 'fill',
                                categoryIcon = 'atom',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core',
                                enabled = not cryspy_atom.occupancy_constraint,
                                absDelta = 0.05,
                                fittable = True,
                                fit = cryspy_atom.occupancy_refinement
                            ))
                            ed_atom['ADP_type'] = dict(Parameter(
                                cryspy_atom.adp_type,
                                idx = idx,
                                category = '_atom_site',
                                name = 'ADP_type',
                                shortPrettyName = 'type',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core'
                            ))
                            ed_atom['B_iso_or_equiv'] = dict(Parameter(
                                cryspy_atom.b_iso_or_equiv,
                                error = cryspy_atom.b_iso_or_equiv_sigma,
                                idx = idx,
                                category = '_atom_site',
                                prettyCategory = 'atom',
                                rowName = cryspy_atom.label,
                                name = 'B_iso_or_equiv',
                                prettyName = 'Biso',
                                shortPrettyName = 'iso',
                                icon = 'arrows-alt',
                                categoryIcon = 'atom',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core',
                                enabled = not cryspy_atom.b_iso_or_equiv_constraint,
                                absDelta = 0.1,
                                units = 'Å²',
                                fittable = True,
                                fit = cryspy_atom.b_iso_or_equiv_refinement
                            ))
                            ed_atom['site_symmetry_multiplicity'] = dict(Parameter(
                                cryspy_atom.multiplicity,
                                optional = True,
                                idx = idx,
                                category = '_atom_site',
                                name = 'site_symmetry_multiplicity',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core'
                            ))
                            ed_atom['Wyckoff_symbol'] = dict(Parameter(
                                cryspy_atom.wyckoff_symbol,
                                optional = True,
                                category = '_atom_site',
                                name = 'Wyckoff_symbol',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_atom_site/',
                                cifDict = 'core'
                            ))
                            ed_atoms.append(ed_atom)
                        ed_phase['loops']['_atom_site'] = ed_atoms

            ed_phases.append(ed_phase)

        return ed_phases

    @staticmethod
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
                    url = 'https://docs.easydiffraction.org/app/project/dictionaries/',
                ))
                ed_experiment_meas_only['name'] = dict(Parameter(
                    data_block_name,
                    icon = 'microscope',
                    url = 'https://docs.easydiffraction.org/app/project/dictionaries/',
                ))

                for item in cryspy_experiment:

                    # DATABLOCK SINGLES

                    # Ranges category
                    if type(item) == cryspy.C_item_loop_classes.cl_1_range.Range:
                        ed_experiment_no_meas['params']['_pd_meas'] = {}
                        ed_experiment_no_meas['params']['_pd_meas']['2theta_range_min'] = dict(Parameter(
                            item.ttheta_min,
                            optional = True,
                            category = '_pd_meas',
                            name = '2theta_range_min',
                            prettyName = 'range min',
                            shortPrettyName = 'min',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/',
                            cifDict = 'pd'
                        ))
                        ed_experiment_no_meas['params']['_pd_meas']['2theta_range_max'] = dict(Parameter(
                            item.ttheta_max,
                            optional = True,
                            category = '_pd_meas',
                            name = '2theta_range_max',
                            prettyName = 'range max',
                            shortPrettyName = 'max',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/',
                            cifDict = 'pd'
                        ))
                        ed_experiment_no_meas['params']['_pd_meas']['2theta_range_inc'] = dict(Parameter(
                            0.1,  # default value to be updated later
                            optional = True,
                            category = '_pd_meas',
                            name = '2theta_range_inc',
                            prettyName = 'range inc',
                            shortPrettyName = 'inc',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/',
                            cifDict = 'pd'
                        ))

                # Start from the beginnig after reading ranges
                for item in cryspy_experiment:

                    # DATABLOCK SINGLES

                    # Setup section (cryspy)
                    if type(item) == cryspy.C_item_loop_classes.cl_1_setup.Setup:
                        if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                        ed_experiment_no_meas['params']['_diffrn_radiation']['probe'] = dict(Parameter(
                            item.radiation.replace('neutrons', 'neutron').replace('X-rays', 'x-ray'),  # NEED FIX
                            permittedValues = ['neutron', 'x-ray'],
                            category = '_diffrn_radiation',
                            name = 'probe',
                            shortPrettyName = 'probe',
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_diffrn_radiation/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_diffrn_radiation/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_calib/',
                            cifDict = 'pd',
                            absDelta = 0.2,
                            units = '°',
                            fittable = True,
                            fit = item.offset_ttheta_refinement
                        ))

                    # Instrument resolution section (cryspy)
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_instr_resolution.PdInstrResolution:
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
                            absDelta = 0.1,
                            fittable = True,
                            fit = item.y_refinement
                        ))

                    # Peak assymetries section (cryspy)
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_instr_reflex_asymmetry.PdInstrReflexAsymmetry:
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.p4_refinement))

                    # Phases section (cryspy)
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_phase.PhaseL:
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
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_phase/',
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
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_phase/',
                                cifDict = 'pd',
                                pctDelta = 25,
                                fittable = True,
                                fit = cryspy_phase.scale_refinement
                            ))
                            ed_phases.append(ed_phase)
                        ed_experiment_no_meas['loops']['_pd_phase_block'] = ed_phases

                    # Background section (cryspy)
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_background.PdBackgroundL:
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
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_background/',
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
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_background/',
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
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_background/',
                                cifDict = 'pd'
                            ))
                            ed_bkg_points.append(ed_bkg_point)
                        ed_experiment_no_meas['loops']['_pd_background'] = ed_bkg_points

                    # Measured data section (cryspy)
                    elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_meas.PdMeasL:
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
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_meas/',
                                cifDict = 'pd'
                            ))
                            ed_meas_point['intensity_total'] = dict(Parameter(
                                cryspy_meas_point.intensity,
                                idx = idx,
                                category = '_pd_meas',
                                name = 'intensity_total',
                                shortPrettyName = 'I',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_meas/',
                                cifDict = 'pd'
                            ))
                            ed_meas_point['intensity_total_su'] = dict(Parameter(
                                cryspy_meas_point.intensity_sigma,
                                idx = idx,
                                category = '_pd_meas',
                                name = 'intensity_total_su',
                                shortPrettyName = 'sI',
                                url = 'https://docs.easydiffraction.org/app/project/dictionaries/_pd_meas/',
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
