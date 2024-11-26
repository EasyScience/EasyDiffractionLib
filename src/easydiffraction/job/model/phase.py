# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from easycrystallography.Structures.Phase import Phase as ecPhase
from easycrystallography.Structures.Phase import Phases as ecPhases

from .site import Atoms
from .site import Site


class Phase(ecPhase):
    _SITE_CLASS = Site
    _ATOMS_CLASS = Atoms

    def __init__(self, name, spacegroup=None, cell=None, atoms=None, scale=None, interface=None, enforce_sym=True, **kwargs):
        super(Phase, self).__init__(name, spacegroup, cell, atoms, scale, enforce_sym=enforce_sym)
        self.interface = interface

    def add_atom(self, *args, **kwargs):
        super(Phase, self).add_atom(*args, **kwargs)
        if self.interface is not None:
            self.interface().link_atom(self, self.atoms[-1])

    def remove_atom(self, key):
        item = self.atoms[key]
        super(Phase, self).remove_atom(key)
        if self.interface is not None:
            self.interface().remove_atom(self, item)

    @property
    def atom_sites(self):
        """
        Vanity method to alias `atoms`
        """
        return self.atoms


class Phases(ecPhases):
    _SITE_CLASS = Site
    _ATOM_CLASS = Atoms
    _PHASE_CLASS = Phase

    def append(self, item: Phase):
        super(Phases, self).append(item)
        if self.interface is not None:
            self.interface().add_phase(self, item)

    def __delitem__(self, key):
        item = self[key]
        if self.interface is not None:
            self.interface().remove_phase(self, item)
        super(Phases, self).__delitem__(key)

    @classmethod
    def from_cif_file(cls, filename):
        return super(Phases, cls).from_cif_file(filename)

    @classmethod
    def from_cif_string(cls, cif_string):
        return super(Phases, cls).from_cif_string(cif_string)
