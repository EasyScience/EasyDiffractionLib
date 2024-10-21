# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

from typing import Callable
from typing import List

import numpy as np
from easycrystallography.Components.Site import Site as Site_base
from easyscience import global_object as borg
from easyscience.Objects.Inferface import ItemContainer

from easydiffraction import Lattice
from easydiffraction import Phase
from easydiffraction import Phases
from easydiffraction import Site
from easydiffraction import SpaceGroup
from easydiffraction.calculators.cryspy import Cryspy as Cryspy_calc
from easydiffraction.components.polarization import PolarizedBeam
from easydiffraction.Interfaces.interfaceTemplate import InterfaceTemplate
from easydiffraction.Profiles.P1D import Instrument1DCWParameters
from easydiffraction.Profiles.P1D import Instrument1DCWPolParameters
from easydiffraction.Profiles.P1D import Instrument1DTOFParameters
from easydiffraction.Profiles.P1D import Powder1DParameters


class Cryspy(InterfaceTemplate):
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
    _polarization_link = {
        "polarization": "polarization",
        "efficiency": "efficiency",
    }
    _chi2_link = {
        "sum": "sum",
        "diff": "diff",
        "up": "up",
        "down": "down",
    }

    _instrument_tof_link = {k: k for k in Instrument1DTOFParameters._defaults.keys()}

    name = "CrysPy"

    saved_kwargs = {}

    feature_available = {
        "Npowder1DCWunp": True,
        "Npowder1DTOFunp": True,
        "Npowder1DCWpol": True,
    }

    def __init__(self):
        self.calculator = Cryspy_calc()

    @staticmethod
    def feature_checker(
        radiation="N",
        exp_type="CW",
        sample_type="powder",
        dimensionality="1D",
        polarization="unp",
        test_str=None,
    ):
        return InterfaceTemplate.features(
            radiation=radiation,
            exp_type=exp_type,
            sample_type=sample_type,
            dimensionality=dimensionality,
            polarization=polarization,
            test_str=test_str,
            FEATURES=Cryspy.feature_available,
        )

    def create(self, model):
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Instrument1DCWParameters):
            self.calculator.createModel(model_key, "powder1DCW")

            # These parameters are linked to the Resolution, Peak Asymmetry and Setup cryspy objects
            res_key = self.calculator.createResolution()
            asymm_key = self.calculator.createReflexAsymmetry()
            setup_key = self.calculator.createSetup()

            keys = self._instrument_link.copy()
            res_keys = {k: v for k, v in keys.items() if 'resolution' in k}
            asymm_keys = {k: v for k, v in keys.items() if 'reflex_asymmetry' in k}
            setup_keys = {k: v for k, v in keys.items() if 'wavelength' in k}

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
        elif issubclass(t_, Powder1DParameters):
            # These parameters do not link directly to cryspy objects.
            self.calculator.pattern = model
            if hasattr(model, "field"):
                r_list.append(
                    ItemContainer(
                        "setup",
                        {"magnetic_field": "field"},
                        self.calculator.genericReturn,
                        self.calculator.genericUpdate,
                    )
                )
                self.calculator.polarized = True
        elif issubclass(t_, PolarizedBeam):
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
        elif issubclass(t_, Lattice):
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
            if hasattr(model, "msp"):
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
        elif issubclass(t_, Phase):
            ident = str(model_key) + "_phase"
            self.calculator.createPhase(ident)
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
        elif t_.__name__ in ["Powder1DCW", "powder1DCW", "Npowder1DCW"]:
            #     #TODO Check to see if parameters and pattern should be initialized here.
            self.__createModel(model_key, "powder1DCW")
        elif t_.__name__ in ["Powder1DTOF", "powder1DTOF", "Npowder1DTOF"]:
            #     #TODO Check to see if parameters and pattern should be initialized here.
            self.__createModel(model_key, "powder1DTOF")
        elif t_.__name__ == "Sample":  # This is legacy mode. Boo
            tt_ = type(model.parameters)
            base = "powder1D"

            if issubclass(tt_, Instrument1DCWParameters):
                base += "CW"
            elif issubclass(tt_, Instrument1DTOFParameters):
                base += "TOF"
            else:
                raise AttributeError("Unknown EXP type")
            if issubclass(tt_, Instrument1DCWPolParameters):
                base += "pol"
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
            self.__createModel(model_key, base)

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

    def fit_func(self, x_array: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Function to perform a fit
        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        # apply cryspy kwargs now, since lmfit strips them
        for arg in self.saved_kwargs:
            if arg not in kwargs:
                kwargs[arg] = self.saved_kwargs[arg]

        return self.calculator.calculate(x_array, *args, **kwargs)

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
        self, x_array: np.ndarray = None, idx=None, phase_name=None, encoded_name=False
    ) -> dict:
        return self.calculator.get_hkl(idx, phase_name, encoded_name)

    def get_phase_components(self, phase_name):
        data = self.calculator.get_phase_components(phase_name)
        return data

    def get_component(self, component_name):
        return self.calculator.get_component(component_name)

    def __createModel(self, model, model_type):
        self.calculator.createModel(model, model_type)

    def get_calculated_y_for_phase(self, phase_idx: int) -> list:
        return self.calculator.get_calculated_y_for_phase(phase_idx)

    def get_total_y_for_phases(self) -> list:
        return self.calculator.get_total_y_for_phases()

    @staticmethod
    def __identify(obj):
        return borg.map.convert_id_to_key(obj)
