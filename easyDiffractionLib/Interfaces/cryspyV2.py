__author__ = "github.com/wardsimon"
__version__ = "0.0.2"

from abc import ABCMeta
from easyCore import borg, np
from easyCore.Objects.Inferface import ItemContainer
from easyDiffractionLib import Lattice, SpaceGroup, Site, Phase, Phases
from easyDiffractionLib.Profiles.P1D import (
    Instrument1DCWParameters,
    Instrument1DTOFParameters,
    Instrument1DCWPolParameters,
    Powder1DParameters,
)
from easyDiffractionLib.components.polarization import PolarizedBeam
from easyDiffractionLib.Interfaces.interfaceTemplate import InterfaceTemplate
from easyDiffractionLib.calculators.cryspy import Cryspy as Cryspy_calc


class MetaCryspy:

    _borg = borg

    def create(self, model):
        cls = self.__class__
        cls_s = cls.__mro__[0:cls.__mro__.index(MetaCryspy)]
        r_list = []
        for cls_ in cls_s:
            if hasattr(cls_, "create"):
                r = cls_.create(self, model, master=True)
                if r is not None and isinstance(r, list):
                    r_list += r
        return r_list

    @staticmethod
    def _identify(obj):
        return borg.map.convert_id_to_key(obj)


class CryspyBase(MetaCryspy, metaclass=ABCMeta):
    """
    A simple example interface using Cryspy
    """

    _sample_link = {"cif_str": "cif_str"}

    _crystal_link = {
        "length_a": "length_a",
        "length_b": "length_b",
        "length_c": "length_c",
        "angle_alpha": "angle_alpha",
        "angle_beta": "angle_beta",
        "angle_gamma": "angle_gamma",
    }

    _atom_link = {
        "label": "label",
        "specie": "type_symbol",
        "fract_x": "fract_x",
        "fract_y": "fract_y",
        "fract_z": "fract_z",
        "occupancy": "occupancy",
        "adp_type": "adp_type",
        "Uiso": "u_iso_or_equiv",
        "Biso": "b_iso_or_equiv",
        "Uani": "u_iso_or_equiv",
        "Bani": "b_iso_or_equiv",
    }
    _subsets = []

    def __init__(self, calculator=None, **kwargs):
        self.calculator = calculator

    def __init_subclass__(cls, is_abstract: bool = False, **kwargs):
        """
        Initialise all subclasses so that they can be created in the factory

        :param is_abstract: Is this a subclass which shouldn't be dded
        :type is_abstract: bool
        :param kwargs: key word arguments
        :type kwargs: dict
        :return: None
        :rtype: noneType
        """
        super().__init_subclass__(**kwargs)
        if not is_abstract:
            cls._subsets.append(cls)

    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        if issubclass(t_, Lattice):
            l_key = self.calculator.createCell(model_key)
            keys = self._crystal_link.copy()
            r_list.append(
                ItemContainer(
                    l_key,
                    keys,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        elif issubclass(t_, SpaceGroup):
            s_key = self.calculator.createSpaceGroup(key=model_key, name_hm_alt="P 1")
            keys = {"_space_group_HM_name": "name_hm_alt"}
            r_list.append(
                ItemContainer(
                    s_key,
                    keys,
                    self.calculator.getSpaceGroupSymbol,
                    self.calculator.updateSpacegroup,
                )
            )
        elif issubclass(t_, Site):
            a_key = self.calculator.createAtom(model_key)
            keys = self._atom_link.copy()
            r_list.append(
                ItemContainer(
                    a_key,
                    keys,
                    lambda x, y: self.calculator.genericReturn(a_key, y),
                    lambda x, **y: self.calculator.genericUpdate(a_key, **y),
                )
            )
        elif issubclass(t_, Phase):
            ident = str(model_key) + "_phase"
            self.calculator.createPhase(ident)
            crystal_name = self.calculator.createEmptyCrystal(model.name, key=model_key)
            self.calculator.assignCell_toCrystal(self.__identify(model.cell), model_key)
            self.calculator.assignSpaceGroup_toCrystal(
                self.__identify(model._spacegroup), model_key
            )
            self.calculator.setPhaseScale(str(model_key), scale=model.scale.raw_value)
            r_list.append(
                ItemContainer(
                    model_key,
                    {"scale": "scale"},
                    self.calculator.getPhaseScale,
                    self.calculator.setPhaseScale,
                )
            )
            for atom in model.atoms:
                self.calculator.assignAtom_toCrystal(self.__identify(atom), model_key)
        elif issubclass(t_, Phases):
            # self.calculator.createModel(model_key, 'powder1D')
            for phase in model:
                ident = str(self.__identify(phase)) + "_phase"
                self.calculator.assignPhase(model_key, ident)
        else:
            if self._borg.debug:
                print(f"I'm a: {type(model)}")
        return r_list

    def link_atom(self, crystal_obj, atom):
        crystal_name = self.__identify(crystal_obj)
        self.calculator.assignAtom_toCrystal(self.__identify(atom), crystal_name)

    def remove_atom(self, crystal_obj, atom):
        crystal_name = self.__identify(crystal_obj)
        self.calculator.removeAtom_fromCrystal(self.__identify(atom), crystal_name)

    def add_phase(self, phases_obj, phase_obj):
        ident = str(self.__identify(phase_obj)) + "_phase"
        self.calculator.assignPhase(self.__identify(phases_obj), ident)
        self.calculator.setPhaseScale(
            self.__identify(phase_obj), scale=phase_obj.scale.raw_value
        )

    def remove_phase(self, phases_obj, phase_obj):
        ident = str(self.__identify(phase_obj)) + "_phase"
        self.calculator.removePhase(self.__identify(phases_obj), ident)

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
        return self.calculator.get_hkl(idx, phase_name, encoded_name)

    def get_phase_components(self, phase_name):
        data = self.calculator.get_phase_components(phase_name)
        return data

    def _createModel(self, model, model_type):
        self.calculator.createModel(model, model_type)

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        return self.calculator.get_calculated_y_for_phase(phase_idx)

    def get_total_y_for_phases(self) -> list:
        return self.calculator.get_total_y_for_phases()


class Powder:
    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Powder1DParameters):
            # These parameters do not link directly to cryspy objects.
            self.calculator.pattern = model
        return r_list


class SingleCrystal:
    pass


class CW:
    _instrument_link = {
        "resolution_u": "u",
        "resolution_v": "v",
        "resolution_w": "w",
        "resolution_x": "x",
        "resolution_y": "y",
        "wavelength":   "wavelength",
    }

    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Instrument1DCWParameters):
            self.calculator.createModel(model_key, "powder1DCW")
            # These parameters are linked to the Resolution and Setup cryspy objects
            res_key = self.calculator.createResolution()
            setup_key = self.calculator.createSetup()
            keys = self._instrument_link.copy()
            keys.pop("wavelength")
            r_list.append(
                ItemContainer(
                    res_key,
                    keys,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
            r_list.append(
                ItemContainer(
                    setup_key,
                    {"wavelength": self._instrument_link["wavelength"]},
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        return r_list


class TOF:
    _instrument_tof_link = {k: k for k in Instrument1DTOFParameters._defaults.keys()}

    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Instrument1DTOFParameters):
            self.calculator.createModel(model_key, "powder1DTOF")
            # These parameters are linked to the Resolution and Setup cryspy objects
            res_key = self.calculator.createResolution(cls_type="powder1DTOF")
            setup_key = self.calculator.createSetup(cls_type="powder1DTOF")
            keys = self._instrument_tof_link.copy()

            setup_keys = {k: keys[k] for k in ["ttheta_bank", "dtt1", "dtt2"]}
            res_keys = {
                k: keys[k]
                for k in [
                    "sigma0",
                    "sigma1",
                    "sigma2",
                    "gamma0",
                    "gamma1",
                    "gamma2",
                    "alpha0",
                    "alpha1",
                    "beta0",
                    "beta1",
                ]
            }
            r_list.append(
                ItemContainer(
                    res_key,
                    res_keys,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
            r_list.append(
                ItemContainer(
                    setup_key,
                    setup_keys,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        return r_list


class POL:
    _polarization_link = {
        "polarization": "polarization",
        "efficiency": "efficiency",
    }

    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, PolarizedBeam):
            p_key = self.calculator.createPolarization()
            r_list.append(
                ItemContainer(
                    p_key,
                    self._polarization_link,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        return r_list


class CryspyCW(CryspyBase, CW, Powder):
    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = 'powder1DCW'
        if t_.__name__ == "Sample" or t_.__name__ in ["Powder1DCW", "powder1DCW", "Npowder1DCW"]:
            self._createModel(model_key, base)
        return r_list


class CryspyTOF(CryspyBase, TOF, Powder):
    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = 'powder1DTOF'
        if t_.__name__ == "Sample" or t_.__name__ in ["Powder1DTOF", "powder1DTOF", "Npowder1DTOF"]:
            self._createModel(model_key, base)
        return r_list


class CryspyCWPol(CryspyCW, POL, CW, Powder):
    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = 'powder1DCWpol'
        if t_.__name__ == "Sample" or t_.__name__ in ["Powder1DCWpol", "powder1DCWpol", "Npowder1DCWpol"]:
            self._createModel(model_key, base)
        return r_list


class CryspyTOFPol(CryspyTOF, POL, TOF, Powder):
    def create(self, model, master=False):
        if not master:
            return MetaCryspy.create(self, model)
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = 'powder1DTOFpol'
        if t_.__name__ == "Sample" or t_.__name__ in ["Powder1DTOFpol", "powder1DTOFpol", "Npowder1DTOFpol"]:
            self._createModel(model_key, base)
        return r_list


class CryspyV2(InterfaceTemplate):

    name = "CrysPyV2"

    feature_available = {"Npowder1DCWunp": True, "Npowder1DTOFunp": True, "Npowder1DCWpol": True}

    def __init__(self):
        self.calculator = Cryspy_calc()
        self._internal = None

    @staticmethod
    def feature_checker(
        radiation="N",
        exp_type="CW",
        sample_type="powder",
        dimensionality="1D",
        polarization='unp',
        test_str=None,
    ):
        return InterfaceTemplate.features(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            polarization=polarization,
            test_str=test_str,
            FEATURES=CryspyV2.feature_available,
        )

    def create(self, model):
        cls = CryspyBase._subsets[0]
        self._internal = cls(calculator=self.calculator)
        return self._internal.create(model)

    def link_atom(self, model_name: str, atom):
        if self._internal is not None:
            self._internal.link_atom(model_name, atom)

    def remove_atom(self, model_name: str, atom: str):
        if self._internal is not None:
            self._internal.remove_atom(model_name, atom)

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        if self._internal is not None:
            return self._internal.fit_func(x_array)

    def get_hkl(self, x_array: np.ndarray = None, idx=None) -> dict:
        if self._internal is not None:
            return self._internal.get_hkl(x_array, idx)

    def get_calculated_y_for_phase(self, idx=None) -> list:
        if self._internal is not None:
            return self._internal.get_calculated_y_for_phase(idx)

    def get_total_y_for_phases(self) -> list:
        if self._internal is not None:
            return self._internal.get_total_y_for_phases()