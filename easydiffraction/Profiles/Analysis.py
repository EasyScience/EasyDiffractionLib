#  SPDX-FileCopyrightText: 2024 easyDiffraction contributors  <support@easydiffraction.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2024 Contributors to the easydiffraction project <https://github.com/easyScience/easydiffraction


from typing import Union

import numpy as np
from easyscience.Datasets.xarray import xr  # type: ignore
from easyscience.Fitting.Fitting import Fitter as CoreFitter
from easyscience.Objects.Job.Analysis import AnalysisBase as coreAnalysis

from easydiffraction.interface import InterfaceFactory


class Analysis(coreAnalysis):
    """
    Diffraction-specific Experiment object.
    """
    def __init__(self, name: str, interface=None, *args, **kwargs):
        super(Analysis, self).__init__(name, *args, **kwargs)
        self.name = name
        if interface is None:
            interface = InterfaceFactory()
        self.interface = interface
        self._fitter = CoreFitter(self, self.interface.fit_func)

    def calculate_theory(self, x: Union[xr.DataArray, np.ndarray], **kwargs) -> np.ndarray:
        '''
        Implementation of the abstract method from JobBase.
        Just a wrapper around the profile calculation.
        '''
        return self.calculate_profile(x, **kwargs)

    def calculate_profile(self, x: Union[xr.DataArray, np.ndarray] = None, coord=None, **kwargs) -> np.ndarray:
        '''
        Calculate the profile based on current phase.
        '''
        x_store, f = coord.EasyScience.fit_prep(
            self.interface.fit_func,
            bdims=xr.broadcast(coord.transpose()),
        )
        y = xr.apply_ufunc(f, *x_store, kwargs=kwargs)
        return y

    def fit(self, x: Union[xr.DataArray, np.ndarray],
                  y: Union[xr.DataArray, np.ndarray],
                  e: Union[xr.DataArray, np.ndarray],
                  **kwargs):
        '''
        Fit the profile based on current phase and experiment.
        '''
        # cursory checks
        if x is None or y is None or e is None:
            return None
        if len(x) != len(y) or len(x) != len(e):
            return None

        self._kwargs = {}
        for kwarg in kwargs:
            self._kwargs[kwarg] = kwargs[kwarg]

        method = self._fitter.available_methods()[0]

        weights = 1 / e

        kwargs = {
            'weights': weights,
            'method': method
        }

        local_kwargs = {}
        if method == 'least_squares':
            kwargs['minimizer_kwargs'] = {'diff_step': 1e-5}

        # save some kwargs on the interface object for use in the calculator
        self.interface._InterfaceFactoryTemplate__interface_obj.saved_kwargs = local_kwargs
        try:
            if isinstance(x, xr.DataArray):
                x = x.values
            if isinstance(y, xr.DataArray):
                y = y.values
            res = self._fitter.fit(x, y, **kwargs)

        except Exception:
            return None
        return res

    @staticmethod
    def from_cif(cif_file: str):
        """
        Load the analysis from a CIF file
        """
        # TODO: Implement this
        return Analysis("Analysis")

    # required dunder methods
    def __str__(self):
        return f"Analysis: {self.name}"
    
    