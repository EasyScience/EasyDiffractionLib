__author__ = "github.com/wardsimon"
__version__ = "0.0.2"

import os
from easyCore import borg, np
from easyCore.Objects.Inferface import ItemContainer

from easyDiffractionLib import Lattice, SpaceGroup, Site, Phases, Phase

from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters, Powder1DParameters
from easyDiffractionLib.Calculators.CFML import CFML as CFML_calc


class CFML(InterfaceTemplate):
    """
    A simple FILE interface using CrysFML
    """

    _sample_link = {"filename": "filename"}

    _crystal_link = {
        "length_a": "length_a",
        "length_b": "length_b",
        "length_c": "length_c",
        "angle_alpha": "angle_alpha",
        "angle_beta": "angle_beta",
        "angle_gamma": "angle_gamma",
    }

    _instrument_link = {
        "resolution_u": "u_resolution",
        "resolution_v": "v_resolution",
        "resolution_w": "w_resolution",
        "resolution_x": "x_resolution",
        "resolution_y": "y_resolution",
        "wavelength": "lamb",
    }

    _atom_link = {
        "label": "label",
        "specie": "specie",
        "fract_x": "fract_x",
        "fract_y": "fract_y",
        "fract_z": "fract_z",
        "occupancy": "occupancy",
        "adp_type": "adp_type",
        "Uiso": "Uiso",
        "Biso": "Biso",
        "Uani": "Uani",
        "Bani": "Bani",
    }
    _pattern_link = {"scale": "scale", "x_offset": "x_offset"}

    feature_available = {"Npowder1DCW": True}

    name = "CrysFML"

    def __init__(self):
        self.calculator = CFML_calc()
        self._phase = None
        self._filename = None

    @staticmethod
    def feature_checker(
        radiation="N",
        exp_type="CW",
        sample_type="powder",
        dimensionality="1D",
        test_str=None,
    ):
        return InterfaceTemplate.features(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            test_str=test_str,
            FEATURES=CFML.feature_available,
        )

    def create(self, model):
        from easyDiffractionLib.sample import Sample

        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Instrument1DCWParameters):
            # These parameters are linked to the Resolution and Setup CFML objects. Note that we can set the job type!
            self.calculator.createConditions(job_type="N")
            keys = self._instrument_link.copy()
            r_list.append(
                ItemContainer(
                    model_key,
                    keys,
                    self.calculator.conditionsReturn,
                    self.calculator.conditionsUpdate,
                )
            )
        elif issubclass(t_, Powder1DParameters):
            # These parameters do not link directly to CFML objects.
            self.calculator.pattern = model
        elif issubclass(t_, Lattice):
            keys = self._crystal_link.copy()
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.dump_cif))
        elif issubclass(t_, SpaceGroup):
            keys = {"_space_group_HM_name": "_space_group_HM_name"}
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.dump_cif))
        elif issubclass(t_, Site):
            keys = self._atom_link.copy()
            r_list.append(ItemContainer(model_key, keys, self.get_value, self.dump_cif))
        elif issubclass(t_, Phases):
            self._phase = model
        elif issubclass(t_, Phase):
            r_list.append(
                ItemContainer(
                    model_key,
                    {"scale": "scale"},
                    self.calculator.getPhaseScale,
                    self.calculator.setPhaseScale,
                )
            )
            self.calculator.add_phase(str(model_key), model.name)
        elif issubclass(t_, Sample):
            self.__createModel(model)
        elif t_.__name__ in ["Powder1DCW", "powder1DCW", "Npowder1DCW"]:
            self.__createModel(model)
        else:
            if self._borg.debug:
                print(f"I'm a: {type(model)}")
        return r_list

    def link_atom(self, crystal_obj, atom):
        pass

    def remove_atom(self, crystal_obj, atom):
        pass

    def add_phase(self, phases_obj, phase_obj):
        ident = str(self.__identify(phase_obj))
        self.calculator.add_phase(ident, phase_obj.name)

    def remove_phase(self, phases_obj, phase_obj):
        ident = str(self.__identify(phase_obj))
        self.calculator.remove_phase(ident)

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit
        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        return self.calculator.calculate(x_array)

    def get_hkl(self, x_array: np.ndarray = None, idx=None, phase_name=None, encoded_name=False) -> dict:
        return self.calculator.get_hkl(x_array)

    def dump_cif(self, *args, **kwargs):
        if self._filename is None:
            return
        with open(self._filename, "w") as fid:
            fid.write(str(self._phase.cif))
        base, file = os.path.split(self._filename)
        ext = file[-3:]
        file = file[:-4]
        for idx, phase in enumerate(self._phase):
            with open(f"{os.path.join(base, file)}_{idx}.{ext}", "w") as fid:
                fid.write(str(phase.cif))

    def __createModel(self, model):
        self._filename = model.filename
        self.calculator.filename = model.filename
        self.dump_cif()

    def get_value(self, key, item_key):
        item = borg.map.get_item_by_key(key)
        if item_key in ["Uiso", "Uani", "Biso", "Bani"]:
            return getattr(getattr(item, "adp"), item_key).raw_value
        return getattr(item, item_key).raw_value

    def get_phase_components(self, phase_name):
        return None

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        return self.calculator.get_calculated_y_for_phase(phase_idx)

    def get_total_y_for_phases(self) -> list:
        return self.calculator.get_total_y_for_phases()

    @staticmethod
    def __identify(obj):
        return borg.map.convert_id_to_key(obj)
