# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

if TYPE_CHECKING:
    from easyscience.Objects.Inferface import B
    from easyscience.Objects.Inferface import ItemContainer


class _Type:
    _internal_type = True
    calculator: Any
    _identify: Callable[[Any], Union[str, int]]

    @abstractmethod
    def create(self, model: B) -> List[ItemContainer]:
        pass


T = TypeVar('T', bound=_Type)


def interfaceMixInMeta(cls):
    class_create = getattr(cls, 'create', None)

    def create(self, model: B) -> List[ItemContainer]:
        cls_s: List[Type[T]] = [c_ for c_ in cls.__bases__ if getattr(c_, '_internal_type', False)]
        r_list = []
        if class_create is not None:
            r_list += class_create(self, model)
        for cls_ in cls_s:
            r_list += cls_.create(self, model)
        return r_list

    setattr(cls, 'create', create)
    return cls


class Neutron(_Type):
    pass


class XRay(_Type):
    pass


class Powder(_Type):
    pass


class SingleCrystal(_Type):
    pass


class CW(_Type):
    pass


class TOF(_Type):
    pass


class Pol(_Type):
    pass


class UPol(_Type):
    pass
