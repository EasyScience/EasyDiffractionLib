#  SPDX-FileCopyrightText: 2022 easyCrystallography contributors  <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022 Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>
#

from __future__ import annotations

__author__ = "github.com/wardsimon"
__version__ = "0.2.0"

from easyCore import np
from easyCore.Objects.ObjectClasses import Descriptor, Parameter, BaseObj
from easyCore.Objects.Groups import BaseCollection
from typing import List, Union, ClassVar, TypeVar, Optional, TYPE_CHECKING
from easyCore.Utils.io.star import StarLoop

from easyCrystallography.Components.Site import (
    Site as ecSite,
    PeriodicSite as ecPeriodicSite,
    Atoms as ecAtoms,
    PeriodicAtoms as ecPeriodicAtoms,
)
from easyCrystallography.Components.Lattice import PeriodicLattice
from easyCrystallography.Components.Specie import Specie
from easyCrystallography.Components.AtomicDisplacement import AtomicDisplacement
from easyCrystallography.Components.Susceptibility import MagneticSusceptibility


if TYPE_CHECKING:
    from easyCore.Utils.typing import iF

class Site(ecSite):
    def __init__(
        self,
        label: Optional[Union[str, Descriptor]] = None,
        specie: Optional[Union[str, Specie]] = None,
        occupancy: Optional[Union[float, Parameter]] = None,
        fract_x: Optional[Union[float, Parameter]] = None,
        fract_y: Optional[Union[float, Parameter]] = None,
        fract_z: Optional[Union[float, Parameter]] = None,
        adp: Optional[Union[str, AtomicDisplacement]] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):

        if "msp" in kwargs.keys():
            msp = kwargs.pop("msp")
            if isinstance(msp, str):
                msp = MagneticSusceptibility(msp)
            for parameter in msp.get_parameters:
                if parameter.name in kwargs.keys():
                    new_option = kwargs.pop(parameter.name)
                    parameter.value = new_option
            kwargs["msp"] = msp

        if adp is not None:
            if isinstance(adp, str):
                adp = AtomicDisplacement(adp)
            for parameter in adp.get_parameters():
                if parameter.name in kwargs.keys():
                    new_option = kwargs.pop(parameter.name)
                    parameter.value = new_option
            kwargs["adp"] = adp

        super(Site, self).__init__(
            label=label,
            specie=specie,
            occupancy=occupancy,
            fract_x=fract_x,
            fract_y=fract_y,
            fract_z=fract_z,
            **kwargs,
        )
        self.interface = interface


class PeriodicSite(ecPeriodicSite):
    @classmethod
    def from_site(cls, lattice: PeriodicLattice, site: Site):
        kwargs = ecPeriodicSite._from_site_kwargs(lattice, site)
        if hasattr(site, "adp"):
            kwargs["adp"] = site.adp
        return cls(**kwargs)


class Atoms(ecAtoms):

    _SITE_CLASS = Site

    def to_star(self) -> List[StarLoop]:
        main_loop = super(Atoms, self).to_star()[0]
        adps = [hasattr(item, "adp") for item in self]
        has_adp = any(adps)
        if not has_adp:
            return [main_loop]
        add_loops = []
        adp_types = [item.adp.adp_type.raw_value for item in self]
        if all(adp_types):
            if adp_types[0] in ["Uiso", "Biso"]:
                main_loop = main_loop.join(
                    StarLoop.from_StarSections(
                        [getattr(item, "adp").to_star(item.label) for item in self]
                    ),
                    "label",
                )
            else:
                entries = []
                for item in self:
                    entries.append(item.adp.to_star(item.label))
                add_loops.append(StarLoop.from_StarSections(entries))
        else:
            raise NotImplementedError("Multiple types of ADP are not supported")
        loops = [main_loop, *add_loops]
        return loops


class PeriodicAtoms(ecPeriodicAtoms):
    _SITE_CLASS = PeriodicSite
