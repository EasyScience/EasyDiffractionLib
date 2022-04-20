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
        msp: Optional[Union[str, MagneticSusceptibility]] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):

        if msp is not None:
            if isinstance(msp, str):
                msp = MagneticSusceptibility(msp)
            for parameter in msp.get_parameters():
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
        if hasattr(site, "msp"):
            kwargs["msp"] = site.msp
        return cls(**kwargs)


class Atoms(ecAtoms):

    _SITE_CLASS = Site

    def to_star(self) -> List[StarLoop]:
        add_loops = []
        main_loop = super(Atoms, self).to_star()[0]

        self.add_adp(main_loop, add_loops)
        self.add_msp(main_loop, add_loops)

        loops = [main_loop, *add_loops]

        return loops

    def add_adp(self, main_loop, add_loops):

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
        return add_loops

    def add_msp(self, main_loop, add_loops):

        msps = [hasattr(item, "msp") for item in self]
        has_msp = any(msps)
        if not has_msp:
            # initialize msp so as_dict doesn't throw a fit
            for item in self:
                msp = MagneticSusceptibility("Cani")
                item.msp = msp
        add_loops = []
        msp_types = [item.msp.msp_type.raw_value for item in self if hasattr(item, 'msp')]
        if all(msp_types):
            if msp_types[0] in ["Cani", "Ciso"]:
                loops = []
                for item in self:
                    if not hasattr(item, 'msp'):
                        msp_item = MagneticSusceptibility(msp_types[0])
                        item.msp = msp_item
                    loops.append(getattr(item, 'msp').to_star(item.label))
                msp_loop = StarLoop.from_StarSections(loops)
                main_loop = main_loop.join(msp_loop, "label")
            else:
                pass
                entries = []
                for item in self:
                    if hasattr(item, 'msp'):
                        entries.append(item.msp.to_star(item.label))
                    else:
                        msp = MagneticSusceptibility(msp_types[0])
                        item.msp = msp
                        entries.append(msp.to_star(item.label))
                add_loops.append(StarLoop.from_StarSections(entries))
        else:
            raise NotImplementedError("Multiple types of MSP are not supported")
        return add_loops
class PeriodicAtoms(ecPeriodicAtoms):
    _SITE_CLASS = PeriodicSite
