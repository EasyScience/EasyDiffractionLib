# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import json
import os
import re
from typing import Tuple

import gemmi
import numpy as np
from easyscience import global_object as borg
from pycrysfml import cfml_utilities

DEFAULT_PHASES_JSON = [
    {
        'pbso4': {
            '_space_group_name_H-M_alt': 'P n m a',
            '_cell_length_a': 8.47793,
            '_cell_length_b': 5.39682,
            '_cell_length_c': 6.9581,
            '_cell_angle_alpha': 90.0,
            '_cell_angle_beta': 90.0,
            '_cell_angle_gamma': 90.0,
            '_atom_site': [
                {
                    '_label': 'Pb',
                    '_type_symbol': 'Pb',
                    '_fract_x': 0.18724,
                    '_fract_y': 0.25,
                    '_fract_z': 0.16615,
                    '_occupancy': 1.0,
                    '_adp_type': 'Biso',
                    '_B_iso_or_equiv': 0.5,
                },
                {
                    '_label': 'S',
                    '_type_symbol': 'S',
                    '_fract_x': 0.06434,
                    '_fract_y': 0.25,
                    '_fract_z': 0.68261,
                    '_occupancy': 1.0,
                    '_adp_type': 'Biso',
                    '_B_iso_or_equiv': 0.5,
                },
                {
                    '_label': 'O1',
                    '_type_symbol': 'O',
                    '_fract_x': 0.9079,
                    '_fract_y': 0.25,
                    '_fract_z': 0.59598,
                    '_occupancy': 1.0,
                    '_adp_type': 'Biso',
                    '_B_iso_or_equiv': 0.5,
                },
                {
                    '_label': 'O2',
                    '_type_symbol': 'O',
                    '_fract_x': 0.1926,
                    '_fract_y': 0.25,
                    '_fract_z': 0.54171,
                    '_occupancy': 1.0,
                    '_adp_type': 'Biso',
                    '_B_iso_or_equiv': 0.5,
                },
                {
                    '_label': 'O3',
                    '_type_symbol': 'O',
                    '_fract_x': 0.08043,
                    '_fract_y': 0.02893,
                    '_fract_z': 0.80734,
                    '_occupancy': 1.0,
                    '_adp_type': 'Biso',
                    '_B_iso_or_equiv': 0.5,
                },
            ],
        }
    }
]

DEFAULT_EXPERIMENT_JSON = [
    {
        'pd': {
            '_diffrn_radiation_probe': 'neutron',
            '_diffrn_radiation_wavelength': 1.912,
            '_pd_instr_resolution_u': 0.12205,
            '_pd_instr_resolution_v': -0.33588,
            '_pd_instr_resolution_w': 0.2838,
            '_pd_instr_resolution_x': 0.14871,
            '_pd_instr_resolution_y': 0.0,
            '_pd_meas_2theta_range_min': 10.0,
            '_pd_meas_2theta_range_max': 140.00,
            '_pd_meas_2theta_range_inc': 0.05,
            '_pd_meas_2theta_offset': -0.138,
        }
    }
]

EXAMPLE = {
    'phases': [
        {
            'pbso4': {
                '_space_group_name_H-M_alt': 'P n m a',
                '_cell_length_a': 8.47793,
                '_cell_length_b': 5.39682,
                '_cell_length_c': 6.9581,
                '_cell_angle_alpha': 90.0,
                '_cell_angle_beta': 90.0,
                '_cell_angle_gamma': 90.0,
                '_atom_site': [
                    {
                        '_label': 'Pb',
                        '_type_symbol': 'Pb',
                        '_fract_x': 0.18724,
                        '_fract_y': 0.25,
                        '_fract_z': 0.16615,
                        '_occupancy': 1.0,
                        '_adp_type': 'Biso',
                        '_B_iso_or_equiv': 0.5,
                    },
                    {
                        '_label': 'S',
                        '_type_symbol': 'S',
                        '_fract_x': 0.06434,
                        '_fract_y': 0.25,
                        '_fract_z': 0.68261,
                        '_occupancy': 1.0,
                        '_adp_type': 'Biso',
                        '_B_iso_or_equiv': 0.5,
                    },
                    {
                        '_label': 'O1',
                        '_type_symbol': 'O',
                        '_fract_x': 0.9079,
                        '_fract_y': 0.25,
                        '_fract_z': 0.59598,
                        '_occupancy': 1.0,
                        '_adp_type': 'Biso',
                        '_B_iso_or_equiv': 0.5,
                    },
                    {
                        '_label': 'O2',
                        '_type_symbol': 'O',
                        '_fract_x': 0.1926,
                        '_fract_y': 0.25,
                        '_fract_z': 0.54171,
                        '_occupancy': 1.0,
                        '_adp_type': 'Biso',
                        '_B_iso_or_equiv': 0.5,
                    },
                    {
                        '_label': 'O3',
                        '_type_symbol': 'O',
                        '_fract_x': 0.08043,
                        '_fract_y': 0.02893,
                        '_fract_z': 0.80734,
                        '_occupancy': 1.0,
                        '_adp_type': 'Biso',
                        '_B_iso_or_equiv': 0.5,
                    },
                ],
            }
        }
    ],
    'experiments': [
        {
            'pd': {
                '_diffrn_radiation_probe': 'neutron',
                '_diffrn_radiation_wavelength': 1.912,
                '_pd_instr_resolution_u': 0.12205,
                '_pd_instr_resolution_v': -0.33588,
                '_pd_instr_resolution_w': 0.2838,
                '_pd_instr_resolution_x': 0.14871,
                '_pd_instr_resolution_y': 0.0,
                '_pd_meas_2theta_range_min': 10.0,
                '_pd_meas_2theta_range_max': 140.00,
                '_pd_meas_2theta_range_inc': 0.05,
                '_pd_meas_2theta_offset': -0.138,
            }
        }
    ],
}


class Pycrysfml:
    def __init__(self, filename: str = None):
        self.filename = filename
        self.conditions = None
        self.background = None
        self.pattern = None
        self.model_cif = None
        self.experiment_cif = None
        self.known_phases = {}
        self.additional_data = {'phases': {}}
        self.storage = {}
        self.model_json = {}
        self.model_json['phases'] = DEFAULT_PHASES_JSON
        self.model_json['experiments'] = DEFAULT_EXPERIMENT_JSON
        self.x_coord = None

    def createConditions(self, job_type='N'):
        self.conditions = {
            'lamb': 1.54,
            'u_resolution': 0.01,
            'v_resolution': 0.0,
            'w_resolution': 0.0,
            'x_resolution': 0.0,
            'y_resolution': 0.0,
            'z_resolution': 0.0,
        }

    def conditionsUpdate(self, _, **kwargs):
        for key, value in kwargs.items():
            self.conditions[key] = value

    def conditionsReturn(self, _, name):
        return self.conditions.get(name)

    # def calculate(self, x_array: nd.ndarray) -> np.ndarray:
    #     """
    #     For a given x calculate the corresponding y
    #     :param x_array: array of data points to be calculated
    #     :type x_array: np.ndarray
    #     :return: points calculated at `x`
    #     :rtype: np.ndarray
    #     """

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value
            offset = self.pattern.zero_shift.raw_value

        if self.x_coord is not None:
            this_x_array = self.x_coord
        else:
            this_x_array = x_array + offset

        # Experiment/Instrument/Simulation parameters
        # x_min = this_x_array[0]
        # x_max = this_x_array[-1]
        # num_points = np.prod(x_array.shape)
        # x_step = (x_max - x_min) / (num_points - 1)
        bg = np.zeros_like(this_x_array)
        if self.pattern is not None and len(self.pattern.backgrounds) > 0:
            bg = self.pattern.backgrounds[0].calculate(this_x_array)

        dependents = []

        x, y = cfml_utilities.powder_pattern_from_json(self.model_json)
        return y

        self.additional_data['global_scale'] = scale
        self.additional_data['background'] = bg
        self.additional_data['ivar_run'] = this_x_array
        self.additional_data['ivar'] = x_array
        self.additional_data['components'] = [scale * dep + bg for dep in dependents]
        self.additional_data['phase_names'] = list(self.known_phases.items())
        self.additional_data['type'] = 'powder1DCW'

        dependent_output = scale * np.sum(dependents, axis=0) + bg

        if borg.debug:
            print(f'y_calc: {dependent_output}')
        return (
            np.sum([s['profile'] for s in self.additional_data['phases'].values()], axis=0)
            + self.additional_data['background']
        )

    def get_hkl(self, x_array: np.ndarray = None, idx=0, phase_name=None, encoded_name=False) -> dict:
        # Do we need to re-run a calculation to get the HKL's
        do_run = False
        old_x = self.additional_data.get('ivar', np.array(()))
        if not np.array_equal(old_x, x_array):
            do_run = True
        if do_run and x_array is not None:
            _ = self.calculate(x_array)

        # Collate and return
        # if phase_name is None:
        #    known_phases = list(self.known_phases.values())
        #    phase_name = known_phases[idx]
        # phase_data = self.additional_data.get(phase_name, {})
        # Temp fix to get phase_data
        full_phase_name = self.additional_data['phase_names'][idx]
        phase_data = self.additional_data['phases'].get(full_phase_name)
        return phase_data.get(
            'hkl',
            {
                'ttheta': np.array([]),
                'h': np.array([]),
                'k': np.array([]),
                'l': np.array([]),
            },
        )

    def updateModelCif(self, cif_string: str):
        # Update the model with the cif string
        self.model_cif = cif_string

        doc = gemmi.cif.read_string(cif_string)
        j = doc.as_json()
        j_dict = json.loads(j)
        cfml_dict = self.convert_atom_site_dict_to_crysfml(j_dict)
        self.model_json['phases'] = [cfml_dict]

    def updateExpCif(self, cif_string: str, modelNames: list):
        # Update the experiment with the cif string
        self.experiment_cif = cif_string
        doc = gemmi.cif.read_string(cif_string)
        j = doc.as_json()
        j_dict = json.loads(j)
        exp_name = list(j_dict.keys())[0]
        # add non-loop keys
        j_dict_no_loops = self.exp_non_loops_from_dict(j_dict)

        # add 2theta range_min, range_max, range_inc, offset
        range_dict = self.exp_add_ranges_from_dict(j_dict[exp_name])
        j_dict_no_loops[exp_name].update(range_dict)

        self.model_json['experiments'] = [j_dict_no_loops]
        pass

    def exp_add_ranges_from_dict(self, j_dict):
        """ "
        Extract the 2theta range from a CIF dictionary
        and updates the x_coord attribute
        """
        range_dict = {}
        if '_pd_meas.2theta_scan' in j_dict:
            # this conditional will need to be updated for TOF
            query = '_pd_meas.2theta_scan'
        else:
            query = '_pd_meas_2theta_scan'

        x0 = j_dict[query][0]
        x1 = j_dict[query][-1]
        x_incr = (x1 - x0) / (len(j_dict[query]) - 1)
        self.x_coord = j_dict[query]
        range_dict['_pd_meas_2theta_range_min'] = x0
        range_dict['_pd_meas_2theta_range_max'] = x1
        range_dict['_pd_meas_2theta_range_inc'] = x_incr
        return range_dict

    @staticmethod
    def exp_non_loops_from_dict(j_dict: dict) -> dict:
        """
        Extract the non-loop keys from a CIF dictionary
        :param j_dict: CIF dictionary
        :type j_dict: dict
        :return: dictionary of non-loop keys
        :rtype: dict
        """
        exp_name = list(j_dict.keys())[0]
        j_dict_no_loops = {exp_name: {}}
        for key, value in j_dict[exp_name].items():
            if not isinstance(value, list):
                s_key = key.replace('.', '_')
                if 'calib' in s_key:
                    s_key = s_key.replace('calib', 'meas')
                j_dict_no_loops[exp_name][s_key] = value
        return j_dict_no_loops

    @staticmethod
    def nonPolarized_update(crystal_name, diffraction_pattern, reflection_list, job_info, scales=1):
        dependent = diffraction_pattern.ycalc

        hkltth = np.array([[*reflection_list[i].hkl, reflection_list[i].stl] for i in range(reflection_list.nref)])

        if len(hkltth) > 1:
            hkl_dict = {
                'ttheta': np.rad2deg(np.arcsin(hkltth[:, 3] * job_info.lambdas[0])) * 2,
                'h': hkltth[:, 0],
                'k': hkltth[:, 1],
                'l': hkltth[:, 2],
            }
        else:
            hkl_dict = {
                'ttheta': np.array([]),
                'h': np.array([]),
                'k': np.array([]),
                'l': np.array([]),
            }
        output = {
            crystal_name: {
                'hkl': hkl_dict,
                'profile': scales * dependent,
                'components': {'total': dependent},
                'profile_scale': scales,
            }
        }
        return dependent, output

    def add_phase(self, phase_id, phase_name):
        self.known_phases[phase_id] = phase_name

    def remove_phase(self, phases_id):
        if phases_id in self.known_phases:
            name = self.known_phases.pop(phases_id)
            if name in self.additional_data['phase_names']:
                del self.additional_data['phase_names'][name]
            if name in self.additional_data['phases'].keys():
                del self.additional_data['phases'][name]

    def get_component(self, component_name=None):
        data = None
        if component_name is None:
            data = self.additional_data.copy()
        elif component_name in self.additional_data:
            data = self.additional_data[component_name].copy()
        return data

    def get_phase_components(self, phase_name):
        data = None
        if phase_name in self.additional_data['phase_names']:
            data = self.additional_data['phases'][phase_name].copy()
        return data

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        """
        For a given phase index, return the calculated y
        :param phase_idx: index of the phase
        :type phase_idx: int
        :return: calculated y
        :rtype: np.ndarray
        """
        if phase_idx > len(self.additional_data['components']):
            raise KeyError(f'phase_index incorrect: {phase_idx}')
        return self.additional_data['phases'][self.additional_data['phase_names'][phase_idx]]['profile']

    def get_total_y_for_phases(self) -> Tuple[np.ndarray, np.ndarray]:
        x_values = self.additional_data['ivar_run']
        y_values = (
            np.sum([s['profile'] for s in self.additional_data['phases'].values()], axis=0)
            + self.additional_data['background']
        )
        return x_values, y_values

    def setPhaseScale(self, model_name, scale=1):
        self.storage[str(model_name) + '_scale'] = scale

    def getPhaseScale(self, model_name, *args, **kwargs):
        return self.storage.get(str(model_name) + '_scale', 1)

    @staticmethod
    def convert_atom_site_dict_to_crysfml(gemmi_dict):
        # Initialize cfml_dict
        phase_name = list(gemmi_dict.keys())[0]
        cfml_dict = {phase_name: {'_atom_site': []}}

        # Extract the key from gemmi_dict
        for key, atom_data in gemmi_dict.items():
            cfml_dict[key] = {'_atom_site': []}  # Initialize the _atom_site key

            # Get the list of all atom site keys
            # atom_keys = [k for k in atom_data.keys() if k.startswith("_atom_site_") or k.startswith("_atom_site.")]
            atom_keys = [k for k in atom_data.keys() if k.startswith('_atom_site')]

            # Number of atoms (length of any value list under "_atom_site_XXX")
            num_atoms = 0
            if '_atom_site_label' in atom_data:
                num_atoms = len(atom_data['_atom_site_label'])
            elif '_atom_site.label' in atom_data:
                num_atoms = len(atom_data['_atom_site.label'])

            # Create a list of dictionaries for each atom
            for i in range(num_atoms):
                atom_entry = {}
                for atom_key in atom_keys:
                    new_key = atom_key.replace('.', '_')  # convert potential CIF1 keys
                    new_key = new_key.replace('_atom_site_', '_')  # Transform key
                    if 'b_iso_or_equiv' in new_key:  # case conversion
                        new_key = '_B_iso_or_equiv'
                    atom_entry[new_key] = atom_data[atom_key][i]  # Assign corresponding value
                cfml_dict[key]['_atom_site'].append(atom_entry)

        # iterate over cif_dict and just copy the key-value pairs for
        # entries which do not contain "_atom_site" in the key
        cif_dict = gemmi_dict[phase_name]
        for key, value in cif_dict.items():
            if '_atom_site' not in key:
                key_2 = key.replace('.', '_')  # convert potential CIF1 keys
                if 'space_group_name' in key_2:  # case conversion
                    key_2 = '_space_group_name_H-M_alt'
                cfml_dict[phase_name][key_2] = value

        return cfml_dict
