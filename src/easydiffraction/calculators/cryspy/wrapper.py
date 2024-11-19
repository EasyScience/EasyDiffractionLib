# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/EasyScience/EasyDiffraction>

from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

import numpy as np
from easycrystallography.Components.AtomicDisplacement import Anisotropic as Anisotropic_base
from easycrystallography.Components.Site import Site as Site_base
from easyscience import global_object as borg
from easyscience.Objects.Inferface import ItemContainer
from numpy import ndarray

from easydiffraction import Lattice
from easydiffraction import Phase
from easydiffraction import Phases
from easydiffraction import Site
from easydiffraction import SpaceGroup
from easydiffraction.calculators.cryspy.calculator import Cryspy as Cryspy_calc
from easydiffraction.calculators.wrapper_base import WrapperBase
from easydiffraction.calculators.wrapper_types import CW as CW_type
from easydiffraction.calculators.wrapper_types import TOF as TOF_type
from easydiffraction.calculators.wrapper_types import Neutron as Neutron_type
from easydiffraction.calculators.wrapper_types import Pol as Pol_type
from easydiffraction.calculators.wrapper_types import Powder as Powder_type
from easydiffraction.calculators.wrapper_types import SingleCrystal as SingleCrystal_type
from easydiffraction.calculators.wrapper_types import UPol as UPol_type
from easydiffraction.calculators.wrapper_types import interfaceMixInMeta
from easydiffraction.components.polarization import PolarizedBeam
from easydiffraction.Profiles.P1D import Instrument1DCWParameters
from easydiffraction.Profiles.P1D import Instrument1DTOFParameters
from easydiffraction.Profiles.P1D import Powder1DParameters

if TYPE_CHECKING:
    from easyscience.Utils.typing import B


class CryspyBase(Neutron_type, metaclass=ABCMeta):
    """
    In this class we deal with the creation of the base crystal structure. No calculation is performed from this class,
    it only creates the crystal structure and inherits all the experiment types from the plugins.
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
    _borg = borg

    def __init__(self, calculator: Optional[Cryspy_calc] = None):
        """
        Initialise the calculator.
        :param calculator: Cryspy instance
        :type calculator:
        :param kwargs:
        :type kwargs:
        """
        self.calculator = calculator

    def __init_subclass__(cls, is_abstract: bool = False, **kwargs):
        """
        Initialise all subclasses so that they can be created in the factory

        :param is_abstract: Is this a subclass which shouldn't be added
        :type is_abstract: bool
        :param kwargs: key word arguments
        :type kwargs: dict
        :return: None
        :rtype: noneType
        """
        super().__init_subclass__(**kwargs)
        if not is_abstract:
            cls._subsets.append(cls)

    def create(self, model: B) -> List[ItemContainer]:
        """
        Create the crystal structure. This deals with interfacing with `Lattice`, `SpaceGroup` `Site`, `Phase`, and
        `Phases`.
        :param model: The model elements to interface with
        :param master: If master we call the mixin create function
        :return: List of links
        """
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)

        # Interface with lattice
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
        # Interface with Spacegroup
        elif issubclass(t_, SpaceGroup):
            s_key = self.calculator.createSpaceGroup(key=model_key, name_hm_alt="P 1")
            keys = {"hermann_mauguin": "name_hm_alt"}
            r_list.append(
                ItemContainer(
                    s_key,
                    keys,
                    self.calculator.getSpaceGroupSymbol,
                    self.calculator.updateSpacegroup,
                )
            )
        # Interface with Site and legacy Site.
        elif issubclass(t_, Site) or issubclass(t_, Site_base):
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
        # Now do anisotropic ADP
        elif issubclass(t_, Anisotropic_base):
            pars = model.get_parameters()
            adp_pars = {par.name: par.raw_value for par in pars}
            ref_name = self.calculator.attachADP(model_key, adp_pars)
            r_list.append(
                ItemContainer(
                    ref_name,
                    {par.name: par.name for par in pars},
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        # Interface with the phase object
        elif issubclass(t_, Phase):
            ident = str(model_key) + "_phase"
            self.calculator.createPhase(ident)
            _ = self.calculator.createEmptyCrystal(model.name, key=model_key)
            self.calculator.assignCell_toCrystal(self._identify(model.cell), model_key)
            self.calculator.assignSpaceGroup_toCrystal(
                self._identify(model._spacegroup), model_key
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
                self.calculator.assignAtom_toCrystal(self._identify(atom), model_key)
        # Interface with the Phases object
        elif issubclass(t_, Phases) and len(model) > 0:
            for phase in model:
                ident = self._identify(phase, as_str=True) + "_phase"
                self.calculator.assignPhase(model_key, ident)

        return r_list

    def link_atom(self, crystal_obj: Phase, atom: Union[Site, Site_base]) -> None:
        """
        Link the atom to the crystal.
        """
        crystal_name = self._identify(crystal_obj)
        self.calculator.assignAtom_toCrystal(self._identify(atom), crystal_name)

    def remove_atom(self, crystal_obj: Phase, atom: Union[Site, Site_base]) -> None:
        """
        Remove the atom from the crystal.
        """
        crystal_name = self._identify(crystal_obj)
        self.calculator.removeAtom_fromCrystal(self._identify(atom), crystal_name)

    def add_phase(self, phases_obj: Phases, phase_obj: Phase) -> None:
        """
        Add a phase to the phases object.
        """
        ident = self._identify(phase_obj, as_str=True) + "_phase"
        self.calculator.assignPhase(self._identify(phases_obj), ident)
        self.calculator.setPhaseScale(
            self._identify(phase_obj), scale=phase_obj.scale.raw_value
        )

    def remove_phase(self, phases_obj: Phases, phase_obj: Phase) -> None:
        """
        Remove a phase from the phases object.
        """
        ident = self._identify(phase_obj, as_str=True) + "_phase"
        self.calculator.removePhase(self._identify(phases_obj), ident)

    def get_hkl(
        self,
        x_array: np.ndarray = None,
        idx: Optional[int] = None,
        phase_name: Optional[str] = None,
        encoded_name: bool = False,
    ) -> dict:
        """
        Get all the hkl values for a phase as specified by EITHER the index or phase name/encoded phase name (obj_id).
        """
        return self.calculator.get_hkl(idx, phase_name, encoded_name)

    def get_component(self, component_name):
        return self.calculator.get_component(component_name)

    def get_phase_components(self, phase_name: str) -> dict:
        """
        Get all the components of a phase as specified by the phase name.
        """
        data = self.calculator.get_phase_components(phase_name)
        return data

    def _createModel(self, model_key: str, model_type: str) -> None:
        self.calculator.createModel(model_type)

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        return self.calculator.get_calculated_y_for_phase(phase_idx)

    def get_total_y_for_phases(self) -> tuple[ndarray, ndarray]:
        return self.calculator.get_total_y_for_phases()

    @staticmethod
    def _identify(obj: B, as_str: bool = False) -> Union[int, str]:
        """
        Helper function to identify objects.
        """
        if hasattr(obj, "unique_name"):
            obj_id = obj.unique_name
        else:
            obj_id = None
        return obj_id



class Powder(Powder_type):
    """
    Class to handle powder calculations. In this instance Powder1DParameters is passed to the calculator.
    """

    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)

        if issubclass(t_, Powder1DParameters):
            # These parameters do not link directly to cryspy objects.
            self.calculator.pattern = model
        return r_list


class SingleCrystal(SingleCrystal_type):
    """
    Class to handle single crystal calculations. At the moment this is a stub/placeholder.
    """

    pass


class CW(CW_type):
    """
    Class to handle Constant Wavelength calculations.
    """

    _instrument_link = {
        "wavelength": "wavelength",
        "resolution_u": "u",
        "resolution_v": "v",
        "resolution_w": "w",
        "resolution_x": "x",
        "resolution_y": "y",
        "reflex_asymmetry_p1": "p1",
        "reflex_asymmetry_p2": "p2",
        "reflex_asymmetry_p3": "p3",
        "reflex_asymmetry_p4": "p4"
    }

    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        #model_key = self._identify(model)

        # Link the Instrumental parameters to the calculator.
        if issubclass(t_, Instrument1DCWParameters):
            # self.calculator.createModel(model_key, "powder1DCW")

            # These parameters are linked to the Resolution, Peak Asymmetry and Setup cryspy objects
            res_key = self.calculator.createResolution()
            asymm_key = self.calculator.createReflexAsymmetry()
            setup_key = self.calculator.createSetup()

            keys = self._instrument_link.copy()
            res_keys = {k: v for k, v in keys.items() if 'resolution' in k}
            asymm_keys = {k: v for k, v in keys.items() if 'reflex_asymmetry' in k}
            setup_keys = {k: v for k, v in keys.items() if 'wavelength' in k}
            self.calculator.parameters = model
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
                    asymm_key,
                    asymm_keys,
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
            self.calculator.createModel("powder1DCW")
        return r_list


class TOF(TOF_type):
    """
    Class to handle Time of Flight calculations.
    """

    _instrument_tof_link = {k: k for k in Instrument1DTOFParameters._defaults.keys()}

    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        #model_key = self._identify(model)

        if issubclass(t_, Instrument1DTOFParameters):
            self.calculator.createModel("powder1DTOF")
            # These parameters are linked to the Resolution and Setup cryspy objects
            res_key = self.calculator.createResolution(cls_type="powder1DTOF")
            setup_key = self.calculator.createSetup(cls_type="powder1DTOF")
            keys = self._instrument_tof_link.copy()
            self.calculator.parameters = model
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


class POL(Pol_type):
    """
    Class to handle calculations with Polarization.
    """

    _polarization_link = {
        "polarization": "polarization",
        "efficiency": "efficiency",
    }

    _field_link = {"magnetic_field": "field"}

    _chi2_link = {
        "sum": "sum",
        "diff": "diff",
        "up": "up",
        "down": "down",
    }

    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)

        # Link the Polarization parameters to the calculator.
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
            p_key = self.calculator.createChi2()
            r_list.append(
                ItemContainer(
                    p_key,
                    self._chi2_link,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        # We have already created a Site in cryspy, now add the MSP
        elif issubclass(t_, Site) or issubclass(t_, Site_base):
            if not hasattr(model, "msp"):
                return r_list
            msp_type = model.msp.msp_type.raw_value
            pars = model.msp.get_parameters()
            msp_pars = {par.name: par.raw_value for par in pars}
            ref_name = self.calculator.attachMSP(model_key, msp_type, msp_pars)
            r_list.append(
                ItemContainer(
                    ref_name,
                    {par.name: par.name for par in pars},
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
        elif issubclass(t_, Powder1DParameters):
            if hasattr(model, "field"):
                r_list.append(
                    ItemContainer(
                        "setup",
                        self._field_link,
                        self.calculator.genericReturn,
                        self.calculator.genericUpdate,
                    )
                )
        return r_list

    @staticmethod
    def up_plus_down(up: np.ndarray, down: np.ndarray) -> np.ndarray:
        """
        Calculate the `up + down` polarization from the up and down polarization.
        :param up: Spin UP
        :param down: Spin DOWN
        :return: Spin UP + Spin DOWN
        """
        return up + down

    @staticmethod
    def up_minus_down(up: np.ndarray, down: np.ndarray) -> np.ndarray:
        """
        Calculate the `up - down` polarization from the up and down polarization.
        :param up: Spin UP
        :param down: Spin DOWN
        :return: Spin UP - Spin DOWN
        """
        return up - down

    @staticmethod
    def up(up: np.ndarray, down: np.ndarray) -> np.ndarray:
        """
        Calculate the `up` polarization from the up and down polarization.
        :param up: Spin UP
        :param down: Spin DOWN
        :return: Spin UP
        """
        return up

    @staticmethod
    def down(up: np.ndarray, down: np.ndarray) -> np.ndarray:
        """
        Calculate the `down` polarization from the up and down polarization.
        :param up: Spin UP
        :param down: Spin DOWN
        :return: Spin DOWN
        """
        return down

    def fit_func(
        self,
        x_array: np.ndarray,
        pol_fn: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        In this case we need to know how to deal with the polarization channels.
        :param pol_fn: How to combine the two chanels
        :param x_array: points to be calculated at
        :return: calculated points
        """
        if pol_fn is None:
            pol_fn = self.up_plus_down
        return self.calculator.calculate(x_array, pol_fn=pol_fn, **kwargs)

    def full_callback(
        self,
        x_array: np.ndarray,
        pol_fn: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Calculate the polarization components.
        :param x_array: points to be calculated at
        :return: calculated points
        """
        if pol_fn is None:
            pol_fn = self.up_plus_down
        return self.calculator.full_calculate(x_array, pol_fn=pol_fn, **kwargs)


class UPol(UPol_type):
    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        return r_list

    def fit_func(self, x_array: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Function to perform a fit.
        :param x_array: points to be calculated at
        :return: calculated points
        """
        return self.calculator.calculate(x_array, *args, **kwargs)

    def full_callback(self, x_array: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Function to perform a fit.
        :param x_array: points to be calculated at
        :return: calculated points
        """
        return self.calculator.full_calculate(x_array, *args, **kwargs)


@interfaceMixInMeta
class CryspyCW(CryspyBase, CW, Powder, UPol):
    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = "powder1DCW"
        if t_.__name__ == "Sample" or t_.__name__ in [
            "Powder1DCW",
            "powder1DCW",
            "Npowder1DCW",
        ]:
            self._createModel(model_key, base)
        return r_list


@interfaceMixInMeta
class CryspyTOF(CryspyBase, TOF, Powder, UPol):
    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = "powder1DTOF"
        if t_.__name__ == "Sample" or t_.__name__ in [
            "Powder1DTOF",
            "powder1DTOF",
            "Npowder1DTOF",
        ]:
            self._createModel(model_key, base)
        return r_list


@interfaceMixInMeta
class CryspyCWPol(CryspyBase, CW, Powder, POL):
    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = "powder1DCWpol"
        if t_.__name__ == "Sample" or t_.__name__ in [
            "PolPowder1DCW",
            "Powder1DCWpol",
            "powder1DCWpol",
            "Npowder1DCWpol",
        ]:
            p_key = self.calculator.createPolarization()
            r_list.append(
                ItemContainer(
                    p_key,
                    self._polarization_link,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
            p_key = self.calculator.createChi2()
            r_list.append(
                ItemContainer(
                    p_key,
                    self._chi2_link,
                    self.calculator.genericReturn,
                    self.calculator.genericUpdate,
                )
            )
            self._createModel(model_key, base)
        return r_list


@interfaceMixInMeta
class CryspyTOFPol(CryspyBase, TOF, Powder, POL):
    def create(self, model: B) -> List[ItemContainer]:
        r_list = []
        t_ = type(model)
        model_key = self._identify(model)
        base = "powder1DTOFpol"
        if t_.__name__ == "Sample" or t_.__name__ in [
            "Powder1DTOFpol",
            "powder1DTOFpol",
            "Npowder1DTOFpol",
        ]:
            self._createModel(model_key, base)
        return r_list


##
## This is the main class which is called, implementing one of the above classes.
##
class CryspyWrapper(WrapperBase):
    name = "CrysPy"

    feature_available = {
        "Npowder1DCWunp": True,
        "Npowder1DTOFunp": True,
        "Npowder1DCWpol": True,
    }

    def __init__(self):
        self.calculator = Cryspy_calc()
        self._internal = None
        self._last_callback = {}

    @staticmethod
    def feature_checker(
        radiation="N",
        exp_type="CW",
        sample_type="powder",
        dimensionality="1D",
        polarization="unp",
        test_str=None,
    ):
        return WrapperBase.features(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            polarization=polarization,
            test_str=test_str,
            FEATURES=CryspyWrapper.feature_available,
        )

    def create(self, model: B):
        cls = self._get_constructor(CryspyBase._subsets, model)
        if cls is not None and cls is not self._internal.__class__:
            self._internal = cls(calculator=self.calculator)
        if self._internal is not None:
            return self._internal.create(model)
        return []

    def __call__(self, *args, **kwargs) -> np.ndarray:
        return self.fit_func(*args, **kwargs)

    def link_atom(self, phase: Phase, atom: Union[Site, Site_base]) -> None:
        if self._internal is not None:
            self._internal.link_atom(phase, atom)

    def add_phase(self, phases_obj, phase_obj: Phase) -> None:
        if self._internal is not None:
            self._internal.add_phase(phases_obj, phase_obj)

    def remove_atom(self, phase: Phase, atom: Union[Site, Site_base]) -> None:
        if self._internal is not None:
            self._internal.remove_atom(phase, atom)

    def remove_phase(self, phases_obj, phase_obj: Phase) -> None:
        if self._internal is not None:
            self._internal.remove_phase(phases_obj, phase_obj)

    def fit_func(self, x_array: np.ndarray, *args, **kwargs) -> Union[np.ndarray, None]:
        if self._internal is not None:
            calculation, self._last_callback = self._internal.full_callback(
                x_array, *args, **kwargs
            )
            return calculation

    def set_exp_cif(self, cif: str) -> None:
        self.calculator.set_exp_cif(cif)

    def set_job_type(self, tof: bool, pol:bool) -> None:
        self.calculator.set_job_type(tof, pol)

    def generate_pol_fit_func(
        self,
        x_array: np.ndarray,
        spin_up: np.ndarray,
        spin_down: np.ndarray,
        components: List[Callable],
    ) -> Callable:
        num_components = len(components)
        dummy_x = np.repeat(x_array[..., np.newaxis], num_components, axis=x_array.ndim)
        calculated_y = np.array(
            [fun(spin_up, spin_down) for fun in components]
        ).swapaxes(0, x_array.ndim)

        def pol_fit_fuction(dummy_x: np.ndarray, **kwargs) -> np.ndarray:
            results, results_dict = self.calculator.full_calculate(
                x_array, pol_fn=components[0], **kwargs
            )
            phases = list(results_dict["phases"].keys())[0]
            up, down = (
                results_dict["phases"][phases]["components"]["up"],
                results_dict["phases"][phases]["components"]["down"],
            )
            bg = results_dict["f_background"]
            sim_y = np.array(
                [fun(up, down) + fun(bg, bg) for fun in components]
            ).swapaxes(0, x_array.ndim)
            return sim_y.flatten()

        return dummy_x.flatten(), calculated_y.flatten(), pol_fit_fuction

    def get_hkl(
        self,
        x_array: np.ndarray = None,
        idx: Optional[int] = None,
        phase_name=None,
        encoded_name=False,
    ) -> dict:
        if self._internal is not None:
            return self._internal.get_hkl(x_array, idx, phase_name, encoded_name)

    def get_calculated_y_for_phase(self, idx: Optional[int] = None) -> list:
        if self._internal is not None:
            return self._internal.get_calculated_y_for_phase(idx)

    def get_total_y_for_phases(self) -> list:
        if self._internal is not None:
            return self._internal.get_total_y_for_phases()

    def get_component(self, component_name):
        if self._internal is not None:
            return self._internal.get_component(component_name)

    def get_phase_components(self, phase_name: str) -> dict:
        """
        Get all the components of a phase as specified by the phase name.
        """
        if self._internal is not None:
            data = self._internal.get_phase_components(phase_name)
            return data

    def updateModelCif(self, cif_string: str) -> None:
        self.calculator.updateModelCif(cif_string)

    def updateExpCif(self, cif_string: str, model_names: list) -> None:
        self.calculator.updateExpCif(cif_string, model_names)

    def replaceExpCif(self, cif_string: str, exp_name: str) -> None:
        self.calculator.replaceExpCif(cif_string, exp_name)

    def full_callback(
        self,
        x_array: np.ndarray,
        pol_fn: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Calculate the polarization components.
        :param x_array: points to be calculated at
        :return: calculated points
        """
        # if pol_fn is None:
        #     pol_fn = self.up_plus_down
        result = None
        if self.calculator is not None:
            result = self.calculator.full_calculate(x_array, pol_fn=pol_fn, **kwargs)
        return result

    def calculate_profile(self):
        results = self.calculator.calculate_profile()
        return results

    def data(self):
        return self.calculator._cryspyData
