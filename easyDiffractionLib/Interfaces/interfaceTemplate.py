__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from abc import ABCMeta, abstractmethod
from typing import Tuple, List
from easyCore import np, borg
from easyCore.Utils.json import MSONable

exp_type_strings = {
    'radiation_options':   ['N', 'X'],
    'exp_type_options':    ['CW', 'TOF'],
    'dimensional_options': ['1D', '2D'],
    'sample_options':      ['powder', 'single']
}


class InterfaceTemplate(MSONable, metaclass=ABCMeta):
    """
    This class is a template and defines all properties that an interface should have.
    """
    _interfaces = []
    _borg = borg
    _link = {}

    @staticmethod
    def features(radiation='N', exp_type='CW', sample_type='powder', dimensionality='1D', test_str=None, FEATURES=None):

        if FEATURES is None:
            raise AttributeError
        feature_dict = InterfaceTemplate._feature_generator(radiation=radiation, exp_type=exp_type,
                                                            sample_type=sample_type, dimensionality=dimensionality)

        for key in FEATURES.keys():
            feature_dict[key] = FEATURES[key]
        if test_str is None:
            test_str = radiation + sample_type + dimensionality + exp_type

        return feature_dict[test_str]

    @staticmethod
    def _feature_generator(radiation='N', exp_type='CW', sample_type='powder', dimensionality='1D'):
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

        features = [''.join(item) for item in np.array(np.meshgrid(radiation_options,
                                                                   sample_options,
                                                                   dimensional_options,
                                                                   exp_type_options)).T.reshape(-1,
                                                                                                len(exp_type_strings)).tolist()]
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
    def get_hkl(self, x_array: np.ndarray = None) -> dict:
        pass
        