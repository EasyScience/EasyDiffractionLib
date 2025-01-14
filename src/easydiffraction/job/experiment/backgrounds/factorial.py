# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from typing import List
from typing import Union

import numpy as np
from easyscience.Objects.Groups import BaseCollection
from easyscience.Objects.ObjectClasses import BaseObj
from easyscience.Objects.ObjectClasses import Descriptor
from easyscience.Objects.ObjectClasses import Parameter

from .background import Background


class BackgroundFactor(BaseObj):
    """
    This class describes a polynomial factor. It contains an amplitude and a power. i.e. for x, Ax^p
    """

    def __init__(self, power: Descriptor, amp: Parameter):
        """
        Construct a background factor.

        :param power: Power to which x will be raised.
        :type power: Descriptor
        :param amp: Amplitude for which x will be multiplied by
        :type amp: Parameter
        """
        name = f'Amplitude_{power.value}'
        super(BackgroundFactor, self).__init__(name, power=power, amp=amp)

    @classmethod
    def from_pars(cls, power: int, amp: float):
        """
        Construct a background factor from a power and amplitude as an integer/float respectively.

        :param power: Power to which x will be raised.
        :type power: int
        :param amp: Amplitude for which x will be multiplied by
        :type amp: float
        :return: Constructed background factor
        :rtype: BackgroundFactor
        """
        power = Descriptor('power', power)
        amp = Parameter('amplitude', amp, fixed=True)
        return cls(power, amp)

    @classmethod
    def default(cls):
        """
        Construct a default background factor with amplitude 1 and power 0

        :return: Constructed background factor
        :rtype: BackgroundFactor
        """
        return cls.from_pars(0, 1)

    def set(self, value):
        """
        Convenience function to set the background amplitude.

        :param value: New amplitude value
        :type value: float
        :rtype: None
        """
        self.amp = value


class FactorialBackground(Background):
    """
    Create a background which is constructed from a collection of background factors. Note that the background factors
    are not stored in order!! `sorted_powers` and `sorted_amplitudes` should be used to access these factors in the
    numerical order (based on increasing powers).
    """

    def __init__(self, *args, **kwargs):
        """
        Factorial based background constructor.

        :param args: Background factors to be added to the background (optional)
        :type args: BackgroundFactor
        :param linked_experiment: Which experiment should this background be linked with.
        :type linked_experiment: str
        :param kwargs: Any additional kwargs
        """
        super(FactorialBackground, self).__init__('factorial_background', *args, **kwargs)
        self.__index_contents()

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        Generate a background from the stored background factors.

        :param x_array: Points for which the background should be calculated.
        :type x_array: np.ndarray
        :return: Background points at the supplied x-positions.
        :rtype: np.ndarray
        """

        shape_x = x_array.shape
        reduced_x = x_array.flat

        y = np.zeros_like(reduced_x)

        powers = self.sorted_powers
        amps = self.sorted_amplitudes

        for power, amp in zip(powers, amps):
            y += amp * x_array**power

        return y.reshape(shape_x)

    def __repr__(self) -> str:
        """
        String representation of the background

        :return: String representation of the background
        :rtype: str
        """
        return f'Background of {len(self)} factors.'

    def __getitem__(self, idx: Union[int, slice]) -> Union[Parameter, Descriptor, BaseObj, 'BaseCollection']:
        """
        Return an item from the collection.

        :param idx: index of item to be returned.
        :type idx: int
        :return: item at point `idx`
        :rtype: Union[Parameter, Descriptor, BaseObj, 'BaseCollection']
        """
        return super(FactorialBackground, self).__getitem__(idx)

    def __delitem__(self, idx: int):
        """
        Remove an item from the collection at index `idx`

        :param idx: index of the item to be deleted
        :type idx: int
        """
        removed_applied = super(FactorialBackground, self).__delitem__(idx)
        self.__index_contents()
        return removed_applied

    @property
    def sorted_powers(self) -> np.ndarray:
        """
        Get the stored powers as a sorted array

        :return: Sorted powers
        :rtype: np.ndarray
        """
        return self._sorted_self['power']

    @property
    def sorted_amplitudes(self) -> np.ndarray:
        """
        Get the stored amplitudes based on the sorted powers

        :return: Sorted amplitudes
        :rtype: np.ndarray
        """
        return self._sorted_self['amp']

    @property
    def names(self) -> List[str]:
        """
        Get the names of the factors in the collection.

        :return: Names of the factors in the collection
        :rtype: List[str]
        """
        return [item.name for item in self]

    def append(self, item: BackgroundFactor):
        """
        Add a background factor to the collection.

        :param item: Background factor to be added.
        :type item: BackgroundFactor
        """
        if not isinstance(item, BackgroundFactor):
            raise TypeError('Item must be a BackgroundFactor')
        if item.power.value in self.sorted_powers:
            raise AttributeError(f'A BackgroundFactor with power {item.power.value} already exists.')
        super(FactorialBackground, self).append(item)
        self.__index_contents()

    def get_parameters(self) -> List[Parameter]:
        """ "
        Redefine get_parameters so that the returned values are in the correct order
        """
        list_pars = np.array(super(FactorialBackground, self).get_parameters())
        idx = np.array([item.power.value for item in self]).argsort()
        return list_pars[idx].tolist()

    def __index_contents(self):
        """
        Index the contents
        """
        x = np.array([item.power.value for item in self])
        idx = x.argsort()
        y = np.array([item.amp.value for item in self])
        self._sorted_self = {'idx': idx, 'power': x[idx], 'amp': y[idx]}
