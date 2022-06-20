from __future__ import annotations

#  SPDX-FileCopyrightText: 2022 easyCrystallography contributors  <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022 Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>
#
__author__ = "github.com/wardsimon"
__version__ = "0.2.0"

from easyCore.Objects.ObjectClasses import Descriptor, Parameter, BaseObj
from easyCore.Objects.Groups import BaseCollection
from typing import List, Union, ClassVar, TypeVar, Optional, TYPE_CHECKING

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


def _option_parser(obj, cls, name, kwargs):
    if isinstance(obj, str):
        obj = cls(obj)
    for parameter in obj.get_parameters():
        if parameter.name in kwargs.keys():
            new_option = kwargs.pop(parameter.name)
            parameter.value = new_option
    kwargs[name] = obj


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
            _option_parser(msp, MagneticSusceptibility, "msp", kwargs)
            # if isinstance(msp, str):
            #     msp = MagneticSusceptibility(msp)
            # for parameter in msp.get_parameters():
            #     if parameter.name in kwargs.keys():
            #         new_option = kwargs.pop(parameter.name)
            #         parameter.value = new_option
            # kwargs["msp"] = msp

        if adp is not None:
            _option_parser(adp, AtomicDisplacement, "adp", kwargs)
            # if isinstance(adp, str):
            #     adp = AtomicDisplacement(adp)
            # for parameter in adp.get_parameters():
            #     if parameter.name in kwargs.keys():
            #         new_option = kwargs.pop(parameter.name)
            #         parameter.value = new_option
            # kwargs["adp"] = adp

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


class PeriodicAtoms(ecPeriodicAtoms):
    _SITE_CLASS = PeriodicSite
