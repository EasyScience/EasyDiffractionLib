# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import numpy as np

try:
    import cryspy
except ImportError:
    print('No CrysPy module found')


class Parameter(dict):
    def __init__(
        self,
        value,
        permittedValues=None,
        idx=0,
        error=0.0,
        min=-np.inf,
        max=np.inf,
        absDelta=None,
        pctDelta=None,
        unit='',
        category='',
        prettyCategory='',
        rowName='',
        name='',
        prettyName='',
        shortPrettyName='',
        icon='',
        categoryIcon='',
        url='',
        cifDict='',
        optional=False,
        enabled=True,
        fittable=False,
        fit=False,
    ):
        self['value'] = value
        self['permittedValues'] = permittedValues
        self['idx'] = idx
        self['optional'] = optional
        self['enabled'] = enabled
        self['fittable'] = fittable
        self['fit'] = fit
        self['error'] = error
        self['group'] = ''
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
        self['unit'] = unit

def calcObjAndDictToEdExperiments(cryspy_obj, cryspy_dict):  # NEED to be modified similar to cryspyObjAndDictToEdModels -> cryspyObjToEdModels

    experiment_names = []
    # possible experiment prefixes
    exp_substrings = ['pd_',  # 'pd-cwl
                        'tof_',  # 'pd-tof'
                        'diffrn_',  # 'sg-cwl'
                        'data_']
    # get experiment names from cryspy_dict
    for key in cryspy_dict.keys():
        for substring in exp_substrings:
            if key.startswith(substring):
                key = key.replace(substring, "").replace("_", "")
                experiment_names.append(key)

    ed_experiments_meas_only = []
    ed_experiments_no_meas = []

    for data_block in cryspy_obj.items:
        data_block_name = data_block.data_name

        if data_block_name in experiment_names:
            cryspy_experiment = data_block.items
            ed_experiment_no_meas = {'name': '', 'params': {}, 'loops': {}}
            ed_experiment_meas_only = {'name': '', 'loops': {}}

            # DATABLOCK ID

            ed_experiment_no_meas['name'] = dict(Parameter(
                data_block_name,
                icon = 'microscope',
                url = 'https://docs.easydiffraction.org/app/dictionaries/',
            ))
            ed_experiment_meas_only['name'] = dict(Parameter(
                data_block_name,
                icon = 'microscope',
                url = 'https://docs.easydiffraction.org/app/dictionaries/',
            ))

            for item in cryspy_experiment:

                # DATABLOCK SINGLES

                # Ranges category
                if type(item) == cryspy.C_item_loop_classes.cl_1_range.Range:
                    ed_experiment_no_meas['params']['_pd_meas'] = {}
                    # pd-cwl ranges
                    if hasattr(item, 'ttheta_min') and hasattr(item, 'ttheta_max'):
                        ed_experiment_no_meas['params']['_pd_meas']['2theta_range_min'] = dict(Parameter(
                            item.ttheta_min,
                            optional = True,
                            category = '_pd_meas',
                            name = '2theta_range_min',
                            prettyName = 'range min',
                            shortPrettyName = 'min',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/',
                            cifDict = 'pd'
                        ))
                        ed_experiment_no_meas['params']['_pd_meas']['2theta_range_max'] = dict(Parameter(
                            item.ttheta_max,
                            optional = True,
                            category = '_pd_meas',
                            name = '2theta_range_max',
                            prettyName = 'range max',
                            shortPrettyName = 'max',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/',
                            cifDict = 'pd'
                        ))
                        ed_experiment_no_meas['params']['_pd_meas']['2theta_range_inc'] = dict(Parameter(
                            0.1,  # initial value to be updated later
                            optional = True,
                            category = '_pd_meas',
                            name = '2theta_range_inc',
                            prettyName = 'range inc',
                            shortPrettyName = 'inc',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/',
                            cifDict = 'pd'
                        ))
                    # pd-tof ranges
                    elif hasattr(item, 'time_min') and hasattr(item, 'time_max'):
                        ed_experiment_no_meas['params']['_pd_meas']['tof_range_min'] = dict(Parameter(
                            item.time_min,
                            optional = True,
                            category = '_pd_meas',
                            name = 'tof_range_min',
                            prettyName = 'range min',
                            shortPrettyName = 'min',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/'
                        ))
                        ed_experiment_no_meas['params']['_pd_meas']['tof_range_max'] = dict(Parameter(
                            item.time_max,
                            optional = True,
                            category = '_pd_meas',
                            name = 'tof_range_max',
                            prettyName = 'range max',
                            shortPrettyName = 'max',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/'
                        ))
                        ed_experiment_no_meas['params']['_pd_meas']['tof_range_inc'] = dict(Parameter(
                            10.0,  # initial value to be updated later
                            optional = True,
                            category = '_pd_meas',
                            name = 'tof_range_inc',
                            prettyName = 'range inc',
                            shortPrettyName = 'inc',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/'
                        ))

            # Start from the beginning after reading ranges
            for item in cryspy_experiment:

                # DATABLOCK SINGLES

                # Phase(s) section
                # pd-cwl and pd-tof phases
                if type(item) is cryspy.C_item_loop_classes.cl_1_phase.PhaseL:
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_phase/',
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_phase/',
                            cifDict = 'pd',
                            pctDelta = 25,
                            fittable = True,
                            fit = cryspy_phase.scale_refinement
                        ))
                        ed_phases.append(ed_phase)
                    ed_experiment_no_meas['loops']['_pd_phase_block'] = ed_phases
                # sg-cwl phase
                elif type(item) is cryspy.C_item_loop_classes.cl_1_phase.Phase:
                    cryspy_phases = [item]
                    ed_phases = []
                    for idx, cryspy_phase in enumerate(cryspy_phases):
                        ed_phase = {}
                        ed_phase['id'] = dict(Parameter(
                            cryspy_phase.label,
                            idx = idx,
                            category = '_exptl_crystal',
                            name = 'id',
                            shortPrettyName = 'label',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_phase/',
                            cifDict = 'core'
                        ))
                        ed_phase['scale'] = dict(Parameter(
                            cryspy_phase.scale,
                            error = cryspy_phase.scale_sigma,
                            idx = idx,
                            category = '_exptl_crystal',
                            prettyCategory = 'phase',
                            rowName = cryspy_phase.label,
                            name = 'scale',
                            prettyName = 'scale',
                            shortPrettyName = 'scale',
                            icon = 'weight',
                            categoryIcon = 'layer-group',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_phase/',
                            cifDict = 'core',
                            pctDelta = 25,
                            fittable = True,
                            fit = cryspy_phase.scale_refinement
                        ))
                        ed_phases.append(ed_phase)
                    ed_experiment_no_meas['loops']['_exptl_crystal'] = ed_phases

                # Cryspy setup section (TOF/CWL)
                elif type(item) == cryspy.C_item_loop_classes.cl_1_setup.Setup:
                    if hasattr(item, 'radiation'):
                        if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                        ed_experiment_no_meas['params']['_diffrn_radiation']['probe'] = dict(Parameter(
                            item.radiation.replace('neutrons', 'neutron').replace('X-rays', 'x-ray'),  # NEED FIX
                            permittedValues = ['neutron', 'x-ray'],
                            category = '_diffrn_radiation',
                            name = 'probe',
                            shortPrettyName = 'probe',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/',
                            cifDict = 'core'
                        ))
                    if hasattr(item, 'wavelength'):
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/',
                            cifDict = 'core',
                            absDelta = 0.01,
                            units = 'Å',
                            fittable = True,
                            fit = item.wavelength_refinement
                        ))
                    if hasattr(item, 'offset_ttheta'):
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_calib/',
                            cifDict = 'pd',
                            absDelta = 0.2,
                            units = '°',
                            fittable = True,
                            fit = item.offset_ttheta_refinement
                        ))

                # Cryspy extinction parameters section
                # sg-cwl
                elif type(item) is cryspy.C_item_loop_classes.cl_1_extinction.Extinction:
                    if hasattr(item, 'model') and hasattr(item, 'mosaicity') and hasattr(item, 'radius'):
                        if '_extinction' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_extinction'] = {}
                        ed_experiment_no_meas['params']['_extinction']['model'] = dict(Parameter(
                            item.model,
                            category = '_extinction',
                            prettyCategory = 'ext',
                            name = 'model',
                            prettyName = 'model',
                            shortPrettyName = 'model',
                            icon = 'arrow-down',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/'
                        ))
                        ed_experiment_no_meas['params']['_extinction']['mosaicity'] = dict(Parameter(
                            item.mosaicity,
                            error = item.mosaicity_sigma,
                            category = '_extinction',
                            prettyCategory = 'ext',
                            name = 'mosaicity',
                            prettyName = 'mosaicity',
                            shortPrettyName = 'mosaicity',  # NEED FIX: rename to one letter...
                            icon = 'arrow-down',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.mosaicity_refinement
                        ))
                        ed_experiment_no_meas['params']['_extinction']['radius'] = dict(Parameter(
                            item.radius,
                            error = item.radius_sigma,
                            category = '_extinction',
                            prettyCategory = 'ext',
                            name = 'radius',
                            prettyName = 'radius',
                            shortPrettyName = 'radius',  # NEED FIX: rename to one letter...
                            icon = 'arrow-down',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.radius_refinement
                        ))

                # Cryspy instrument resolution section (CWL)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_pd_instr_resolution.PdInstrResolution:
                    if hasattr(item, 'u') and hasattr(item, 'v') and hasattr(item, 'w') and hasattr(item, 'x') and hasattr(item, 'y'):
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
                            icon = 'shapes',  # 'grip-lines-vertical'
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            icon = 'shapes',  # 'grip-lines-vertical'
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            icon = 'shapes',  # 'grip-lines-vertical'
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            icon = 'shapes',  # 'grip-lines-vertical'
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            icon = 'shapes',  # 'grip-lines-vertical'
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.1,
                            fittable = True,
                            fit = item.y_refinement
                        ))

                # Cryspy peak asymmetries section (CWL)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_pd_instr_reflex_asymmetry.PdInstrReflexAsymmetry:
                    if hasattr(item, 'p1') and hasattr(item, 'p2') and hasattr(item, 'p3') and hasattr(item, 'p4'):
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.p4_refinement
                        ))

                # Cryspy parameters section (TOF)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_tof_parameters.TOFParameters:
                    if hasattr(item, 'zero') and hasattr(item, 'dtt1') and hasattr(item, 'dtt2') and hasattr(item, 'ttheta_bank'):
                        if '_pd_instr' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_pd_instr'] = {}
                        ed_experiment_no_meas['params']['_pd_instr']['2theta_bank'] = dict(Parameter(
                            item.ttheta_bank,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = '2theta_bank',
                            prettyName = '2theta bank',
                            shortPrettyName = '2θ bank',
                            icon = 'hashtag',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            fittable = False
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['dtt1'] = dict(Parameter(
                            item.dtt1,
                            error = item.dtt1_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'dtt1',  # DIFC in GSAS
                            prettyName = 'dtt1',
                            shortPrettyName = 'dtt1',
                            icon = 'radiation',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 100.0,
                            fittable = True,
                            fit = item.dtt1_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['dtt2'] = dict(Parameter(
                            item.dtt2,
                            error = item.dtt2_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'dtt2',  # DIFA in GSAS
                            prettyName = 'dtt2',
                            shortPrettyName = 'dtt2',
                            icon = 'radiation',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.1,
                            fittable = True,
                            fit = item.dtt2_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['zero'] = dict(Parameter(
                            item.zero,
                            error = item.zero_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'zero',  # TZERO in GSAS
                            prettyName = 'zero',
                            shortPrettyName = 'zero',
                            icon = 'arrows-alt-h',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.zero_refinement
                        ))

                # Cryspy peak profile section (TOF)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_tof_profile.TOFProfile:
                    if hasattr(item, 'alpha0') and hasattr(item, 'beta0') and hasattr(item, 'sigma0'):
                        if '_pd_instr' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_pd_instr'] = {}
                        ed_experiment_no_meas['params']['_pd_instr']['alpha0'] = dict(Parameter(
                            item.alpha0,
                            error = item.alpha0_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'alpha0',
                            prettyName = 'alpha0',
                            shortPrettyName = 'α0',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.alpha0_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['alpha1'] = dict(Parameter(
                            item.alpha1,
                            error = item.alpha1_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'alpha1',
                            prettyName = 'alpha1',
                            shortPrettyName = 'α1',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.alpha1_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['beta0'] = dict(Parameter(
                            item.beta0,
                            error = item.beta0_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'beta0',
                            prettyName = 'beta0',
                            shortPrettyName = 'β0',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.beta0_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['beta1'] = dict(Parameter(
                            item.beta1,
                            error = item.beta1_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'beta1',
                            prettyName = 'beta1',
                            shortPrettyName = 'β1',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.beta1_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['sigma0'] = dict(Parameter(
                            item.sigma0,
                            error = item.sigma0_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'sigma0',
                            prettyName = 'sigma0',
                            shortPrettyName = 'σ0',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.sigma0_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['sigma1'] = dict(Parameter(
                            item.sigma1,
                            error = item.sigma1_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'sigma1',
                            prettyName = 'sigma1',
                            shortPrettyName = 'σ1',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.sigma1_refinement
                        ))
                    if hasattr(item, 'sigma2'):
                        if '_pd_instr' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_pd_instr'] = {}
                        ed_experiment_no_meas['params']['_pd_instr']['sigma2'] = dict(Parameter(
                            item.sigma2,
                            error = item.sigma2_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'sigma2',
                            prettyName = 'sigma2',
                            shortPrettyName = 'σ2',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.sigma2_refinement
                        ))
                    if hasattr(item, 'gamma0') and hasattr(item, 'gamma1') and hasattr(item, 'gamma2'):
                        if '_pd_instr' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_pd_instr'] = {}
                        ed_experiment_no_meas['params']['_pd_instr']['gamma0'] = dict(Parameter(
                            item.gamma0,
                            error = item.gamma0_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'gamma0',
                            prettyName = 'gamma0',
                            shortPrettyName = 'γ0',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.gamma0_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['gamma1'] = dict(Parameter(
                            item.gamma1,
                            error = item.gamma1_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'gamma1',
                            prettyName = 'gamma1',
                            shortPrettyName = 'γ1',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.gamma1_refinement
                        ))
                        ed_experiment_no_meas['params']['_pd_instr']['gamma2'] = dict(Parameter(
                            item.gamma2,
                            error = item.gamma2_sigma,
                            category = '_pd_instr',
                            prettyCategory = 'inst',
                            name = 'gamma2',
                            prettyName = 'gamma2',
                            shortPrettyName = 'γ2',
                            icon = 'shapes',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                            absDelta = 0.5,
                            fittable = True,
                            fit = item.gamma2_refinement
                        ))

                # Cryspy background section (TOF, points)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_tof_background_by_points.TOFBackgroundPointL:
                    cryspy_bkg_points = item.items
                    ed_bkg_points = []
                    for idx, cryspy_bkg_point in enumerate(cryspy_bkg_points):
                        ed_bkg_point = {}
                        ed_bkg_point['line_segment_X'] = dict(Parameter(
                            cryspy_bkg_point.time,
                            idx = idx,
                            category = '_pd_background',
                            name = 'line_segment_X',
                            prettyName = 'TOF',
                            shortPrettyName = 'TOF',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            cifDict = 'pd'
                        ))
                        ed_bkg_point['line_segment_intensity'] = dict(Parameter(
                            cryspy_bkg_point.intensity,
                            error = cryspy_bkg_point.intensity_sigma,
                            idx = idx,
                            category = '_pd_background',
                            prettyCategory = 'bkg',
                            rowName = f'{cryspy_bkg_point.time:g}µs',  # formatting float to str without trailing zeros
                            name = 'line_segment_intensity',
                            prettyName = 'intensity',
                            shortPrettyName = 'Ibkg',
                            icon = 'mountain',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            cifDict = 'pd',
                            pctDelta = 25,
                            fittable = True,
                            fit = cryspy_bkg_point.intensity_refinement
                        ))
                        ed_bkg_point['X_coordinate'] = dict(Parameter(
                            'time-of-flight',
                            idx = idx,
                            category = '_pd_background',
                            name = 'X_coordinate',
                            prettyName = 'X coord',
                            shortPrettyName = 'X coord',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            cifDict = 'pd'
                        ))
                        ed_bkg_points.append(ed_bkg_point)
                    ed_experiment_no_meas['loops']['_pd_background'] = ed_bkg_points

                # Cryspy background section (TOF, polinom coeffs)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_tof_background.TOFBackground:
                    if hasattr(item, 'time_max'):
                        if '_tof_background' not in ed_experiment_no_meas['params']:
                            ed_experiment_no_meas['params']['_tof_background'] = {}
                        ed_experiment_no_meas['params']['_tof_background']['time_max'] = dict(Parameter(
                            item.time_max,
                            optional=True,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'time_max',  # Is this the name used on save cif?
                            prettyName = 'TOF max',
                            shortPrettyName = 'max',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_instr/',
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff1'] = dict(Parameter(
                            item.coeff1 if hasattr(item, 'coeff1') else 0.0,
                            error = item.coeff1_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff1',
                            prettyName = 'coeff1',
                            shortPrettyName = 'c1',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff1_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff2'] = dict(Parameter(
                            item.coeff2 if hasattr(item, 'coeff2') else 0.0,
                            error = item.coeff2_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff2',
                            prettyName = 'coeff2',
                            shortPrettyName = 'c2',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff2_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff3'] = dict(Parameter(
                            item.coeff3 if hasattr(item, 'coeff3') else 0.0,
                            error = item.coeff3_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff3',
                            prettyName = 'coeff3',
                            shortPrettyName = 'c3',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff3_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff4'] = dict(Parameter(
                            item.coeff4 if hasattr(item, 'coeff4') else 0.0,
                            error = item.coeff4_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff4',
                            prettyName = 'coeff4',
                            shortPrettyName = 'c4',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff4_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff5'] = dict(Parameter(
                            item.coeff5 if hasattr(item, 'coeff5') else 0.0,
                            error = item.coeff5_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff5',
                            prettyName = 'coeff5',
                            shortPrettyName = 'c5',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff5_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff6'] = dict(Parameter(
                            item.coeff6 if hasattr(item, 'coeff6') else 0.0,
                            error = item.coeff6_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff6',
                            prettyName = 'coeff6',
                            shortPrettyName = 'c6',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff6_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff7'] = dict(Parameter(
                            item.coeff7 if hasattr(item, 'coeff7') else 0.0,
                            error = item.coeff7_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff7',
                            prettyName = 'coeff7',
                            shortPrettyName = 'c7',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff7_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff8'] = dict(Parameter(
                            item.coeff8 if hasattr(item, 'coeff8') else 0.0,
                            error = item.coeff8_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff8',
                            prettyName = 'coeff8',
                            shortPrettyName = 'c8',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff8_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff9'] = dict(Parameter(
                            item.coeff9 if hasattr(item, 'coeff9') else 0.0,
                            error = item.coeff9_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff9',
                            prettyName = 'coeff9',
                            shortPrettyName = 'c9',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff9_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff10'] = dict(Parameter(
                            item.coeff10 if hasattr(item, 'coeff10') else 0.0,
                            error = item.coeff10_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff10',
                            prettyName = 'coeff10',
                            shortPrettyName = 'c10',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff10_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff11'] = dict(Parameter(
                            item.coeff11 if hasattr(item, 'coeff11') else 0.0,
                            error = item.coeff11_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff11',
                            prettyName = 'coeff11',
                            shortPrettyName = 'c11',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff11_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff12'] = dict(Parameter(
                            item.coeff12 if hasattr(item, 'coeff12') else 0.0,
                            error = item.coeff12_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff12',
                            prettyName = 'coeff12',
                            shortPrettyName = 'c12',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff12_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff13'] = dict(Parameter(
                            item.coeff13 if hasattr(item, 'coeff13') else 0.0,
                            error = item.coeff13_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff13',
                            prettyName = 'coeff13',
                            shortPrettyName = 'c13',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff13_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff14'] = dict(Parameter(
                            item.coeff14 if hasattr(item, 'coeff14') else 0.0,
                            error = item.coeff14_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff14',
                            prettyName = 'coeff14',
                            shortPrettyName = 'c14',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff14_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff15'] = dict(Parameter(
                            item.coeff15 if hasattr(item, 'coeff15') else 0.0,
                            error = item.coeff15_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff15',
                            prettyName = 'coeff15',
                            shortPrettyName = 'c15',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff15_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff16'] = dict(Parameter(
                            item.coeff16 if hasattr(item, 'coeff16') else 0.0,
                            error = item.coeff16_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff16',
                            prettyName = 'coeff16',
                            shortPrettyName = 'c16',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff16_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff17'] = dict(Parameter(
                            item.coeff17 if hasattr(item, 'coeff17') else 0.0,
                            error = item.coeff17_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff17',
                            prettyName = 'coeff17',
                            shortPrettyName = 'c17',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff17_refinement
                        ))
                        ed_experiment_no_meas['params']['_tof_background']['coeff18'] = dict(Parameter(
                            item.coeff18 if hasattr(item, 'coeff18') else 0.0,
                            error = item.coeff18_sigma,
                            category = '_tof_background',
                            prettyCategory = 'bkg',
                            name = 'coeff18',
                            prettyName = 'coeff18',
                            shortPrettyName = 'c18',
                            categoryIcon = 'wave-square',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            pctDelta = 25,
                            fittable = True,
                            fit = item.coeff18_refinement
                        ))

                # Cryspy background section (CWL, points)
                elif type(item) is cryspy.C_item_loop_classes.cl_1_pd_background.PdBackgroundL:
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_background/',
                            cifDict = 'pd'
                        ))
                        ed_bkg_points.append(ed_bkg_point)
                    ed_experiment_no_meas['loops']['_pd_background'] = ed_bkg_points

                # Cryspy measured data section: pd-tof
                elif type(item) is cryspy.C_item_loop_classes.cl_1_tof_meas.TOFMeasL:
                    if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation']['type'] = dict(Parameter(
                        'tof',
                        optional=True,
                        category='_diffrn_radiation',
                        name='type',
                        shortPrettyName='type',
                        url='https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/'
                    ))
                    if '_sample' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_sample'] = {}
                    ed_experiment_no_meas['params']['_sample']['type'] = dict(Parameter(
                        'pd',
                        optional=True,
                        category='_sample',
                        name='type',  # NEED FIX. If needed, should be different form _diffrn_radiation.type
                        shortPrettyName='type',  # NEED FIX. If needed, should be different form _diffrn_radiation.type
                        url='https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/'  # NEED FIX
                    ))
                    cryspy_meas_points = item.items
                    ed_meas_points = []
                    for idx, cryspy_meas_point in enumerate(cryspy_meas_points):
                        ed_meas_point = {}
                        ed_meas_point['time_of_flight'] = dict(Parameter(
                            cryspy_meas_point.time,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'time_of_flight',
                            shortPrettyName = 'tof',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_point['intensity_total'] = dict(Parameter(
                            cryspy_meas_point.intensity,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'intensity_total',
                            shortPrettyName = 'I',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_point['intensity_total_su'] = dict(Parameter(
                            cryspy_meas_point.intensity_sigma,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'intensity_total_su',
                            shortPrettyName = 'sI',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_points.append(ed_meas_point)
                    ed_experiment_meas_only['loops']['_pd_meas'] = ed_meas_points

                    # Modify range_inc based on the measured data points in _pd_meas loop
                    pd_meas_range_min = ed_meas_points[0]['time_of_flight']['value']
                    pd_meas_range_max = ed_meas_points[-1]['time_of_flight']['value']
                    pd_meas_range_inc = (pd_meas_range_max - pd_meas_range_min) / (len(ed_meas_points) - 1)
                    ed_experiment_no_meas['params']['_pd_meas']['tof_range_inc']['value'] = pd_meas_range_inc

                # Cryspy measured data section: pd-cwl
                elif type(item) is cryspy.C_item_loop_classes.cl_1_pd_meas.PdMeasL:
                    if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation']['type'] = dict(Parameter(
                        'cwl',
                        optional=True,
                        category='_diffrn_radiation',
                        name='type',
                        shortPrettyName='type',
                        url='https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/'
                    ))
                    if '_sample' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_sample'] = {}
                    ed_experiment_no_meas['params']['_sample']['type'] = dict(Parameter(
                        'pd',
                        optional=True,
                        category='_sample',
                        name='type',  # NEED FIX. If needed, should be different form _diffrn_radiation.type
                        shortPrettyName='type',  # NEED FIX. If needed, should be different form _diffrn_radiation.type
                        url='https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/'  # NEED FIX
                    ))
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
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_point['intensity_total'] = dict(Parameter(
                            cryspy_meas_point.intensity,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'intensity_total',
                            shortPrettyName = 'I',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_point['intensity_total_su'] = dict(Parameter(
                            cryspy_meas_point.intensity_sigma,
                            idx = idx,
                            category = '_pd_meas',
                            name = 'intensity_total_su',
                            shortPrettyName = 'sI',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'pd'
                        ))
                        ed_meas_points.append(ed_meas_point)
                    ed_experiment_meas_only['loops']['_pd_meas'] = ed_meas_points

                    # Modify range_inc based on the measured data points in _pd_meas loop
                    pd_meas_range_min = ed_meas_points[0]['2theta_scan']['value']
                    pd_meas_range_max = ed_meas_points[-1]['2theta_scan']['value']
                    pd_meas_range_inc = (pd_meas_range_max - pd_meas_range_min) / (len(ed_meas_points) - 1)
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_inc']['value'] = pd_meas_range_inc

                # Cryspy measured data section: sg-cwl
                elif type(item) is cryspy.C_item_loop_classes.cl_1_diffrn_refln.DiffrnReflnL:
                    if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation']['type'] = dict(Parameter(
                        'cwl',
                        optional=True,
                        category='_diffrn_radiation',
                        name='type',
                        shortPrettyName='type',
                        url='https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/'
                    ))
                    if '_sample' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_sample'] = {}
                    ed_experiment_no_meas['params']['_sample']['type'] = dict(Parameter(
                        'sg',
                        optional=True,
                        category='_sample',
                        name='type',  # NEED FIX. If needed, should be different form _diffrn_radiation.type
                        shortPrettyName='type',  # NEED FIX. If needed, should be different form _diffrn_radiation.type
                        url='https://docs.easydiffraction.org/app/dictionaries/_diffrn_radiation/'  # NEED FIX
                    ))
                    cryspy_meas_points = item.items
                    ed_meas_points = []
                    for idx, cryspy_meas_point in enumerate(cryspy_meas_points):
                        ed_meas_point = {}
                        ed_meas_point['index_h'] = dict(Parameter(
                            cryspy_meas_point.index_h,
                            idx = idx,
                            category = '_refln',
                            name = 'index_h',
                            shortPrettyName = 'h',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'core'
                        ))
                        ed_meas_point['index_k'] = dict(Parameter(
                            cryspy_meas_point.index_k,
                            idx = idx,
                            category = '_refln',
                            name = 'index_k',
                            shortPrettyName = 'k',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'core'
                        ))
                        ed_meas_point['index_l'] = dict(Parameter(
                            cryspy_meas_point.index_l,
                            idx = idx,
                            category = '_refln',
                            name = 'index_l',
                            shortPrettyName = 'l',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'core'
                        ))
                        ed_meas_point['intensity_total'] = dict(Parameter(
                            cryspy_meas_point.intensity,
                            idx = idx,
                            category = '_refln',
                            name = 'intensity_meas',
                            shortPrettyName = 'I',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'core'
                        ))
                        ed_meas_point['intensity_total_su'] = dict(Parameter(
                            cryspy_meas_point.intensity_sigma,
                            idx = idx,
                            category = '_refln',
                            name = 'intensity_meas_su',
                            shortPrettyName = 'sI',
                            url = 'https://docs.easydiffraction.org/app/dictionaries/_pd_meas/',
                            cifDict = 'core'
                        ))
                        ed_meas_points.append(ed_meas_point)
                    ed_experiment_meas_only['loops']['_refln'] = ed_meas_points

        if ed_experiment_meas_only is not None:
            ed_experiments_meas_only.append(ed_experiment_meas_only)
        if ed_experiment_no_meas is not None:
            ed_experiments_no_meas.append(ed_experiment_no_meas)

    return ed_experiments_meas_only, ed_experiments_no_meas


def calcObjAndDictToEdExperiments_old(calc_obj, calc_dict):
    experiment_names = []
    exp_substrings = ['pd_', 'data_']  # possible experiment prefixes
    # get experiment names from cryspy_dict
    for key in calc_dict.keys():
        for substring in exp_substrings:
            if key.startswith(substring):
                key = key.replace(substring, '').replace('_', '')
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

            ed_experiment_no_meas['name'] = dict(
                Parameter(
                    data_block_name,
                    icon='microscope',
                    url='https://docs.easydiffraction.org/lib/dictionaries/',
                )
            )
            ed_experiment_meas_only['name'] = dict(
                Parameter(
                    data_block_name,
                    icon='microscope',
                    url='https://docs.easydiffraction.org/lib/dictionaries/',
                )
            )

            for item in cryspy_experiment:
                # DATABLOCK SINGLES

                # Ranges category
                if isinstance(item, cryspy.C_item_loop_classes.cl_1_range.Range):
                    ed_experiment_no_meas['params']['_pd_meas'] = {}
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_min'] = dict(
                        Parameter(
                            item.ttheta_min,
                            optional=True,
                            category='_pd_meas',
                            name='2theta_range_min',
                            prettyName='range min',
                            shortPrettyName='min',
                            url='https://docs.easydiffraction.org/lib/dictionaries/',
                            cifDict='pd',
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_max'] = dict(
                        Parameter(
                            item.ttheta_max,
                            optional=True,
                            category='_pd_meas',
                            name='2theta_range_max',
                            prettyName='range max',
                            shortPrettyName='max',
                            url='https://docs.easydiffraction.org/lib/dictionaries/',
                            cifDict='pd',
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_meas']['2theta_range_inc'] = dict(
                        Parameter(
                            0.1,  # default value to be updated later
                            optional=True,
                            category='_pd_meas',
                            name='2theta_range_inc',
                            prettyName='range inc',
                            shortPrettyName='inc',
                            url='https://docs.easydiffraction.org/lib/dictionaries/',
                            cifDict='pd',
                        )
                    )

            # Start from the beginnig after reading ranges
            for item in cryspy_experiment:
                # DATABLOCK SINGLES

                # Setup section (cryspy)
                if isinstance(item, cryspy.C_item_loop_classes.cl_1_setup.Setup):
                    if '_diffrn_radiation' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation']['probe'] = dict(
                        Parameter(
                            item.radiation.replace('neutrons', 'neutron').replace('X-rays', 'x-ray'),  # NEED FIX
                            permittedValues=['neutron', 'x-ray'],
                            category='_diffrn_radiation',
                            name='probe',
                            shortPrettyName='probe',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_diffrn_radiation/',
                            cifDict='core',
                        )
                    )
                    if '_diffrn_radiation_wavelength' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_diffrn_radiation_wavelength'] = {}
                    ed_experiment_no_meas['params']['_diffrn_radiation_wavelength']['wavelength'] = dict(
                        Parameter(
                            item.wavelength,
                            error=item.wavelength_sigma,
                            category='_diffrn_radiation_wavelength',
                            prettyCategory='radiation',
                            name='wavelength',
                            prettyName='wavelength',
                            shortPrettyName='wavelength',
                            icon='radiation',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_diffrn_radiation/',
                            cifDict='core',
                            absDelta=0.01,
                            unit='Å',
                            fittable=True,
                            fit=item.wavelength_refinement,
                        )
                    )
                    if '_pd_calib' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_pd_calib'] = {}
                    ed_experiment_no_meas['params']['_pd_calib']['2theta_offset'] = dict(
                        Parameter(
                            item.offset_ttheta,
                            error=item.offset_ttheta_sigma,
                            category='_pd_calib',
                            prettyCategory='calib',
                            name='2theta_offset',
                            prettyName='2θ offset',
                            shortPrettyName='offset',
                            icon='arrows-alt-h',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_calib/',
                            cifDict='pd',
                            absDelta=0.2,
                            unit='°',
                            fittable=True,
                            fit=item.offset_ttheta_refinement,
                        )
                    )

                # Instrument resolution section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_instr_resolution.PdInstrResolution):
                    if '_pd_instr' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_pd_instr'] = {}
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_u'] = dict(
                        Parameter(
                            item.u,
                            error=item.u_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='resolution_u',
                            prettyName='resolution u',
                            shortPrettyName='u',
                            icon='grip-lines-vertical',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.1,
                            fittable=True,
                            fit=item.u_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_v'] = dict(
                        Parameter(
                            item.v,
                            error=item.v_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='resolution_v',
                            prettyName='resolution v',
                            shortPrettyName='v',
                            icon='grip-lines-vertical',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.1,
                            fittable=True,
                            fit=item.v_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_w'] = dict(
                        Parameter(
                            item.w,
                            error=item.w_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='resolution_w',
                            prettyName='resolution w',
                            shortPrettyName='w',
                            icon='grip-lines-vertical',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.1,
                            fittable=True,
                            fit=item.w_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_x'] = dict(
                        Parameter(
                            item.x,
                            error=item.x_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='resolution_x',
                            prettyName='resolution x',
                            shortPrettyName='x',
                            icon='grip-lines-vertical',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.1,
                            fittable=True,
                            fit=item.x_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['resolution_y'] = dict(
                        Parameter(
                            item.y,
                            error=item.y_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='resolution_y',
                            prettyName='resolution y',
                            shortPrettyName='y',
                            icon='grip-lines-vertical',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.1,
                            fittable=True,
                            fit=item.y_refinement,
                        )
                    )

                # Peak assymetries section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_instr_reflex_asymmetry.PdInstrReflexAsymmetry):
                    if '_pd_instr' not in ed_experiment_no_meas['params']:
                        ed_experiment_no_meas['params']['_pd_instr'] = {}
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p1'] = dict(
                        Parameter(
                            item.p1,
                            error=item.p1_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='reflex_asymmetry_p1',
                            prettyName='asymmetry p1',
                            shortPrettyName='p1',
                            icon='balance-scale-left',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.5,
                            fittable=True,
                            fit=item.p1_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p2'] = dict(
                        Parameter(
                            item.p2,
                            error=item.p2_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='reflex_asymmetry_p2',
                            prettyName='asymmetry p2',
                            shortPrettyName='p2',
                            icon='balance-scale-left',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.5,
                            fittable=True,
                            fit=item.p2_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p3'] = dict(
                        Parameter(
                            item.p3,
                            error=item.p3_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='reflex_asymmetry_p3',
                            prettyName='asymmetry p3',
                            shortPrettyName='p3',
                            icon='balance-scale-left',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.5,
                            fittable=True,
                            fit=item.p3_refinement,
                        )
                    )
                    ed_experiment_no_meas['params']['_pd_instr']['reflex_asymmetry_p4'] = dict(
                        Parameter(
                            item.p4,
                            error=item.p4_sigma,
                            category='_pd_instr',
                            prettyCategory='inst',
                            name='reflex_asymmetry_p4',
                            prettyName='asymmetry p4',
                            shortPrettyName='p4',
                            icon='balance-scale-left',
                            url='https://docs.easydiffraction.org/lib/dictionaries/_pd_instr/',
                            absDelta=0.5,
                            fittable=True,
                            fit=item.p4_refinement,
                        )
                    )

                # Phases section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_phase.PhaseL):
                    cryspy_phases = item.items
                    ed_phases = []
                    for idx, cryspy_phase in enumerate(cryspy_phases):
                        ed_phase = {}
                        ed_phase['id'] = dict(
                            Parameter(
                                cryspy_phase.label,
                                idx=idx,
                                category='_pd_phase_block',
                                name='id',
                                shortPrettyName='label',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_phase/',
                                cifDict='pd',
                            )
                        )
                        ed_phase['scale'] = dict(
                            Parameter(
                                cryspy_phase.scale,
                                error=cryspy_phase.scale_sigma,
                                idx=idx,
                                category='_pd_phase_block',
                                prettyCategory='phase',
                                rowName=cryspy_phase.label,
                                name='scale',
                                prettyName='scale',
                                shortPrettyName='scale',
                                icon='weight',
                                categoryIcon='layer-group',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_phase/',
                                cifDict='pd',
                                pctDelta=25,
                                fittable=True,
                                fit=cryspy_phase.scale_refinement,
                            )
                        )
                        ed_phases.append(ed_phase)
                    ed_experiment_no_meas['loops']['_pd_phase_block'] = ed_phases

                # Background section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_background.PdBackgroundL):
                    cryspy_bkg_points = item.items
                    ed_bkg_points = []
                    for idx, cryspy_bkg_point in enumerate(cryspy_bkg_points):
                        ed_bkg_point = {}
                        ed_bkg_point['line_segment_X'] = dict(
                            Parameter(
                                cryspy_bkg_point.ttheta,
                                idx=idx,
                                category='_pd_background',
                                name='line_segment_X',
                                prettyName='2θ',
                                shortPrettyName='2θ',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_pd_background/',
                                cifDict='pd',
                            )
                        )
                        ed_bkg_point['line_segment_intensity'] = dict(
                            Parameter(
                                cryspy_bkg_point.intensity,
                                error=cryspy_bkg_point.intensity_sigma,
                                idx=idx,
                                category='_pd_background',
                                prettyCategory='bkg',
                                rowName=f'{cryspy_bkg_point.ttheta:g}°',  # formatting float to str without trailing zeros
                                name='line_segment_intensity',
                                prettyName='intensity',
                                shortPrettyName='Ibkg',
                                icon='mountain',
                                categoryIcon='wave-square',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_pd_background/',
                                cifDict='pd',
                                pctDelta=25,
                                fittable=True,
                                fit=cryspy_bkg_point.intensity_refinement,
                            )
                        )
                        ed_bkg_point['X_coordinate'] = dict(
                            Parameter(
                                '2theta',
                                idx=idx,
                                category='_pd_background',
                                name='X_coordinate',
                                prettyName='X coord',
                                shortPrettyName='X coord',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_pd_background/',
                                cifDict='pd',
                            )
                        )
                        ed_bkg_points.append(ed_bkg_point)
                    ed_experiment_no_meas['loops']['_pd_background'] = ed_bkg_points

                # Measured data section (cryspy)
                elif isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_meas.PdMeasL):
                    cryspy_meas_points = item.items
                    ed_meas_points = []
                    for idx, cryspy_meas_point in enumerate(cryspy_meas_points):
                        ed_meas_point = {}
                        ed_meas_point['2theta_scan'] = dict(
                            Parameter(
                                cryspy_meas_point.ttheta,
                                idx=idx,
                                category='_pd_meas',
                                name='2theta_scan',
                                shortPrettyName='2θ',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_pd_meas/',
                                cifDict='pd',
                            )
                        )
                        ed_meas_point['intensity_total'] = dict(
                            Parameter(
                                cryspy_meas_point.intensity,
                                idx=idx,
                                category='_pd_meas',
                                name='intensity_total',
                                shortPrettyName='I',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_pd_meas/',
                                cifDict='pd',
                            )
                        )
                        ed_meas_point['intensity_total_su'] = dict(
                            Parameter(
                                cryspy_meas_point.intensity_sigma,
                                idx=idx,
                                category='_pd_meas',
                                name='intensity_total_su',
                                shortPrettyName='sI',
                                url='https://docs.easydiffraction.org/lib/dictionaries/_pd_meas/',
                                cifDict='pd',
                            )
                        )
                        ed_meas_points.append(ed_meas_point)
                    ed_experiment_meas_only['loops']['_pd_meas'] = ed_meas_points

                    # Modify range_inc based on the measured data points in _pd_meas loop
                    pd_meas_2theta_range_min = ed_meas_points[0]['2theta_scan']['value']
                    pd_meas_2theta_range_max = ed_meas_points[-1]['2theta_scan']['value']
                    pd_meas_2theta_range_inc = (pd_meas_2theta_range_max - pd_meas_2theta_range_min) / (
                        len(ed_meas_points) - 1
                    )
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
        '_experiment.cif_file_name': '_experiment_cif_file_name',
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
