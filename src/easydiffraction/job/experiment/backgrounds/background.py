# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from abc import abstractmethod
from typing import List
from typing import Union

import numpy as np
from easyscience.Objects.Groups import BaseCollection
from easyscience.Objects.variable import DescriptorStr as Descriptor


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
            raise AttributeError(
                'Backgrounds need to be associated with an experiment. Use the `linked_experiment` key word argument.'
            )
        elif isinstance(linked_experiment, str):
            linked_experiment = Descriptor('linked_experiment', linked_experiment)

        if not isinstance(linked_experiment, Descriptor):
            raise ValueError('The `linked_experiment` key word argument must be a string or Descriptor')

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
            raise ValueError('The `linked_experiment` key word argument must be a string or Descriptor')

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

    def _modify_dict(self, skip: list = None) -> dict:
        d = {}
        d['linked_experiment'] = self._linked_experiment.value
        return d


class BackgroundContainer(BaseCollection):
    """
    Background container which will hold all the backgrounds for a given instance. Backgrounds can be of
    any type and have to be associated to an experiment. There can't be multiple backgrounds associated with an
    experiment!!
    """

    def __init__(self, *args, interface=None, **kwargs):
        """
        Constructor, with a link to an interface.
        """
        # Remove the data key word argument if it is empty
        # This can happen if the object is created from a json file with no background points
        if 'data' in kwargs and not kwargs['data']:
            kwargs.pop('data')
        super(BackgroundContainer, self).__init__('background', *args, **kwargs)
        self.interface = interface

    @property
    def linked_experiments(self) -> List[str]:
        """
        Get a list of experiments for which items are linked.

        :return:
        :rtype:
        """
        return [item.linked_experiment.value for item in self]

    def __repr__(self) -> str:
        """
        Simple representation of the object

        :return: Simple representation of the object
        :rtype: str
        """
        return f'Collection of {len(self)} backgrounds.'

    def __getitem__(self, idx: Union[int, slice, str]):
        """
        Obtain an item in the list from either it's integer position or a slice object.

        :param idx: Which item to retrieve
        :type idx: int
        :return: Background object
        :rtype: Background
        """
        if isinstance(idx, str) and idx in self.linked_experiments:
            idx = self.linked_experiments.index(idx)
        return super(BackgroundContainer, self).__getitem__(idx)

    def __delitem__(self, key: Union[int, str]):
        """
        Remove a background from the list. Key can be an index or experiment name

        :param key: Unique identifier of key to be removed
        :type key: int, str
        :return: None
        """
        if isinstance(key, str) and key in self.linked_experiments:
            key = self.linked_experiments.index(key)
        super(BackgroundContainer, self).__delitem__(key)

    def __setitem__(self, pos: int, item):
        # Remove the reference
        self._global_object.map.prune_vertex_from_edge(self, self[pos])
        # Add the new reference
        self._global_object.map.add_edge(self, item)
        # Get all items, go through and change the item at index pos to the new one
        keys = self._kwargs.keys()
        items = {}
        for idx, key in enumerate(keys):
            if idx == pos:
                items[item.unique_name] = item
            else:
                items[key] = self._kwargs[key]
        # Set the new dict
        self._kwargs = items

    def append(self, item):
        """
        Add an element to the list

        :param item: Background element
        :type item: Background
        """
        if item.linked_experiment in self.linked_experiments:
            raise AttributeError(f'A background exists for experiment: {item.linked_experiment}')
        super(BackgroundContainer, self).append(item)
