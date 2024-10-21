# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

import numpy as np
from easyscience import global_object as borg
from easyscience.Objects.Inferface import ItemContainer

from easydiffraction import Lattice
from easydiffraction import Phases
from easydiffraction import Site
from easydiffraction import SpaceGroup
from easydiffraction.Profiles.P1D import Instrument1DCWParameters
from easydiffraction.Profiles.P1D import Powder1DParameters

from ..calculators.GSASII import GSASII as GSAS_calc
from ..Interfaces.interfaceTemplate import InterfaceTemplate


class GSASII(InterfaceTemplate):
    """
    A simple FILE interface using GSASII
    """

    _sample_link = {
        'filename': 'filename'}

    _crystal_link = {
        "length_a": "length_a",
        "length_b": "length_b",
        "length_c": "length_c",
        "angle_alpha": "angle_alpha",
        "angle_beta": "angle_beta",
        "angle_gamma": "angle_gamma",
    }

    _instrument_link = {
        'resolution_u': 'u_resolution',
        'resolution_v': 'v_resolution',
        'resolution_w': 'w_resolution',
        'resolution_x': 'x_resolution',
        'resolution_y': 'y_resolution',
        'wavelength': 'wavelength'
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
       'Bani': 'Bani'
    }
    _pattern_link = {
        'scale': 'scale',
        'x_offset': 'x_offset'
    }

    feature_available = {
        'Npowder1DCW': True,
        'Npowder1DCWunp': True
    }

    name = 'GSASII'

    def __init__(self):
        self.calculator = GSAS_calc()
        self._phase = None
        self._filename = None

    @staticmethod
    def feature_checker(radiation='N', exp_type='CW', sample_type='powder', dimensionality='1D', test_str=None):
        return InterfaceTemplate.features(radiation=radiation, exp_type=exp_type, sample_type=sample_type,
                                          dimensionality=dimensionality, test_str=test_str,
                                          FEATURES=GSASII.feature_available)

    def create(self, model):
        from easydiffraction.sample import Sample
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Instrument1DCWParameters):
            # These parameters are linked to the Resolution and Setup CFML objects. Note that we can set the job type!
            self.calculator.createConditions(job_type='N')
            keys = self._instrument_link.copy()
            r_list.append(
                ItemContainer(model_key, keys,
                              self.calculator.conditionsReturn,
                              self.calculator.conditionsUpdate)
            )
        elif issubclass(t_, Powder1DParameters):
            # These parameters do not link directly to CFML objects.
            self.calculator.pattern = model
        elif issubclass(t_, Lattice):
            keys = self._crystal_link.copy()
            r_list.append(
                ItemContainer(model_key, keys,
                              self.get_value,
                              self.dump_cif)
            )
        elif issubclass(t_, SpaceGroup):
            keys = {'_space_group_HM_name': '_space_group_HM_name'}
            r_list.append(
                ItemContainer(model_key, keys,
                              self.get_value,
                              self.dump_cif)
            )
        elif issubclass(t_, Site):
            keys = self._atom_link.copy()
            r_list.append(ItemContainer(model_key, keys,
                                        self.get_value,
                                        self.dump_cif))
        elif issubclass(t_, Phases):
            self._phase = model
        elif t_.__name__ in ['Powder1DCW', 'powder1DCW', 'Npowder1DCW', 'Npowder1DCWunp']:
            #TODO Check to see if parameters and pattern should be initialized here.
            self.__createModel(model)
        elif issubclass(t_, Sample):
            self.__createModel(model)

        return r_list

    def link_atom(self, crystal_obj, atom):
        pass

    def remove_atom(self, crystal_obj, atom):
        pass

    def add_phase(self, phases_obj, phase_obj):
        pass

    def remove_phase(self, phases_obj, phase_obj):
        pass

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

    def dump_cif(self, *args, **kwargs):
        if self._filename is None:
            return
        with open(self._filename, 'w') as fid:
            fid.write(str(self._phase.cif))

    def get_value(self, key, item_key):
        item = borg.map.get_item_by_key(key)
        if item_key in ['Uiso', 'Uani', 'Biso', 'Bani']:
            return getattr(getattr(item, 'adp'), item_key).raw_value
        return getattr(item, item_key).raw_value

    def __createModel(self, model):
        self._filename = model.filename
        self.calculator.filename = model.filename
        self.dump_cif()

    def get_phase_components(self, phase_name):
        return None

    def get_component(self, component_name):
        return None

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        return self.calculator.get_calculated_y_for_phase(phase_idx)

    def get_total_y_for_phases(self) -> list:
        return self.calculator.get_total_y_for_phases()

    @staticmethod
    def __identify(obj):
        return borg.map.convert_id_to_key(obj)
