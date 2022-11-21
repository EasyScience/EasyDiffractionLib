__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import Optional
from easyCrystallography.Structures.Phase import Phase as ecPhase, Phases as ecPhases
from .site import Site, Atoms


class Phase(ecPhase):
    _SITE_CLASS = Site
    _ATOMS_CLASS = Atoms

    def __init__(
        self,
        name,
        spacegroup=None,
        cell=None,
        atoms=None,
        scale=None,
        interface=None,
        enforce_sym=True,
        **kwargs
    ):
        super(Phase, self).__init__(
            name, spacegroup, cell, atoms, scale, enforce_sym=enforce_sym
        )
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

