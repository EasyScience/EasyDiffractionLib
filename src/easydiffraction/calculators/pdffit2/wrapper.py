# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from typing import TYPE_CHECKING
from typing import List

import numpy as np
from diffpy.utils.parsers.loaddata import loadData
from easycrystallography.Components.Lattice import Lattice
from easycrystallography.Components.SpaceGroup import SpaceGroup
from easyscience import global_object as borg
from easyscience.Objects.Inferface import ItemContainer

from easydiffraction.calculators.pdffit2.calculator import Pdffit2 as Pdffit2_calc
from easydiffraction.calculators.wrapper_base import WrapperBase
from easydiffraction.job.experiment.pd_1d import PDFParameters
from easydiffraction.job.experiment.pd_1d import Powder1DParameters
from easydiffraction.job.model.phase import Phases
from easydiffraction.job.model.site import Site

if TYPE_CHECKING:
    pass


class Pdffit2Wrapper(WrapperBase):
    """
    A simple interface using Pdffit2
    """

    _model_link = {'scale': 'scale', 'background': 'bkg', 'resolution': 'dq'}

    name = 'Pdffit2'

    feature_available = {
        'Npdf1DCWunp': True,
        'Npdf1DTOFunp': True,
        'Npdf1DCWpol': True,
    }

    _crystal_link = {
        'length_a': 'length_a',
        'length_b': 'length_b',
        'length_c': 'length_c',
        'angle_alpha': 'angle_alpha',
        'angle_beta': 'angle_beta',
        'angle_gamma': 'angle_gamma',
    }

    _instrument_link = {
        'resolution_u': 'u_resolution',
        'resolution_v': 'v_resolution',
        'resolution_w': 'w_resolution',
        'resolution_x': 'x_resolution',
        'resolution_y': 'y_resolution',
        'wavelength': 'wavelength',
        'qmax': 'qmax',
        'qdamp': 'qdamp',
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

    def __init__(self):
        self.calculator = Pdffit2_calc()
        self._namespace = {}
        self._phase = None

    def reset_storage(self):
        """
        Reset the storage area of the calculator
        """
        self.calculator.reset_storage()

    @staticmethod
    def feature_checker(
        radiation='N',
        exp_type='CW',
        sample_type='powder',
        dimensionality='1D',
        polarization='unp',
        test_str=None,
    ):
        return WrapperBase.features(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            polarization=polarization,
            test_str=test_str,
            FEATURES=Pdffit2Wrapper.feature_available,
        )

    def create(self, model) -> List[ItemContainer]:
        """
        Creation function

        :param model: Object to be created
        :return: Item containers of the objects
        """
        from easydiffraction.job.old_sample.old_sample import Sample

        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)

        if issubclass(t_, PDFParameters):
            self.calculator.conditionsSet(model)
            keys = self._instrument_link.copy()
            r_list.append(
                ItemContainer(
                    model_key,
                    keys,
                    self.get_value,
                    self.updateCif,
                )
            )
        elif issubclass(t_, Lattice):
            keys = self._crystal_link.copy()
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.updateCif))

        elif issubclass(t_, SpaceGroup):
            keys = {'_space_group_HM_name': '_space_group_HM_name'}
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.updateCif))

        elif issubclass(t_, Site):
            keys = self._atom_link.copy()
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.updateCif))

        elif issubclass(t_, Phases):
            self._phase = model
            self.calculator.phases = model

        elif issubclass(t_, Sample):
            self.updateCif()

        elif issubclass(t_, Powder1DParameters):
            self.calculator.pattern = model

        return r_list

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit

        :param x_array: points to be calculated at
        :param model_id: The model id
        :return: calculated points
        """
        return self.calculator.calculate(x_array)

    def get_calculated_y_for_phase(self, phase_id: int):
        pass

    def get_hkl(self, x_array: np.ndarray = None, idx=None, phase_name=None, encoded_name=False):
        pass

    def get_total_y_for_phases(self):
        pass

    def link_atom(self, crystal_obj, atom):
        pass

    def remove_atom(self, crystal_obj, atom):
        pass

    def get_value(self, key, item_key):
        item = borg.map.get_item_by_key(key)
        if item_key in ['Uiso', 'Uani', 'Biso', 'Bani']:
            return getattr(getattr(item, 'adp'), item_key).value
        return getattr(item, item_key).value

    def updateCif(self, *args, **kwargs):
        if self._phase is not None:
            self.calculator.cif_string = str(self._phase.cif)
        pass

    @staticmethod
    def __identify(obj):
        return obj.unique_name


def readGRData(filename):
    """
    Read PDF experimental data from the .gr file.
    This uses `loadData` method from the pdffit2 package.

    :param filename: The filename
    :return: The data as an nx4 array with columns: x, y, dy, dx
    """
    return loadData(filename)
