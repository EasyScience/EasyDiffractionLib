# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from typing import Union

import numpy as np
from easyscience.Datasets.xarray import xr  # type: ignore
from easyscience.fitting.fitter import Fitter as CoreFitter
from easyscience.fitting.minimizers.factory import AvailableMinimizers
from easyscience.Objects.job.analysis import AnalysisBase as coreAnalysis

from easydiffraction.calculators.wrapper_factory import WrapperFactory


class Analysis(coreAnalysis):
    """
    Diffraction-specific Experiment object.
    """

    def __init__(self, name: str, interface=None, *args, **kwargs):
        super(Analysis, self).__init__(name, *args, **kwargs)
        self.name = name
        if interface is None:
            interface = WrapperFactory()
        self.interface = interface
        self._fitter = CoreFitter(self, self.interface.fit_func)

    def calculate_theory(self, x: Union[xr.DataArray, np.ndarray], **kwargs) -> np.ndarray:
        """
        Implementation of the abstract method from JobBase.
        Just a wrapper around the profile calculation.
        """
        return self.calculate_profile(x, **kwargs)

    def calculate_profile(self, x: Union[xr.DataArray, np.ndarray] = None, coord=None, **kwargs) -> np.ndarray:
        """
        Calculate the profile based on current phase.
        """
        x_store, f = coord.EasyScience.fit_prep(
            self.interface.fit_func,
            bdims=xr.broadcast(coord.transpose()),
        )
        y = xr.apply_ufunc(f, *x_store, kwargs=kwargs)
        return y

    def fit(
        self,
        x: Union[xr.DataArray, np.ndarray],
        y: Union[xr.DataArray, np.ndarray],
        e: Union[xr.DataArray, np.ndarray],
        **kwargs,
    ):
        """
        Fit the profile based on current phase and experiment.
        """
        # cursory checks
        if x is None or y is None or e is None:
            return None
        if len(x) != len(y) or len(x) != len(e):
            return None

        self._kwargs = {}
        for kwarg in kwargs:
            self._kwargs[kwarg] = kwargs[kwarg]

        weights = 1 / e
        self._kwargs['weights'] = weights

        # save some kwargs on the interface object for use in the calculator
        self.interface._InterfaceFactoryTemplate__interface_obj.saved_kwargs = self._kwargs
        try:
            if isinstance(x, xr.DataArray):
                x = x.values
            if isinstance(y, xr.DataArray):
                y = y.values
            res = self._fitter.fit(x, y, **kwargs)

        except Exception as ex:
            print(f'Error in fitting: {ex}')
            return None
        return res

    @property
    def available_minimizers(self) -> list:
        """
        Return a list of available minimizers, converted to a list of strings.
        """
        # AvailableMinimizers is an enum. Convert it to a list of strings.
        minimizers = [minimizer.name for minimizer in AvailableMinimizers]
        return minimizers

    @property
    def current_minimizer(self) -> str:
        """
        Return the current minimizer as a string.
        """
        minimizer = self._fitter._enum_current_minimizer.name
        return minimizer

    @current_minimizer.setter
    def current_minimizer(self, minimizer: str):
        """
        Set the current minimizer.
        """
        # Convert the string to an enum
        if minimizer not in AvailableMinimizers.__members__:
            raise ValueError(f'Minimizer {minimizer} not available')
        minimizer = AvailableMinimizers[minimizer]
        self._fitter.switch_minimizer(minimizer)

    @staticmethod
    def from_cif(cif_file: str):
        """
        Load the analysis from a CIF file
        """
        # TODO: Implement this
        return Analysis('Analysis')

    # required dunder methods
    def __str__(self):
        return f'Analysis: {self.name}'
