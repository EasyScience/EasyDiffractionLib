__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from typing import Union, List

from easyCore import np
from easyCore.Objects.Groups import BaseCollection
from easyCore.Objects.Base import Parameter, Descriptor, BaseObj
from .Background import Background


class BackgroundPoint(BaseObj):
    def __init__(self, x: Descriptor, y: Parameter, name=None):
        if name is None:
            name = '{:.1f}_deg'.format(x.raw_value).replace(".", ",")
        x._callback = property(fget=None,
                               fset=lambda x_value: self._modify_x_label(x_value),
                               fdel=None)
        super(BackgroundPoint, self).__init__(name, x=x, y=y)

    @classmethod
    def from_pars(cls, x: float, y: float):
        x = Descriptor('x', x)
        y = Parameter('intensity', y, fixed=True)
        return cls(x, y)

    @classmethod
    def default(cls):
        return cls.from_pars(0, 0)

    def set(self, value):
        self.y = value

    def _modify_x_label(self, value: float):
        self.name = '{:.1f}_deg'.format(value).replace(".", ",")


class PointBackground(Background):

    def __init__(self, *args, **kwargs):
        super(PointBackground, self).__init__('point_background', *args, **kwargs)

    def calculate(self, x_array: np.ndarray) -> np.ndarray:

        shape_x = x_array.shape
        reduced_x = x_array.flat

        y = np.zeros_like(reduced_x)

        low_x = x_array.flat[0]
        x_points = self.x_points
        low_y = 0
        y_points = self.y_points

        for point, intensity in zip(x_points, y_points):
            idx = (reduced_x >= low_x) & (reduced_x < point)
            if np.any(idx):
                y[idx] = np.interp(reduced_x[idx], [low_x, point], [low_y, intensity])
            low_x = point
            low_y = intensity

        idx = reduced_x > low_x
        y[idx] = low_y
        return y.reshape(shape_x)

    def __repr__(self) -> str:
        return f'Background of {len(self)} points.'

    def __getitem__(self, idx: Union[int, slice]) -> Union[Parameter, Descriptor, BaseObj, 'BaseCollection']:
        return super(PointBackground, self).__getitem__(idx)

    def __delitem__(self, key):
        return super(PointBackground, self).__delitem__(key)

    @property
    def x_points(self):
        x = np.array([item.x.raw_value for item in self])
        x.sort()
        return x

    @property
    def y_points(self):
        idx = np.array([item.x.raw_value for item in self]).argsort()
        y = np.array([item.y.raw_value for item in self])
        return y[idx]

    def append(self, item: BackgroundPoint):
        if not isinstance(item, BackgroundPoint):
            raise TypeError('Item must be a BackgroundPoint')
        if item.x.raw_value in self.x_points:
            raise AttributeError(f'An BackgroundPoint at {item.x.raw_value} already exists.')
        super(PointBackground, self).append(item)

    # def as_dict(self, skip: list = None):
    #     this_dict = super(PointBackground, self).as_dict(skip=skip)
    #     old_data = this_dict['data']
    #     idx = np.array([item.x.raw_value for item in self]).argsort()
    #     new_data = old_data[idx]
    #     this_dict['data'] = new_data
    #     return this_dict

    def get_parameters(self) -> List[Parameter]:
        """"
        Redefine get_parameters so that the returned values are in th correct order
        """
        list_pars = np.array(super(PointBackground, self).get_parameters())
        idx = np.array([item.x.raw_value for item in self]).argsort()
        return list_pars[idx].tolist()
