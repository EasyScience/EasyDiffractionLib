__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


from easyCore.Elements.HigherLevel.Phase import Phases, Atoms, Site, SpaceGroup, Lattice, Phase

"""
This is a horrendous monkey patch of the Phase and Phases class so that adding and removing communicates
with the interface. If you are shaking your head in disbelief, I'm sorry........
"""

_a_atom = getattr(Phase, "add_atom")
_rm_atom = getattr(Phase, "remove_atom")


def _add_atom(self, *args, **kwargs):
    _a_atom(self, *args, **kwargs)
    if self.interface is not None:
        self.interface().link_atom(self, self.atoms[-1])


def _remove_atom(self, key):
    item = self.atoms[key]
    _rm_atom(self, key)
    if self.interface is not None:
        self.interface().remove_atom(self, item)


setattr(Phase, "add_atom", _add_atom)
setattr(Phase, "remove_atom", _remove_atom)

_d_item = getattr(Phases, "__delitem__")
_a_item = getattr(Phases, "append")


def _p__delitem__(self, key):
    item = self[key]
    if self.interface is not None:
        self.interface().removePhase(self, item)
    return _d_item(self, key)


def _append(self, item: Phase):
    _a_item(self, item)
    if self.interface is not None:
        self.interface().assignPhase(self, item)


setattr(Phases, "__delitem__", _p__delitem__)
setattr(Phases, "append", _a_item)
