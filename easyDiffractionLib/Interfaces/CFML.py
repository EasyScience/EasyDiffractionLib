__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import List

import numpy as np

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
from easyDiffractionLib.Calculators.CFML import CFML as CFML_calc


class CFML(InterfaceTemplate):
    """
    A simple example interface using CFML
    """

    _sample_link = {
        'filename': 'filename'}

    _instrument_link = {
        'resolution_u': 'u_resolution',
        'resolution_v': 'v_resolution',
        'resolution_w': 'w_resolution',
        'resolution_x': 'x_resolution',
        'resolution_y': 'lorentzian_size',
        'wavelength': 'lamb'
    }

    _pattern_link = {
        'scale': 'scale',
        'x_offset': 'x_offset'
    }

    name = 'CrysFML'

    def __init__(self):
        self.calculator = CFML_calc()
        self._namespace = {}

    def get_value(self, value_label: str) -> float:
        """
        Method to get a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :return: associated value
        :rtype: float
        """
        if value_label in self._sample_link.keys():
            value_label = self._sample_link[value_label]
        return getattr(self.calculator, value_label, None)

    def set_value(self, value_label: str, value: float):
        """
        Method to set a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :param value: new numeric value
        :type value: float
        :return: None
        :rtype: noneType
        """
        if self._borg.debug:
            print(f'Interface1: Value of {value_label} set to {value}')
        if value_label in self._sample_link.keys():
            value_label = self._sample_link[value_label]
        setattr(self.calculator, value_label, value)

    def get_instrument_value(self, value_label: str) -> float:
        """
        Method to get a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :return: associated value
        :rtype: float
        """
        if value_label in self._instrument_link.keys():
            value_label = self._instrument_link[value_label]
        value = getattr(self.calculator.conditions, value_label, None)
        if value_label == self._instrument_link['resolution_y']:
            value = self.lorentzian_size_to_resolution_y(value)
        return value

    def set_instrument_value(self, value_label: str, value: float):
        """
        Method to set a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :param value: new numeric value
        :type value: float
        :return: None
        :rtype: noneType
        """
        if self._borg.debug:
            print(f'Interface1: Value of {value_label} set to {value}')
        if value_label == 'resolution_y':
            value = self.lorentzian_size_to_resolution_y(value)
        if value_label in self._instrument_link.keys():
            value_label = self._instrument_link[value_label]
        setattr(self.calculator.conditions, value_label, value)

    def get_background_value(self, background, value_label: int) -> float:
        """
        Method to get a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :return: associated value
        :rtype: float
        """
        self.calculator.background = background
        # if value_label <= len(self.calculator.background):
        #     return self.calculator.background[value_label]
        # else:
        #     raise IndexError

    def set_background_value(self, background, value_label: int, value: float):
        """
        Method to set a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :param value: new numeric value
        :type value: float
        :return: None
        :rtype: noneType
        """
        self.calculator.background = background
        # if value_label <= len(self.calculator.background):
        #     self.calculator.background[value_label].set(value)
        # else:
        #     raise IndexError

    def set_pattern_value(self, pattern, value_label: int, value: float):
        """
        Method to set a value from the calculator
        :param value_label: parameter name to get
        :type value_label: str
        :param value: new numeric value
        :type value: float
        :return: None
        :rtype: noneType
        """
        self.calculator.pattern = pattern

    def bulk_update(self, value_label_list: List[str], value_list: List[float], external: bool):
        """
        Perform an update of multiple values at once to save time on expensive updates

        :param value_label_list: list of parameters to set
        :type value_label_list: List[str]
        :param value_list: list of new numeric values
        :type value_list: List[float]
        :param external: should we lookup a name conversion to internal labeling?
        :type external: bool
        :return: None
        :rtype: noneType
        """
        for label, value in zip(value_label_list, value_list):
            # This is a simple case so we will serially update
            if label in self._sample_link:
                self.set_value(label, value)
            elif label in self._instrument_link:
                self.set_instrument_value(label, value)

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit
        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        return self.calculator.calculate(x_array)

    def get_hkl(self, x_array: np.ndarray = None) -> dict:
        return self.calculator.get_hkl(x_array)

    def lorentzian_size_to_resolution_y(self, value):
        # convert CrysFML lorentzian_size to resolution_y (CrysPy y_resolution)
        if value < 0.0001:
            value = 0.0001
        value = 100.0 / value
        return value
