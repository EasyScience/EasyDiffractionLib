__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from abc import abstractmethod
from typing import Union, List

from easyCore.Objects.Base import Descriptor, Parameter
from easyCore.Objects.Groups import BaseCollection
from easyCore import np


class Background(BaseCollection):

    def __init__(self, *args, linked_experiment=None, **kwargs):
        if linked_experiment is None:
            raise AttributeError
        elif isinstance(linked_experiment, str):
            linked_experiment = Descriptor('linked_experiment', linked_experiment)

        if not isinstance(linked_experiment, Descriptor):
            raise ValueError

        super(Background, self).__init__(*args, **kwargs)
        self._linked_experiment = linked_experiment

    @property
    def linked_experiment(self):
        return self._linked_experiment

    @linked_experiment.setter
    def linked_experiment(self, value: str):
        self.linked_experiment = value

    @abstractmethod
    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        pass


class BackgroundContainer(BaseCollection):
    def __init__(self, *args, interface=None, **kwargs):
        super(BackgroundContainer, self).__init__('Backgrounds', *args, **kwargs)
        self.interface = interface

    @property
    def linked_experiments(self) -> List[str]:
        return [item.linked_experiment.raw_value for item in self]

    def __repr__(self) -> str:
        return f'Collection of {len(self)} backgrounds.'

    def __getitem__(self, idx: Union[int, slice]):
        if isinstance(idx, str) and idx in self.linked_experiments:
            idx = self.linked_experiments.index(idx)
        return super(BackgroundContainer, self).__getitem__(idx)

    def __delitem__(self, key):
        if isinstance(key, str) and key in self.linked_experiments:
            key = self.linked_experiments.index(key)
        return super(BackgroundContainer, self).__delitem__(key)

    def append(self, item):
        if item.linked_experiment in self.linked_experiments:
            raise AttributeError(f'A background exists for experiment: {item.linked_experiment}')
        super(BackgroundContainer, self).append(item)
