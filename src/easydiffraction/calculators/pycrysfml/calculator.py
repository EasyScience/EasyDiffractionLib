# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import os
import re
from typing import Tuple

import CFML_api
import numpy as np
from easyscience import global_object as borg


class Pycrysfml:
    def __init__(self, filename: str = None):
        self.filename = filename
        self.conditions = None
        self.background = None
        self.pattern = None
        self.known_phases = {}
        self.additional_data = {'phases': {}}
        self.storage = {}

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

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        if self.filename is None:
            raise AttributeError

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.value
            offset = self.pattern.zero_shift.value

        this_x_array = x_array + offset

        # Experiment/Instrument/Simulation parameters
        x_min = this_x_array[0]
        x_max = this_x_array[-1]
        num_points = np.prod(x_array.shape)
        x_step = (x_max - x_min) / (num_points - 1)
        bg = np.zeros_like(this_x_array)
        if self.pattern is not None and len(self.pattern.backgrounds) > 0:
            bg = self.pattern.backgrounds[0].calculate(this_x_array)

        dependents = []

        # Sample parameters
        # We assume that the phases items has the same indexing as the knownphases item
        cifs = self.grab_cifs()
        if len(cifs) == 0:
            raise ValueError('No phases found for calculation')

        for idx, file in enumerate(cifs):
            cif_file = CFML_api.CIFFile(file)
            cell = cif_file.cell
            space_group = cif_file.space_group
            atom_list = cif_file.atom_list
            job_info = cif_file.job_info

            job_info.range_2theta = (x_min, x_max)
            job_info.theta_step = x_step
            job_info.u_resolution = self.conditions['u_resolution']
            job_info.v_resolution = self.conditions['v_resolution']
            job_info.w_resolution = self.conditions['w_resolution']
            job_info.x_resolution = self.conditions['x_resolution']
            job_info.y_resolution = self.conditions['y_resolution']
            job_info.lambdas = (self.conditions['lamb'], self.conditions['lamb'])
            job_info.bkg = 0.0
            # Calculations
            try:
                reflection_list = CFML_api.ReflectionList(cell, space_group, True, job_info)
                reflection_list.compute_structure_factors(space_group, atom_list, job_info)
                diffraction_pattern = CFML_api.DiffractionPattern(job_info, reflection_list, cell.reciprocal_cell_vol)
            except Exception:
                for cif in cifs:
                    os.remove(cif)
                raise ArithmeticError

            item = list(self.known_phases.items())[idx]
            key = list(self.known_phases.keys())[idx]
            phase_scale = self.getPhaseScale(key)

            dependent, additional_data = self.nonPolarized_update(
                item, diffraction_pattern, reflection_list, job_info, scales=phase_scale
            )
            dependents.append(dependent)
            self.additional_data['phases'].update(additional_data)
        # This causes issues on windows, so commenting out.
        # Macos/Linux don't seem to need it as well, but leaving just in case.
        # for cif in cifs:
        #     os.remove(cif)
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

    def grab_cifs(self):
        base, file = os.path.split(self.filename)
        ext = file[-3:]
        file = file[:-4]
        files = [base + os.path.sep + f for f in os.listdir(base) if re.match(rf'{file}_[0-9]+.*\.{ext}', f)]
        return files
