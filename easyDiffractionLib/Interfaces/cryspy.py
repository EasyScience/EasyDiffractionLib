__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import numpy as np
from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
from easyCore.Objects.Inferface import ItemContainer
from easyDiffractionLib.Calculators.cryspy import Cryspy as Cryspy_calc
from easyDiffractionLib.Elements.Experiments.Experiment import Pars1D
from easyDiffractionLib.Elements.Experiments.Pattern import Pattern1D
from easyDiffractionLib import Lattice, SpaceGroup, Site, Phase


class Cryspy(InterfaceTemplate):
    """
    A simple example interface using CFML
    """

    _sample_link = {
        'cif_str': 'cif_str'}

    _crystal_link = {
        "length_a": "length_a",
        "length_b": "length_b",
        "length_c": "length_c",
        "angle_alpha": "angle_alpha",
        "angle_beta": "angle_beta",
        "angle_gamma": "angle_gamma",
    }

    _atom_link = {
       'label': 'label',
       'specie': 'type_symbol',
       'fract_x': 'fract_x',
       'fract_y': 'fract_y',
       'fract_z': 'fract_z',
       'occupancy': 'occupancy',
       'adp_type': 'adp_type',
       'Uiso': 'u_iso_or_equiv',
       'Biso': 'b_iso_or_equiv',
       'Uani': 'u_iso_or_equiv',
       'Bani': 'b_iso_or_equiv'
    }
    _instrument_link = {
        'resolution_u': 'u',
        'resolution_v': 'v',
        'resolution_w': 'w',
        'resolution_x': 'x',
        'resolution_y': 'y',
        'wavelength': 'wavelength'
    }

    name = 'CrysPy'

    def __init__(self):
        self.calculator = Cryspy_calc()
        self._namespace = {}

    def create(self, model):
        r_list = []
        t_ = type(model)
        if issubclass(t_, Pars1D):
            # These parameters are linked to the Resolution and Setup cryspy objects
            res_key = self.calculator.createResolution()
            setup_key = self.calculator.createSetup()
            keys = self._instrument_link.copy()
            keys.pop('wavelength')
            r_list.append(
                ItemContainer(res_key, keys,
                              self.calculator.genericReturn,
                              self.calculator.genericUpdate)
            )
            r_list.append(
                ItemContainer(setup_key, {'wavelength': self._instrument_link['wavelength']},
                              self.calculator.genericReturn,
                              self.calculator.genericUpdate)
            )
        elif issubclass(t_, Pattern1D):
            # These parameters do not link directly to cryspy objects.
            self.calculator.pattern = model
        elif issubclass(t_, Lattice):
            l_key = self.calculator.createCell()
            keys = self._crystal_link.copy()
            r_list.append(
                ItemContainer(l_key, keys,
                              self.calculator.genericReturn,
                              self.calculator.genericUpdate)
            )
        elif issubclass(t_, SpaceGroup):
            s_key = self.calculator.createSpaceGroup(name_hm_alt='P 1')
            keys = {'_space_group_HM_name': 'name_hm_alt'}
            r_list.append(
                ItemContainer(s_key, keys,
                              self.calculator.genericReturn,
                              self.calculator.updateSpacegroup)
            )
        elif issubclass(t_, Site):
            a_key = self.calculator.createAtom(model.label.raw_value)
            keys = self._atom_link.copy()
            r_list.append(ItemContainer(a_key, keys,
                                        lambda x, y: self.calculator.genericReturn(model.label.raw_value, y),
                                        lambda x, **y: self.calculator.genericUpdate(model.label.raw_value, **y)))
        elif issubclass(t_, Phase):
            crystal_name = self.calculator.createEmptyCrystal(model.name)
            self.calculator.assignCell_toCrystal('cell', crystal_name)
            self.calculator.assignSpaceGroup_toCrystal('spacegroup', crystal_name)
            for atom in model.atoms:
                self.calculator.assignAtom_toCrystal(atom.label.raw_value, crystal_name)
        else:
            if self._borg.debug:
                print(f"I'm a: {type(model)}")
        return r_list

    def link_atom(self, crystal_name, atom):
        self.calculator.assignAtom_toCrystal(atom.label.raw_value, crystal_name)

    def remove_atom(self, crystal_name: str, atom_label):
        self.calculator.removeAtom_fromCrystal(atom_label, crystal_name)

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit
        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        return self.calculator.calculate(x_array)

    def get_hkl(self, x_array: np.ndarray = None) -> dict:
        return self.calculator.get_hkl(x_array)
