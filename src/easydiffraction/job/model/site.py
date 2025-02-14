# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Union

from easycrystallography.Components.AtomicDisplacement import AtomicDisplacement
from easycrystallography.Components.Site import Atoms as ecAtoms
from easycrystallography.Components.Site import Site as ecSite
from easycrystallography.Components.Specie import Specie
from easycrystallography.Components.Susceptibility import MagneticSusceptibility
from easycrystallography.io.star_base import StarLoop
from easyscience.Objects.variable import DescriptorStr as Descriptor
from easyscience.Objects.variable import Parameter

if TYPE_CHECKING:
    from easyscience.Objects.Inferface import iF


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
        msp = kwargs.get('msp', None)
        if msp is not None:
            if isinstance(msp, str):
                msp = MagneticSusceptibility(msp)
            for parameter in msp.get_parameters():
                if parameter.name in kwargs.keys():
                    new_option = kwargs.pop(parameter.name)
                    parameter.value = new_option
            kwargs['msp'] = msp

        if adp is not None:
            if isinstance(adp, str):
                adp = AtomicDisplacement(adp)
            for parameter in adp.get_parameters():
                if parameter.name in kwargs.keys():
                    new_option = kwargs.pop(parameter.name)
                    parameter.value = new_option
            kwargs['adp'] = adp

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

    def add_adp(self, adp_type: Union[str, AtomicDisplacement], **kwargs):
        if isinstance(adp_type, str):
            adp_type = AtomicDisplacement(adp_type, **kwargs)
        self._add_component('adp', adp_type)
        if self.interface is not None:
            self.interface.generate_bindings()

    def add_msp(self, msp_type: Union[str, MagneticSusceptibility], **kwargs):
        if isinstance(msp_type, str):
            msp_type = MagneticSusceptibility(msp_type, **kwargs)
        self._add_component('msp', msp_type)
        if self.interface is not None:
            self.interface.generate_bindings()


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
        adps = [hasattr(item, 'adp') for item in self]
        has_adp = any(adps)
        if not has_adp:
            return [main_loop]
        add_loops = []
        adp_types = [item.adp.adp_type.value for item in self]
        if all(adp_types):
            if adp_types[0] in ['Uiso', 'Biso']:
                main_loop = main_loop.join(
                    StarLoop.from_StarSections([getattr(item, 'adp').to_star(item.label) for item in self]),
                    'label',
                )
            else:
                entries = []
                for item in self:
                    entries.append(item.adp.to_star(item.label))
                add_loops.append(StarLoop.from_StarSections(entries))
        else:
            raise NotImplementedError('Multiple types of ADP are not supported')
        return add_loops

    def add_msp(self, main_loop, add_loops):
        # msps = [hasattr(item, "msp") for item in self]
        # has_msp = any(msps)
        loops = []
        # if has_msp:
        for item in self:
            if hasattr(item, 'msp'):
                loops.append(getattr(item, 'msp').to_star(item.label))
        if loops:
            add_loops.append(StarLoop.from_StarSections(loops))
        # if not has_msp:
        #     # initialize msp so as_dict doesn't throw a fit
        #     for item in self:
        #         msp = MagneticSusceptibility("Ciso")
        #         item.msp = msp
        #         item.msp.default = True
        # add_loops = []
        # msp_types = [
        #     item.msp.msp_type.raw_value for item in self if hasattr(item, "msp")
        # ]
        # if all(msp_types):
        #     if msp_types[0] in ["Cani", "Ciso"]:
        #         loops = []
        #         for item in self:
        #             if not hasattr(item, "msp"):
        #                 msp_item = MagneticSusceptibility(msp_types[0])
        #                 item.msp = msp_item
        #                 item.msp.default = False
        #             loops.append(getattr(item, "msp").to_star(item.label))
        #         msp_loop = StarLoop.from_StarSections(loops)
        #         main_loop = main_loop.join(msp_loop, "label")
        #     else:
        #         pass
        #         entries = []
        #         for item in self:
        #             if hasattr(item, "msp"):
        #                 entries.append(item.msp.to_star(item.label))
        #             else:
        #                 msp = MagneticSusceptibility(msp_types[0])
        #                 item.msp = msp
        #                 item.msp.default = False
        #                 entries.append(msp.to_star(item.label))
        #         add_loops.append(StarLoop.from_StarSections(entries))
        # else:
        #     raise NotImplementedError("Multiple types of MSP are not supported")
        # return add_loops
