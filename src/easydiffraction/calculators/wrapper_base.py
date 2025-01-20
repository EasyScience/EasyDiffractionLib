# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from abc import ABCMeta
from abc import abstractmethod
from typing import Tuple

import numpy as np
from easyscience import global_object as borg
from easyscience.Objects.core import ComponentSerializer

exp_type_strings = {
    'radiation_options': ['N', 'X'],
    'exp_type_options': ['CW', 'TOF'],
    'dimensional_options': ['1D', '2D'],
    'sample_options': ['powder', 'single'],
    'polarization_options': ['unp', 'pol'],
}


class WrapperBase(ComponentSerializer, metaclass=ABCMeta):
    """
    This class is a template and defines all properties that an interface should have.
    """

    _interfaces = []
    _borg = borg
    _link = {}

    @staticmethod
    def features(
        radiation='N',
        exp_type='CW',
        sample_type='powder',
        dimensionality='1D',
        polarization='unp',
        test_str=None,
        FEATURES=None,
    ):
        if FEATURES is None:
            raise AttributeError
        feature_dict = WrapperBase._feature_generator(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            polarization=polarization,
        )

        for key in FEATURES.keys():
            feature_dict[key] = FEATURES[key]
        if test_str is None:
            test_str = radiation + sample_type + dimensionality + exp_type

        return feature_dict[test_str]

    @staticmethod
    def _feature_generator(radiation='N', exp_type='CW', sample_type='powder', dimensionality='1D', polarization='unp'):
        radiation_options = exp_type_strings['radiation_options']
        if radiation not in radiation_options:
            raise AttributeError(f'"{radiation}" is not supported, only: {radiation_options}')
        exp_type_options = exp_type_strings['exp_type_options']
        if exp_type not in exp_type_options:
            raise AttributeError(f'"{exp_type}" is not supported, only: {exp_type_options}')
        dimensional_options = exp_type_strings['dimensional_options']
        if dimensionality not in dimensional_options:
            raise AttributeError(f'"{dimensionality}" is not supported, only: {dimensional_options}')
        sample_options = exp_type_strings['sample_options']
        if sample_type not in sample_options:
            raise AttributeError(f'"{sample_type}" is not supported, only: {sample_options}')
        polarization_options = exp_type_strings['polarization_options']
        if polarization not in polarization_options:
            raise AttributeError(f'"{polarization}" is not supported, only: {polarization_options}')

        features = [
            ''.join(item)
            for item in np.array(
                np.meshgrid(radiation_options, sample_options, dimensional_options, exp_type_options, polarization_options)
            )
            .T.reshape(-1, len(exp_type_strings))
            .tolist()
        ]
        feature_dict = dict.fromkeys(features, False)
        return feature_dict

    def __init_subclass__(cls, is_abstract: bool = False, **kwargs):
        """
        Initialise all subclasses so that they can be created in the factory

        :param is_abstract: Is this a subclass which shouldn't be dded
        :type is_abstract: bool
        :param kwargs: key word arguments
        :type kwargs: dict
        :return: None
        :rtype: noneType
        """
        super().__init_subclass__(**kwargs)
        if not is_abstract:
            cls._interfaces.append(cls)

    @abstractmethod
    def create(self, model) -> Tuple[str, dict]:
        """
        Method to create an object in the calculator workspace and return it's ID.
        This ID will be used in the implicit get/set for properties.

        :param model:
        :type model:
        :return:
        :rtype:
        """

    @abstractmethod
    def link_atom(self, model_name: str, atom):
        """
        This links an atom to a model

        :param model_name: Name of Phase
        :type model_name: str
        :param atom: Site object
        :type atom: Atom
        :return:
        :rtype:
        """

    @abstractmethod
    def remove_atom(self, model_name: str, atom: str):
        """
        This links an atom to a model

        :param model_name: Name of Phase
        :type model_name: str
        :param atom: Site object
        :type atom: Atom
        :return:
        :rtype:
        """

    @abstractmethod
    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit

        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        pass

    @abstractmethod
    def get_hkl(self, x_array: np.ndarray = None, idx=None) -> dict:
        pass

    @abstractmethod
    def get_calculated_y_for_phase(self, idx=None) -> list:
        pass

    @abstractmethod
    def get_total_y_for_phases(self) -> list:
        pass

    @abstractmethod
    def is_tof(self) -> bool:
        pass

    @staticmethod
    def _get_constructor(known_components, sample_object):
        all_bases = set([base for base in sample_object.__class__.__bases__ if hasattr(base, '_internal_type')])
        if len(all_bases) == 0:
            return None
        all_components = [
            set([base for base in component.__mro__ if hasattr(base, '_internal_type')]) for component in known_components
        ]
        for idx, component in enumerate(all_components):
            test = all_bases - component
            if len(test) == 0:
                return known_components[idx]
