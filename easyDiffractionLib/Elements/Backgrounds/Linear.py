__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from .Background import Background
from typing import Union, List

from easyCore import np
from easyCore.Objects.Groups import BaseCollection
from easyCore.Objects.Base import Parameter, Descriptor, BaseObj


class BackgroundFactor(BaseObj):
    def __init__(self, power: Descriptor, amp: Parameter):
        name = f'Amplitude_{power.raw_value}'
        super(BackgroundFactor, self).__init__(name, power=power, amp=amp)

    @classmethod
    def from_pars(cls, power: float, amp: float):
        power = Descriptor('power', power)
        amp = Parameter('amplitude', amp, fixed=True)
        return cls(power, amp)

    @classmethod
    def default(cls):
        return cls.from_pars(0, 1)

    def set(self, value):
        self.amp = value


class FactorialBackground(Background):

    def __init__(self, *args, **kwargs):
        super(FactorialBackground, self).__init__('factorial_background', *args, **kwargs)

    def calculate(self, x_array: np.ndarray) -> np.ndarray:

        shape_x = x_array.shape
        reduced_x = x_array.flat

        y = np.zeros_like(reduced_x)

        powers = self.sorted_powers
        amps = self.sorted_amplitudes

        for power, amp in zip(powers, amps):
            y += amp*x_array**power

        return y.reshape(shape_x)

    def __repr__(self) -> str:
        return f'Background of {len(self)} points.'

    def __getitem__(self, idx: Union[int, slice]) -> Union[Parameter, Descriptor, BaseObj, 'BaseCollection']:
        return super(FactorialBackground, self).__getitem__(idx)

    def __delitem__(self, key):
        return super(FactorialBackground, self).__delitem__(key)

    @property
    def sorted_powers(self):
        x = np.array([item.power.raw_value for item in self])
        x.sort()
        return x

    @property
    def sorted_amplitudes(self):
        idx = np.array([item.power.raw_value for item in self]).argsort()
        y = np.array([item.amp.raw_value for item in self])
        return y[idx]

    @property
    def names(self):
        return [item.name for item in self]

    def append(self, item: BackgroundFactor):
        if not isinstance(item, BackgroundFactor):
            raise TypeError('Item must be a BackgroundFactor')
        if item.power.raw_value in self.sorted_powers:
            raise AttributeError(f'A BackgroundFactor with power {item.power.raw_value} already exists.')
        super(FactorialBackground, self).append(item)

    def get_parameters(self) -> List[Parameter]:
        """"
        Redefine get_parameters so that the returned values are in the correct order
        """
        list_pars = np.array(super(FactorialBackground, self).get_parameters())
        idx = np.array([item.power.raw_value for item in self]).argsort()
        return list_pars[idx].tolist()
