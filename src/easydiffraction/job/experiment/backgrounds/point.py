# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from typing import List
from typing import Union

import numpy as np
from easyscience.Objects.Groups import BaseCollection
from easyscience.Objects.ObjectClasses import BaseObj
from easyscience.Objects.variable import DescriptorNumber as Descriptor
from easyscience.Objects.variable import Parameter

from .background import Background


class BackgroundPoint(BaseObj):
    """
    This class describes a background point. It contains x position and y intensities. Note that the label for x
    varies with it's value!!!
    """

    def __init__(self, x: Union[float, Descriptor] = 0.0, y: Union[float, Parameter] = 0.0, name: str = None):
        """
        Construct a background point from a x-Descriptor any y-parameter.

        :param x: x-position of the background point
        :type x: Descriptor
        :param y: Intensity/y-position of the background point
        :type y: Parameter
        :param name: Override the default naming.
        :type name: str
        """
        if not isinstance(x, Descriptor):
            x = Descriptor('x', x)
        if not isinstance(y, Parameter):
            y = Parameter('intensity', y, fixed=True)
        if name is None:
            name = '{:.1f}_deg'.format(x.value).replace('.', ',')
        x._callback = property(fget=None, fset=lambda x_value: self._modify_x_label(x_value), fdel=None)
        super(BackgroundPoint, self).__init__(name, x=x, y=y)

    def set(self, value: float):
        """
        Convenience function to set the background intensity.

        :param value: New intensity/y-position value
        :type value: float
        :rtype: None
        """
        self.y = value

    def _modify_x_label(self, value: float):
        """
        Auto generate a new label for x which is tied to it's value

        :param value: New x-value
        :type value: float
        :rtype: None
        """
        self.name = '{:.1f}_deg'.format(value).replace('.', ',')

    def __repr__(self) -> str:
        y_str = str(self.y).split(': ')[1][:-1]
        return f"<{self.__class__.__name__} '{self.name}': {y_str}>"


class PointBackground(Background):
    """
    Create a background which is constructed from a collection of background points. Note that the background points
    are not stored in order!! `x_sorted_points` and `y_sorted_points` should be used to access these points in the
    numerical order.
    """

    def __init__(self, *args, linked_experiment: str = None, **kwargs):
        """
        Point based background constructor.

        :param args: Background points to be added to the background (optional)
        :type args: BackgroundPoint
        :param linked_experiment: Which experiment should this background be linked with.
        :type linked_experiment: str
        :param kwargs: Any additional kwargs
        """
        if linked_experiment is None:
            linked_experiment = 'default'
        super(PointBackground, self).__init__('point_background', *args, linked_experiment=linked_experiment, **kwargs)

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        Generate a background from the stored background points.

        :param x_array: Points for which the background should be calculated.
        :type x_array: np.ndarray
        :return: Background points at the supplied x-positions.
        :rtype: np.ndarray
        """

        # shape_x = x_array.shape
        # reduced_x = x_array.flat

        # y = np.zeros_like(reduced_x)

        # low_x = x_array.flat[0] - 1e-10
        x_points = self.x_sorted_points
        if not len(x_points):
            return np.zeros_like(x_array)
        # low_y = 0
        y_points = self.y_sorted_points
        return np.interp(x_array, x_points, y_points)
        #
        # for point, intensity in zip(x_points, y_points):
        #     idx = (reduced_x > low_x) & (reduced_x <= point)
        #     if np.any(idx):
        #         y[idx] = np.interp(reduced_x[idx], [low_x, point], [low_y, intensity])
        #     low_x = point
        #     low_y = intensity
        #
        # idx = reduced_x > low_x
        # y[idx] = low_y
        # return y.reshape(shape_x)

    def __repr__(self) -> str:
        """
        String representation of the background

        :return: String representation of the background
        :rtype: str
        """
        return f'Background of {len(self)} points.'

    def __getitem__(self, idx: Union[int, slice]) -> Union[Parameter, Descriptor, BaseObj, 'BaseCollection']:
        """
        Return an item from the collection.

        :param idx: index of item to be returned.
        :type idx: int
        :return: item at point `idx`
        :rtype: Union[Parameter, Descriptor, BaseObj, 'BaseCollection']
        """
        return super(PointBackground, self).__getitem__(idx)

    def __delitem__(self, idx: int):
        """
        Remove an item from the collection at index `idx`

        :param idx: index of the item to be deleted
        :type idx: int
        """
        return super(PointBackground, self).__delitem__(idx)

    @property
    def x_sorted_points(self) -> np.ndarray:
        """
        Get the stored x-values as a sorted array

        :return: Sorted x-values
        :rtype: np.ndarray
        """
        x = np.array([item.x.value for item in self])
        x.sort()
        return x

    @property
    def y_sorted_points(self) -> np.ndarray:
        """
        Get the stored y-values based on the sorted x-values

        :return: Sorted y-values
        :rtype: np.ndarray
        """
        idx = np.array([item.x.value for item in self]).argsort()
        y = np.array([item.y.value for item in self])
        return y[idx]

    @property
    def names(self) -> List[str]:
        """
        Get the names of the points in the collection.

        :return: Names of the points in the collection
        :rtype: List[str]
        """
        return [item.name for item in self]

    def append(self, item: BackgroundPoint):
        """
        Add a background point to the collection.

        :param item: Background point to be added.
        :type item: BackgroundPoint
        """
        if not isinstance(item, BackgroundPoint):
            raise TypeError('Item must be a BackgroundPoint')
        if item.x.value in self.x_sorted_points:
            raise AttributeError(f'An BackgroundPoint at {item.x.value} already exists.')
        super(PointBackground, self).append(item)

    def get_parameters(self) -> List[Parameter]:
        """ "
        Redefine get_parameters so that the returned values are in the correct order
        """
        list_pars = np.array(super(PointBackground, self).get_parameters())
        idx = np.array([item.x.value for item in self]).argsort()
        return list_pars[idx].tolist()
