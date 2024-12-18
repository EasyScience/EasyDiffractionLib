# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

import glob
import os

import numpy as np
from easycrystallography.Components.Lattice import Lattice
from easycrystallography.Components.SpaceGroup import SpaceGroup
from easyscience import global_object as borg
from easyscience.Objects.Inferface import ItemContainer
from easycrystallography.Components.Site import Site as Site_base

from easydiffraction.calculators.pycrysfml.calculator import Pycrysfml
from easydiffraction.calculators.wrapper_base import WrapperBase
from easydiffraction.job.experiment.experiment import Experiment
from easydiffraction.job.experiment.pd_1d import Instrument1DCWParameters
from easydiffraction.job.experiment.pd_1d import Powder1DParameters
from easydiffraction.job.model.phase import Phase
from easydiffraction.job.model.phase import Phases
from easydiffraction.job.model.site import Site


class PycrysfmlWrapper(WrapperBase):
    """
    A simple FILE interface using CrysFML
    """

    _sample_link = {'filename': 'filename'}

    _crystal_link = {
        'length_a': 'length_a',
        'length_b': 'length_b',
        'length_c': 'length_c',
        'angle_alpha': 'angle_alpha',
        'angle_beta': 'angle_beta',
        'angle_gamma': 'angle_gamma',
    }

    _instrument_link = {
        'resolution_u': '_pd_instr_resolution_u',
        'resolution_v': '_pd_instr_resolution_v',
        'resolution_w': '_pd_instr_resolution_w',
        'resolution_x': '_pd_instr_resolution_x',
        'resolution_y': '_pd_instr_resolution_y',
        'wavelength': '_diffrn_radiation_wavelength',
    }

    _atom_link = {
        'label': 'label',
        'specie': 'specie',
        'fract_x': 'fract_x',
        'fract_y': 'fract_y',
        'fract_z': 'fract_z',
        'occupancy': 'occupancy',
        'adp_type': 'adp_type',
        'Uiso': 'Uiso',
        'Biso': 'Biso',
        'Uani': 'Uani',
        'Bani': 'Bani',
    }
    _pattern_link = {'scale': 'scale', 'x_offset': 'x_offset'}

    feature_available = {'Npowder1DCW': True, 'Npowder1DCWunp': True}

    name = 'CrysFML'

    def __init__(self):
        self.calculator = Pycrysfml()
        self._phase = None
        self._filename = None

    @staticmethod
    def feature_checker(
        radiation='N',
        exp_type='CW',
        sample_type='powder',
        dimensionality='1D',
        test_str=None,
    ):
        return WrapperBase.features(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            test_str=test_str,
            FEATURES=PycrysfmlWrapper.feature_available,
        )

    def create(self, model):
        from easydiffraction.job.old_sample.old_sample import Sample

        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Instrument1DCWParameters):
            # These parameters are linked to the Resolution and Setup Pycrysfml objects. Note that we can set the job type!
            self.calculator.createConditions(job_type='N')
            keys = self._instrument_link.copy()
            r_list.append(
                ItemContainer(
                    model_key,
                    keys,
                    self.calculator.conditionsReturn,
                    self.calculator.conditionsUpdate,
                )
            )
        elif issubclass(t_, Powder1DParameters):
            # These parameters do not link directly to Pycrysfml objects.
            self.calculator.pattern = model
        elif issubclass(t_, Lattice):
            keys = self._crystal_link.copy()
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.set_phase_value))
        elif issubclass(t_, SpaceGroup):
            keys = {'_space_group_HM_name': '_space_group_HM_name'}
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.set_phase_value))
        elif issubclass(t_, Site) or issubclass(t_, Site_base):
            keys = self._atom_link.copy()
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.set_phase_value))
        elif issubclass(t_, Phases):
            self._phase = model
        elif issubclass(t_, Phase):
            r_list.append(
                ItemContainer(
                    model_key,
                    {'scale': 'scale'},
                    self.calculator.getPhaseScale,
                    self.calculator.setPhaseScale,
                )
            )
            self.calculator.add_phase(str(model_key), model.cif)
        elif issubclass(t_, Experiment):
            self.__createExpModel(model)
        # elif issubclass(t_, Sample):
        #    self.__createSampleModel(model)
        elif t_.__name__ in ['Powder1DCW', 'powder1DCW', 'Npowder1DCW', 'Npowder1DCWunp']:
            self.__createModel(model)
        # need to add handling for Background
        # need to add handling for ...
        return r_list

    def link_atom(self, crystal_obj, atom):
        pass

    def remove_atom(self, crystal_obj, atom):
        pass

    def add_phase(self, phases_obj, phase_obj):
        ident = str(self.__identify(phase_obj))
        self.calculator.add_phase(ident, phase_obj.cif)

    def remove_phase(self, phases_obj, phase_obj):
        ident = str(self.__identify(phase_obj))
        self.calculator.remove_phase(ident)

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit
        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        return self.calculator.calculate(x_array)

    def get_hkl(self, x_array: np.ndarray = None, idx=None, phase_name=None, encoded_name=False) -> dict:
        return self.calculator.get_hkl(x_array)

    def set_phase_value(self, *args, **kwargs):
        if self._phase is None:
            phase_name = None
        else:
            phase_name = self._phase[0].name
        self.calculator.setPhaseValue(phase_name, *args, **kwargs)

    def dump_cif(self, *args, **kwargs):
        if self._filename is None:
            return
        # delete preexising cif files
        self.remove_cif()
        # naive and silly workaround for something mysterious happening in easyCrystallography
        content = str(self._phase.cif)
        content = content.replace('H-M_ref', 'H-M_alt')
        with open(self._filename, 'w') as fid:
            # fid.write(str(self._phase.cif))
            fid.write(content)
        base, file = os.path.split(self._filename)
        ext = file[-3:]
        file = file[:-4]
        for idx, phase in enumerate(self._phase):
            content = str(phase.cif)
            content = content.replace('H-M_ref', 'H-M_alt')
            with open(f'{os.path.join(base, file)}_{idx}.{ext}', 'w') as fid:
                # fid.write(str(phase.cif))
                fid.write(content)

    def remove_cif(self):
        if self._filename is None:
            return
        base, file = os.path.split(self._filename)
        ext = file[-3:]
        file = file[:-4]
        file_wildcarded = os.path.join(base, file) + '_*.' + ext
        fileList = glob.glob(file_wildcarded)
        for f in fileList:
            try:
                os.remove(f)
            except OSError:
                pass

    def updateModelCif(self, cif_string: str) -> None:
        self.calculator.updateModelCif(cif_string)

    def updateExpCif(self, edCif, modelNames):
        self.calculator.updateExpCif(edCif, modelNames)

    def __createSampleModel(self, model):
        self.updateModelCif(model.cif)

    def __createExpModel(self, model):
        self.updateExpCif(model.cif_string, [model.name])

    def get_value(self, key, item_key):
        item = borg.map.get_item_by_key(key)
        if item_key in ['Uiso', 'Uani', 'Biso', 'Bani']:
            return getattr(getattr(item, 'adp'), item_key).raw_value
        return getattr(item, item_key).raw_value

    def get_phase_components(self, phase_name):
        return None

    def get_component(self, component_name):
        return self.calculator.get_component(component_name)

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        return self.calculator.get_calculated_y_for_phase(phase_idx)

    def get_total_y_for_phases(self) -> list:
        return self.calculator.get_total_y_for_phases()

    @staticmethod
    def __identify(obj):
        return obj.unique_name
