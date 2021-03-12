__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import List

import numpy as np

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
from easyDiffractionLib.Calculators.GSASII import GSASII as GSASII_calc


class GSASII(InterfaceTemplate):
    """
    A simple example interface using GSASII
    """

    _sample_link = {
        'filename': 'filename'}

    _instrument_link = {
        'resolution_u': 'u',
        'resolution_v': 'v',
        'resolution_w': 'w',
        'resolution_x': 'x',
        'resolution_y': 'y',
        'wavelength': 'wavelength'
    }

    name = 'GSAS-II'

    def __init__(self):
        self.calculator = GSASII_calc()
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
        if value_label == 'wavelength':
            return self.calculator.conditions.get(value_label, None)
        return self.calculator.conditions['resolution'].get(value_label, None)

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
        if value_label in self._instrument_link.keys():
            value_label = self._instrument_link[value_label]
        if value_label == 'wavelength':
            self.calculator.conditions[value_label] = value
            return
        self.calculator.conditions['resolution'][value_label] = value

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