__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import List

import numpy as np

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
from easyCore.Objects.Inferface import ItemContainer
from easyDiffractionLib.Calculators.cryspy import Cryspy as Cryspy_calc
from easyDiffractionLib.Elements.Experiments.Experiment import Pars1D


class Cryspy(InterfaceTemplate):
    """
    A simple example interface using CFML
    """

    _sample_link = {
        'cif_str': 'cif_str'}

    _crystal_link = {
        "length_a": "length_a",
        "length_b": "length_b",
        "length_c": "length_c",
        "angle_alpha": "angle_alpha",
        "angle_beta": "angle_beta",
        "angle_gamma": "angle_gamma",
    }

    _instrument_link = {
        'resolution_u': 'u',
        'resolution_v': 'v',
        'resolution_w': 'w',
        'resolution_x': 'x',
        'resolution_y': 'y',
        'wavelength': 'wavelength'
    }

    name = 'CrysPy'

    def __init__(self):
        self.calculator = Cryspy_calc()
        self._namespace = {}

    def create(self, model):
        r_list = []
        if issubclass(type(model), Pars1D):
            res_key = self.calculator.createResolution()
            setup_key = self.calculator.createSetup()
            keys = self._instrument_link.copy()
            keys.pop('wavelength')
            r_list.append(
                ItemContainer(res_key, keys,
                              self.calculator.genericReturn,
                              self.calculator.genericUpdate)
            )
            r_list.append(
                ItemContainer(setup_key, {'wavelength': self._instrument_link['wavelength']},
                              self.calculator.genericReturn,
                              self.calculator.genericUpdate)
            )
        else:
            print(f"I'm a: {type(model)}")
        return r_list

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
