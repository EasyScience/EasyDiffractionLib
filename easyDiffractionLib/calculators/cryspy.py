__author__ = "github.com/wardsimon"
__version__ = "0.0.3"

import time
from typing import Tuple, Optional, Any, Callable, List, Dict, Union

import cryspy
from cryspy.procedure_rhochi.rhochi_by_dictionary import \
    rhochi_calc_chi_sq_by_dictionary

import warnings

from numpy import ndarray

from easyCore import np, borg

# from pathos import multiprocessing as mp
import functools

warnings.filterwarnings("ignore")

normalization = 1.0


class Cryspy:
    def __init__(self):
        self.pattern = None
        self.conditions = {
            "wavelength": 1.25,
            "resolution": {"u": 0.001, "v": 0.001, "w": 0.001, "x": 0.000, "y": 0.000},
            "reflex_asymmetry": {"p1": 0.0, "p2": 0.0, "p3": 0.0, "p4": 0.0}
        }
        self.conditions_TOF = {
            "ttheta_bank": 0,
            "dtt1": 0.1,
            "dtt2": 0,
            "resolution": {
                "sigma0": 0,
                "sigma1": 0,
                "sigma2": 0,
                "gamma0": 0,
                "gamma1": 0,
                "gamma2": 0,
                "alpha0": 0,
                "alpha1": 0,
                "beta0": 0,
                "beta1": 0,
            },
        }
        self.background = None
        self.storage = {}
        self.current_crystal = {}
        self.model = None
        self.phases = cryspy.PhaseL()
        self.type = "powder1DCW"
        self.additional_data = {"phases": {}}
        self.polarized = False
        self._cryspyInOutDict = {}
        self._cryspyObject = None
        self.experiment_cif = ""
        self._first_experiment_name = ""

    @property
    def cif_str(self) -> str:
        key = list(self.current_crystal.keys())[0]
        return self.storage[key].to_cif()

    @cif_str.setter
    def cif_str(self, value: str):
        self.createCrystal_fromCifStr(value)

    def set_exp_cif(self, value: str):
        print("\nset_exp_cif called ****")
        if value == self.experiment_cif:
            return
        self.experiment_cif = value
        exp_obj = cryspy.str_to_globaln(self.experiment_cif)
        if self._cryspyObject is None:
            self._cryspyObject = cryspy.str_to_globaln(self.cif_str)
        self._cryspyObject.items.append(exp_obj.items[0])

        self._cryspyDict = self._cryspyObject.get_dictionary()
        self._edDict = createEdDict(self._cryspyObject, self._cryspyDict)
        print("\ncryspyDict: ", list(self._cryspyDict.keys()))
        print("\nedDict: ", list(self._edDict.keys()))
        self._first_experiment_name = list(self._edDict['experiments'][0].keys())[0]
        print("\nExperiment name: ", self._first_experiment_name)

    def createModel(self, model_id: str, model_type: str = "powder1DCW"):
        model = {"background": cryspy.PdBackgroundL(), "phase": self.phases}
        self.polarized = False
        if model_type.endswith("pol"):
            self.polarized = True
            model_type = model_type.split("pol")[0]
        cls = cryspy.Pd
        if model_type == "powder1DTOF":
            cls = cryspy.TOF
            model["background"] = cryspy.TOFBackground()
        self.type = model_type
        self.model = cls(**model)

    def createPhase(self, crystal_name: str, key: str = "phase") -> str:
        phase = cryspy.Phase(label=crystal_name, scale=1, igsize=0)
        self.storage[key] = phase
        return key

    def assignPhase(self, model_name: str, phase_name: str):
        print("\nAssignPhase called ****")
        phase = self.storage[phase_name]
        self.phases.items.append(phase)
        #self._cryspyObject = cryspy.str_to_globaln(self.cif_str)

        #self._cryspyDict = self._cryspyObject.get_dictionary()
        #self._edDict = createEdDict(self._cryspyObject, self._cryspyDict)

    def removePhase(self, model_name: str, phase_name: str):
        phase = self.storage[phase_name]
        del self.storage[phase_name]
        del self.storage[phase_name.split("_")[0] + "_scale"]
        self.phases.items.pop(self.phases.items.index(phase))
        name = self.current_crystal.pop(int(phase_name.split("_")[0]))
        if name in self.additional_data["phases"].keys():
            del self.additional_data["phases"][name]

    def setPhaseScale(self, model_name: str, scale: float = 1.0):
        self.storage[str(model_name) + "_scale"] = scale

    def getPhaseScale(self, model_name: str, *args, **kwargs) -> float:
        return self.storage.get(str(model_name) + "_scale", 1.0)

    def createCrystal_fromCifStr(self, cif_str: str) -> str:
        crystal = cryspy.Crystal.from_cif(cif_str)
        key = crystal.data_name
        self.storage[key] = crystal
        self.current_crystal[key] = key
        self.createPhase(key)
        return key

    def createEmptyCrystal(self, crystal_name: str, key: Optional[str] = None) -> str:
        crystal = cryspy.Crystal(crystal_name, atom_site=cryspy.AtomSiteL())
        if key is None:
            key = crystal_name
        self.storage[key] = crystal
        self.createPhase(crystal_name, key=str(key) + "_phase")
        self.current_crystal[key] = crystal_name
        return key

    def createCell(self, key: str = "cell") -> str:
        cell = cryspy.Cell()
        self.storage[key] = cell
        return key

    def assignCell_toCrystal(self, cell_name: str, crystal_name: str):
        crystal = self.storage[crystal_name]
        cell = self.storage[cell_name]
        crystal.cell = cell

    def createSpaceGroup(
        self, key: str = "spacegroup", name_hm_alt: str = "P 1"
    ) -> str:
        sg_split = name_hm_alt.split(":")
        opts = {"name_hm_alt": sg_split[0]}
        if len(sg_split) > 1:
            opts["it_coordinate_system_code"] = sg_split[1]
        try:
            sg = cryspy.SpaceGroup(**opts)
        except Exception as e:
            print(e)
            sg = cryspy.SpaceGroup(**{"name_hm_alt": sg_split[0]})
        self.storage[key] = sg
        return key

    def getSpaceGroupSymbol(self, spacegroup_name: str, *args, **kwargs) -> str:
        sg = self.storage[spacegroup_name]
        hm_alt = getattr(sg, "name_hm_alt")
        setting = getattr(sg, "it_coordinate_system_code")
        if setting:
            hm_alt += ":" + setting
        return hm_alt

    def assignSpaceGroup_toCrystal(self, spacegroup_name: str, crystal_name: str):
        if not crystal_name:
            return
        crystal = self.storage[crystal_name]
        space_group: cryspy.SpaceGroup = self.storage[spacegroup_name]
        setattr(crystal, "space_group", space_group)
        for atom in crystal.atom_site.items:
            atom.define_space_group_wyckoff(space_group.space_group_wyckoff)
            atom.form_object()

    def updateSpacegroup(self, sg_key: str, **kwargs):
        # This has to be done as sg.name_hm_alt = 'blah' doesn't work :-(
        keys = list(self.current_crystal.keys())
        previous_key = ""
        for key in keys:
            if key in self.storage.keys():
                previous_sg = getattr(self.storage[key], "space_group", None)
                if previous_sg == self.storage[sg_key]:
                    previous_key = key
                    break
        sg_key = self.createSpaceGroup(key=sg_key, **kwargs)
        self.assignSpaceGroup_toCrystal(sg_key, previous_key)

    def createAtom(self, atom_name: str, **kwargs) -> str:
        atom = cryspy.AtomSite(**kwargs)
        self.storage[atom_name] = atom
        return atom_name

    def attachMSP(self, atom_name: str, msp_name: str, msp_args: Dict[str, float]):
        atom = self.storage[atom_name]
        msp = cryspy.AtomSiteSusceptibility(chi_type=msp_name, **msp_args)
        ref_name = str(atom_name) + "_" + msp_name
        self.storage[ref_name] = msp
        return ref_name

    def assignAtom_toCrystal(self, atom_label: str, crystal_name: str):
        crystal = self.storage[crystal_name]
        atom = self.storage[atom_label]
        wyckoff = crystal.space_group.space_group_wyckoff
        atom.define_space_group_wyckoff(wyckoff)
        atom.form_object()
        for item in crystal.items:
            if not isinstance(item, cryspy.AtomSiteL):
                continue
            item.items.append(atom)

    def removeAtom_fromCrystal(self, atom_label: str, crystal_name: str):
        crystal = self.storage[crystal_name]
        atom = self.storage[atom_label]
        for item in crystal.items:
            if not isinstance(item, cryspy.AtomSiteL):
                continue
            idx = item.items.index(atom)
            del item.items[idx]

    def createBackground(self, background_obj) -> str:
        key = "background"
        self.storage[key] = background_obj
        return key

    def createSetup(self, key: str = "setup", cls_type: Optional[str] = None):

        if cls_type is None:
            cls_type = self.type

        if cls_type == "powder1DCW":
            setup = cryspy.Setup(
                wavelength=self.conditions["wavelength"], offset_ttheta=0, field=0
            )
        elif cls_type == "powder1DTOF":
            setup = cryspy.TOFParameters(
                zero=0,
                dtt1=self.conditions_TOF["dtt1"],
                dtt2=self.conditions_TOF["dtt2"],
                ttheta_bank=self.conditions_TOF["ttheta_bank"],
            )
        else:
            raise AttributeError("The experiment is of an unknown type")
        self.storage[key] = setup
        if self.model is not None:
            setattr(self.model, "setup", setup)
        return key

    def genericUpdate(self, item_key: str, **kwargs):
        item = self.storage[item_key]
        for key, value in kwargs.items():
            setattr(item, key, kwargs[key])

    def genericReturn(self, item_key: str, value_key: str) -> Any:
        item = self.storage[item_key]
        value = getattr(item, value_key)
        return value

    def createPolarization(self, key: str = "polarized_beam") -> str:
        item = cryspy.DiffrnRadiation()
        self.storage[key] = item
        return key

    def createChi2(self, key: str = "chi2") -> str:
        item = cryspy.Chi2()

        # test
        item.sum = False
        item.diff = False
        item.up = True
        item.down = True

        self.storage[key] = item
        return key

    def createResolution(self, cls_type: Optional[str] = None) -> str:

        if cls_type is None:
            cls_type = self.type

        if cls_type == "powder1DCW":
            key = "pd_instr_resolution"
            resolution = cryspy.PdInstrResolution(**self.conditions["resolution"])
        elif cls_type == "powder1DTOF":
            key = "tof_profile"
            resolution = cryspy.TOFProfile(**self.conditions_TOF["resolution"])
            resolution.peak_shape = "Gauss"
        else:
            raise AttributeError("The experiment is of an unknown type")
        self.storage[key] = resolution
        if self.model is not None:
            setattr(self.model, key, resolution)
        return key

    def updateResolution(self, key: str, **kwargs):
        resolution = self.storage[key]
        for r_key in kwargs.keys():
            setattr(resolution, r_key, kwargs[key])

    def createReflexAsymmetry(self) -> str:
        key = "pd_instr_reflex_asymmetry"
        reflex_asymmetry = cryspy.PdInstrReflexAsymmetry(**self.conditions["reflex_asymmetry"])
        self.storage[key] = reflex_asymmetry
        if self.model is not None:
            setattr(self.model, key, reflex_asymmetry)
        return key

    def updateReflexAsymmetry(self, key: str, **kwargs):
        reflex_asymmetry = self.storage[key]
        for r_key in kwargs.keys():
            setattr(reflex_asymmetry, r_key, kwargs[key])

    def powder_1d_calculate(
        self, x_array: np.ndarray, full_return: bool = False, **kwargs
    ):

        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        pol_fn = None
        for key_inner in ["pd_instr_resolution", "setup"]:
            if not hasattr(self.model, key_inner):
                setattr(self.model, key_inner, self.storage[key_inner])

        if self.polarized:
            if "pol_fn" in kwargs.keys():
                pol_fn = kwargs["pol_fn"]
            if not hasattr(self.model, "diffrn_radiation"):
                setattr(self.model, "diffrn_radiation", self.storage["polarized_beam"])
            if not hasattr(self.model, "chi2"):
                setattr(self.model, "chi2", self.storage["chi2"])
            if "pol_refinement" in kwargs:
                self.model.chi2.sum = kwargs["pol_refinement"]["sum"]
                self.model.chi2.diff = kwargs["pol_refinement"]["diff"]
                self.model.chi2.up = kwargs["pol_refinement"]["up"]
                self.model.chi2.down = kwargs["pol_refinement"]["down"]

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value / normalization
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array + offset

        if borg.debug:
            print("CALLING FROM Cryspy\n----------------------")

        results, additional = self.do_calc_setup(scale, this_x_array, pol_fn)
        if full_return:
            return results, additional
        return results

    def powder_1d_tof_calculate(
        self, x_array: np.ndarray, pol_fn=None, full_return: bool = False
    ):
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        setup, tof_profile, phase, tof_background, tof_meas
        """

        for key_inner in ["tof_profile", "setup"]:
            if not hasattr(self.model, key_inner):
                try:
                    setattr(self.model, key_inner, self.storage[key_inner])
                except ValueError:
                    # Try to fix cryspy....
                    s = self.storage[key_inner]
                    cls = s.__class__
                    for idx, item in enumerate(self.model.items):
                        if isinstance(item, cls) and id(item) is not id(s):
                            self.model.items[idx] = s
                            break

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value / normalization
            offset = self.pattern.zero_shift.raw_value

        self.model["tof_parameters"].zero = offset
        this_x_array = x_array

        if borg.debug:
            print("CALLING FROM Cryspy\n----------------------")
        results, additional = self.do_calc_setup(scale, this_x_array, pol_fn)
        if full_return:
            return results, additional
        return results

    def do_calc_setup(
        self, scale: float, this_x_array: np.ndarray, pol_fn: Callable
    ) -> Tuple[np.ndarray, dict]:
        if len(self.pattern.backgrounds) == 0:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.pattern.backgrounds[0].calculate(this_x_array)
        new_bg = bg

        num_crys = len(self.current_crystal.keys())

        if num_crys == 0:
            return bg

        crystals = [self.storage[key] for key in self.current_crystal.keys()]
        phase_scales = [
            self.storage[str(key) + "_scale"] for key in self.current_crystal.keys()
        ]
        phase_lists = []
        profiles = []
        peak_dat = []
        storage_invert = {v: k for k, v in self.storage.items()}
        for crystal in crystals:
            phasesL = cryspy.PhaseL()
            atoms = crystal.atom_site
            pol_atoms = []
            ass = []
            for atom in atoms:
                i = None
                l = str(storage_invert[atom]) + "_Cani"
                if l in self.storage.keys():
                    i = self.storage[l]
                l = str(storage_invert[atom]) + "_Ciso"
                if l in self.storage.keys():
                    i = self.storage[l]
                if i is not None:
                    i.label = atom.label
                    pol_atoms.append(i)
                    ii = cryspy.AtomSiteScat()
                    ii.label = atom.label
                    ass.append(ii)
            if pol_atoms:
                asl = cryspy.AtomSiteSusceptibilityL()
                asl.items = pol_atoms
                sl = cryspy.AtomSiteScatL()
                sl.items = ass
                setattr(crystal, "atom_site_susceptibility", asl)
                setattr(crystal, "atom_site_scat", sl)
            else:
                if hasattr(crystal, "atom_site_susceptibility"):
                    delattr(crystal, "atom_site_susceptibility")
                if hasattr(crystal, "atom_site_scat"):
                    delattr(crystal, "atom_site_scat")
            idx = [
                idx
                for idx, item in enumerate(self.phases.items)
                if item.label == crystal.data_name
            ][0]
            phasesL.items.append(self.phases.items[idx])
            phase_lists.append(phasesL)
            profile, peak = self._do_run(
                self.model, self.polarized, this_x_array, crystal, phasesL
            )
            profiles.append(profile)
            peak_dat.append(peak)
        # pool = mp.ProcessPool(num_crys)
        # print("\n\nPOOL = " + str(pool))
        # result = pool.amap(functools.partial(_do_run, self.model, self.polarized, this_x_array), crystals,
        # phase_lists)
        # while not result.ready():
        #     time.sleep(0.01)
        # obtained = result.get()
        # profiles, peak_dat = zip(*obtained)
        # else:
        #     raise ArithmeticError

        # Do this for now
        x_str = "ttheta"
        if self.type == "powder1DTOF":
            x_str = "time"
        if self.polarized:
            # TODO *REPLACE PLACEHOLDER FN*
            dependents, additional_data = self.polarized_update(
                pol_fn,
                crystals,
                profiles,
                peak_dat,
                phase_scales,
                x_str,
            )

            new_bg = pol_fn(bg, bg)  # Scale the bg for the components requested
        else:
            dependents, additional_data = self.nonPolarized_update(
                crystals, profiles, peak_dat, phase_scales, x_str
            )
        self.additional_data["phases"].update(additional_data)
        self.additional_data["global_scale"] = scale
        self.additional_data["background"] = new_bg
        self.additional_data["f_background"] = bg
        self.additional_data["ivar_run"] = this_x_array
        self.additional_data["phase_names"] = list(additional_data.keys())
        self.additional_data["type"] = self.type

        scaled_dependents = [scale * dep / normalization for dep in dependents]
        self.additional_data["components"] = scaled_dependents

        total_profile = (
            np.sum(
                [s["profile"] for s in self.additional_data["phases"].values()], axis=0
            )
            + new_bg
        )

        return total_profile, self.additional_data

    def calculate(self, x_array: np.ndarray, **kwargs) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        res = np.zeros_like(x_array)
        self.additional_data["ivar"] = res
        args = x_array
        if self.type == "powder1DCW":
            return self.powder_1d_calculate(args, **kwargs)
        if self.type == "powder1DTOF":
            return self.powder_1d_tof_calculate(args, **kwargs)
        return res

    def full_calculate(self, x_array: np.ndarray, **kwargs) -> Tuple[np.ndarray, dict]:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        res = np.zeros_like(x_array)
        self.additional_data["ivar"] = res
        args = x_array
        if self.type == "powder1DCW":
            return self.powder_1d_calculate(args, full_return=True, **kwargs)
        if self.type == "powder1DTOF":
            return self.powder_1d_tof_calculate(args, full_return=True, **kwargs)
        return res, dict()

    def get_phase_components(self, phase_name: str) -> List[np.ndarray]:
        data = None
        if phase_name in self.additional_data["phase_names"]:
            data = self.additional_data["phases"][phase_name].copy()
        return data

    def get_calculated_y_for_phase(self, phase_idx: int) -> List[np.ndarray]:
        """
        For a given phase index, return the calculated y
        :param phase_idx: index of the phase
        :type phase_idx: int
        :return: calculated y
        :rtype: np.ndarray
        """
        if phase_idx > len(self.additional_data["components"]):
            raise KeyError(f"phase_index incorrect: {phase_idx}")
        return list(self.additional_data["phases"].values())[phase_idx]["profile"]

    def get_total_y_for_phases(self) -> Tuple[np.ndarray, np.ndarray]:
        x_values = self.additional_data["ivar_run"]
        y_values = (
            np.sum(
                [s["profile"] for s in self.additional_data["phases"].values()], axis=0
            )
            + self.additional_data["background"]
        )
        return x_values, y_values

    def get_hkl(
        self, idx: int = 0, phase_name: Optional[str] = None, encoded_name: bool = False
    ) -> dict:
        # Collate and return
        if phase_name is not None:
            if encoded_name:
                known_phases = [str(key) for key in self.current_crystal.keys()]
                idx = known_phases.index(phase_name)
                phase_name = list(self.current_crystal.values())[idx]
            else:
                known_phases = list(self.current_crystal.values())
                phase_name = known_phases[idx]
        else:
            phase_name = list(self.current_crystal.values())[idx]
        return self.additional_data["phases"][phase_name]["hkl"]

    def get_component(self, component_name=None) -> Optional[dict]:
        data = None
        if component_name is None:
            data = self.additional_data.copy()
        elif component_name in self.additional_data:
            data = self.additional_data[component_name].copy()
        return data

    @staticmethod
    def nonPolarized_update(crystals, profiles, peak_dat, scales, x_str):
        # dependent = np.array([profile.numpy_intensity for profile in profiles])
        dependent = np.array(profiles)

        output = {}
        for idx, profile in enumerate(profiles):
            output.update(
                {
                    crystals[idx].data_name: {
                        "hkl": {
                            # x_str: getattr(peak_dat[idx], "numpy_" + x_str),
                            # "h": peak_dat[idx].numpy_index_h,
                            # "k": peak_dat[idx].numpy_index_k,
                            # "l": peak_dat[idx].numpy_index_l,
                        },
                        "profile": scales[idx] * dependent[idx, :] / normalization,
                        "components": {"total": dependent[idx, :]},
                        "profile_scale": scales[idx],
                    }
                }
            )
        return dependent, output

    @staticmethod
    def polarized_update(func, crystals, profiles, peak_dat, scales, x_str):
        up = np.array([profile.intensity_plus_net for profile in profiles])
        down = np.array([profile.intensity_minus_net for profile in profiles])
        dependent = np.array([func(u, d) for u, d in zip(up, down)])

        output = {}
        for idx, profile in enumerate(profiles):
            output.update(
                {
                    crystals[idx].data_name: {
                        "hkl": {
                            # x_str: getattr(peak_dat[idx], "numpy_" + x_str),
                            # "h": peak_dat[idx].numpy_index_h,
                            # "k": peak_dat[idx].numpy_index_k,
                            # "l": peak_dat[idx].numpy_index_l,
                        },
                        "profile": scales[idx] * dependent[idx, :] / normalization,
                        "components": {
                            "total": dependent[idx, :],
                            "up": scales[idx] * up[idx, :] / normalization,
                            "down": scales[idx] * down[idx, :] / normalization,
                        },
                        "profile_scale": scales[idx],
                        "func": func,
                    }
                }
            )

        return dependent, output

    def _do_run(self,
    model,
    polarized,
    x_array,
    crystals,
    phase_list,
    ):
        idx = [
            idx for idx, item in enumerate(model.items) if isinstance(item, cryspy.PhaseL)
        ][0]
        model.items[idx] = phase_list
        #result1 = model.calc_profile(
        #    x_array, [crystals], flag_internal=True, flag_polarized=polarized
        #)
        # start = x_array[0]
        # end = x_array[-1]
        # step = (end - start) / (len(x_array) -1)

        # result1 = cryspy.simulation_pd(
        #     [crystals],
        #     start,
        #     end,
        #     step,
        #     flag_polarized=polarized
        # )
        # add pd object to cryspy
        # setattr(self._cryspyObject, "pd", self.model)
        # setattr(self.model, 'data_name', 'pd')
        # excluded_points = np.full(len(x_array), True)
        # setattr(self.model['setup'], 'excluded_points', excluded_points)
        # self._cryspyObject.items.append(self.model)
        # self._cryspyDict = self._cryspyObject.get_dictionary()
        # self._cryspyDict['pd_pd']['excluded_points'] = excluded_points
        # self._cryspyDict['pd_pd']['ttheta'] = x_array
        rhochi_calc_chi_sq_by_dictionary(self._cryspyDict,
                                        dict_in_out=self._cryspyInOutDict,
                                        flag_use_precalculated_data=False,
                                        flag_calc_analytical_derivatives=False)
        print("DONE")
        print(list(self._cryspyDict.keys()))
        print(list(self._cryspyInOutDict.keys()))
        yArray = self._cryspyInOutDict[f'pd_{self._first_experiment_name}']['signal_plus']

        # result2 = model.d_internal_val["peak_" + crystals.data_name]
        result1 = yArray
        result2 = None
        # should we return the whole pd_sim_1d object or just the profile?
        # currently returning profile as 'pd_proc' attribute
        return result1, result2

def createEdDict(cryspy_obj, cryspy_dict):
    phase_names = [name.replace('crystal_', '') for name in cryspy_dict.keys() if name.startswith('crystal_')]
    experiment_names = [name.replace('pd_', '') for name in cryspy_dict.keys() if name.startswith('pd_')]
    if not experiment_names:
        # TOF
        experiment_names = [name.replace('data_', '') for name in cryspy_dict.keys() if name.startswith('data_')]
    ed_dict = {}
    for data_block in cryspy_obj.items:
        data_block_name = data_block.data_name.lower()
        # Phase datablock
        if data_block_name in phase_names:
            ed_dict['phases'] = []
            ed_phase = {data_block_name: {}}
            cryspy_phase = data_block.items
            for item in cryspy_phase:
                # Space group section
                if type(item) == cryspy.C_item_loop_classes.cl_2_space_group.SpaceGroup:
                    ed_phase[data_block_name]['_space_group_name_H-M_alt'] = item.name_hm_alt
                # Cell section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_cell.Cell:
                    ed_phase[data_block_name]['_cell_length_a'] = item.length_a
                    ed_phase[data_block_name]['_cell_length_b'] = item.length_b
                    ed_phase[data_block_name]['_cell_length_c'] = item.length_c
                    ed_phase[data_block_name]['_cell_angle_alpha'] = item.angle_alpha
                    ed_phase[data_block_name]['_cell_angle_beta'] = item.angle_beta
                    ed_phase[data_block_name]['_cell_angle_gamma'] = item.angle_gamma
                # Atoms section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_atom_site.AtomSiteL:
                    ed_atoms = []
                    cryspy_atoms = item.items
                    for cryspy_atom in cryspy_atoms:
                        ed_atom = {}
                        ed_atom['_label'] = cryspy_atom.label
                        ed_atom['_type_symbol'] = cryspy_atom.type_symbol
                        ed_atom['_fract_x'] = cryspy_atom.fract_x
                        ed_atom['_fract_y'] = cryspy_atom.fract_y
                        ed_atom['_fract_z'] = cryspy_atom.fract_z
                        ed_atom['_occupancy'] = cryspy_atom.occupancy
                        ed_atom['_adp_type'] = cryspy_atom.adp_type
                        if hasattr(cryspy_atom, 'b_iso_or_equiv'):
                            ed_atom['_B_iso_or_equiv'] = cryspy_atom.b_iso_or_equiv
                        ed_atom['_multiplicity'] = cryspy_atom.multiplicity
                        ed_atom['_Wyckoff_symbol'] = cryspy_atom.wyckoff_symbol
                        ed_atoms.append(ed_atom)
                    ed_phase[data_block_name]['_atom_site'] = ed_atoms
            ed_dict['phases'].append(ed_phase)
            # Experiment datablock
        if data_block_name in experiment_names:
            ed_dict['experiments'] = []
            ed_experiment = {data_block_name: {}}
            cryspy_experiment = data_block.items
            for item in cryspy_experiment:
                # Ranges section
                if type(item) == cryspy.C_item_loop_classes.cl_1_range.Range:
                    ed_experiment[data_block_name]['_pd_meas_2theta_range_min'] = item.ttheta_min
                    ed_experiment[data_block_name]['_pd_meas_2theta_range_max'] = item.ttheta_max
                    ed_experiment[data_block_name]['_pd_meas_2theta_range_inc'] = 0.05  # NEED FIX
                # Setup section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_setup.Setup:
                    ed_experiment[data_block_name]['_diffrn_radiation_probe'] = item.radiation.replace('neutrons', 'neutron').replace('X-rays', 'x-ray')
                    ed_experiment[data_block_name]['_diffrn_radiation_wavelength'] = item.wavelength
                    ed_experiment[data_block_name]['_pd_meas_2theta_offset'] = item.offset_ttheta
                # Instrument resolution section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_instr_resolution.PdInstrResolution:
                    ed_experiment[data_block_name]['_pd_instr_resolution_u'] = item.u
                    ed_experiment[data_block_name]['_pd_instr_resolution_v'] = item.v
                    ed_experiment[data_block_name]['_pd_instr_resolution_w'] = item.w
                    ed_experiment[data_block_name]['_pd_instr_resolution_x'] = item.x
                    ed_experiment[data_block_name]['_pd_instr_resolution_y'] = item.y
                # Peak assymetries section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_instr_reflex_asymmetry.PdInstrReflexAsymmetry:
                    ed_experiment[data_block_name]['_pd_instr_reflex_asymmetry_p1'] = item.p1
                    ed_experiment[data_block_name]['_pd_instr_reflex_asymmetry_p2'] = item.p2
                    ed_experiment[data_block_name]['_pd_instr_reflex_asymmetry_p3'] = item.p3
                    ed_experiment[data_block_name]['_pd_instr_reflex_asymmetry_p4'] = item.p4
                # Phases section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_phase.PhaseL:
                    ed_phases = []
                    cryspy_phases = item.items
                    for cryspy_phase in cryspy_phases:
                        ed_phase = {}
                        ed_phase['_label'] = cryspy_phase.label
                        ed_phase['_scale'] = cryspy_phase.scale
                        ed_phases.append(ed_phase)
                    ed_experiment[data_block_name]['_phase'] = ed_phases
                # Background section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_background.PdBackgroundL:
                    ed_bkg_points = []
                    cryspy_bkg_points = item.items
                    for cryspy_bkg_point in cryspy_bkg_points:
                        ed_bkg_point = {}
                        ed_bkg_point['_2theta'] = cryspy_bkg_point.ttheta
                        ed_bkg_point['_intensity'] = cryspy_bkg_point.intensity
                        ed_bkg_points.append(ed_bkg_point)
                    ed_experiment[data_block_name]['_pd_background'] = ed_bkg_points
                # Measured data section
                elif type(item) == cryspy.C_item_loop_classes.cl_1_pd_meas.PdMeasL:
                    ed_meas_points = []
                    cryspy_meas_points = item.items
                    for cryspy_meas_point in cryspy_meas_points:
                        ed_meas_point = {}
                        ed_meas_point['_2theta'] = cryspy_meas_point.ttheta
                        ed_meas_point['_intensity'] = cryspy_meas_point.intensity
                        ed_meas_point['_intensity_sigma'] = cryspy_meas_point.intensity_sigma
                        ed_meas_points.append(ed_meas_point)
                    ed_experiment[data_block_name]['_pd_meas'] = ed_meas_points
            ed_dict['experiments'].append(ed_experiment)
    return ed_dict
