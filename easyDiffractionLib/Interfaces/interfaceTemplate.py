__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import numpy as np
from abc import ABCMeta, abstractmethod

from easyCore import borg
from easyCore.Utils.json import MSONable


class InterfaceTemplate(MSONable, metaclass=ABCMeta):
    """
    This class is a template and defines all properties that an interface should have.
    """
    _interfaces = []
    _borg = borg
    _link = {}

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
    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit

        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        pass
