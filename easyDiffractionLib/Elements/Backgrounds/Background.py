__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from abc import abstractmethod
from typing import Union, List

from easyCore import np
from easyCore.Objects.Base import Descriptor
from easyCore.Objects.Groups import BaseCollection


class Background(BaseCollection):
    """
    Background is a base class for which different types of backgrounds can be built. It functions as
    a pseudo list of elements which can be used to generate a background using the abstract `calculate`
    method. i.e. contents could be points in a point based background or polynomials in a curve background.
    """

    def __init__(self, *args, linked_experiment=None, **kwargs):
        """
        Initialisation routine called from super(). Each background has to be linked with an experiment

        :param args: Optional elements which are making up the background
        :param linked_experiment: which experiment this background should be linked to
        :type linked_experiment: str
        :param kwargs: For serialisation
        """

        #  Convert `linked_experiment` to a Descriptor
        if linked_experiment is None:
            raise AttributeError
        elif isinstance(linked_experiment, str):
            linked_experiment = Descriptor('linked_experiment', linked_experiment)

        if not isinstance(linked_experiment, Descriptor):
            raise ValueError

        #  Initialise
        super(Background, self).__init__(*args, **kwargs)
        self._linked_experiment = linked_experiment

    @property
    def linked_experiment(self) -> Descriptor:
        """
        Get the experiment which the background is linked to
        :return: linked experiment name
        :rtype: Descriptor
        """
        return self._linked_experiment

    @linked_experiment.setter
    def linked_experiment(self, value: Union[str, Descriptor]):
        """
        Set the value of the linked experiment
        :param value: THe name of the experiment to be linked to
        :type value: str
        :return: None
        """
        if isinstance(value, str):
            self.linked_experiment = value
        elif isinstance(value, Descriptor):
            self._linked_experiment = value
        else:
            raise ValueError

    @abstractmethod
    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        Abstract method to actually calculate the background.

        :param x_array: values to be calculated at
        :type x_array: np.ndarray
        :return: y-values of the calculated background
        :rtype: np.ndarray
        """
        pass


class BackgroundContainer(BaseCollection):
    """
    Background container which will hold all the backgrounds for a given instance. Backgrounds can be of
    any type and
    """
    def __init__(self, *args, interface=None, **kwargs):
        super(BackgroundContainer, self).__init__('Instrument', *args, **kwargs)
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
