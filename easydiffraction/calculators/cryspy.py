# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

import warnings
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import cryspy
import numpy as np
from cryspy.procedure_rhochi.rhochi_by_dictionary import rhochi_calc_chi_sq_by_dictionary
from easyscience import global_object as borg

from easydiffraction.io.cif import cifV2ToV1
from easydiffraction.io.cif import cifV2ToV1_tof
from easydiffraction.io.cryspy_parser import CryspyParser

# from pathos import multiprocessing as mp

warnings.filterwarnings("ignore")

normalization = 0.5

RAD_MAP = {
    'x-ray': 'X-rays',
    'neutron': 'neutrons',
    'neutrons': 'neutrons',
    'neutronss': 'neutrons',
}

CRYSPY_MODEL_INSTR_KEYS = {
    'wavelength': 'wavelength',
    'ttheta': 'offset_ttheta',
    'u': 'resolution_parameters',
    'v': 'resolution_parameters',
    'w': 'resolution_parameters',
    'x': 'resolution_parameters',
    'y': 'resolution_parameters',
    'p1': 'asymmetry_parameters',
    'p2': 'asymmetry_parameters',
    'p3': 'asymmetry_parameters',
    'p4': 'asymmetry_parameters',
}

CRYSPY_MODEL_PHASE_KEYS = {
    'fract_x' : 'atom_fract_xyz',
    'fract_y' : 'atom_fract_xyz',
    'fract_z' : 'atom_fract_xyz',
    'occupancy' : 'atom_occupancy',
    'b_iso_or_equiv' : 'atom_b_iso',
    'length_a': 'unit_cell_parameters',
    'length_b': 'unit_cell_parameters',
    'length_c': 'unit_cell_parameters',
}

CRYSPY_MODEL_COORD_INDEX = {
    'length_a': 0,
    'length_b': 1,
    'length_c': 2,
    'fract_x' : 0,
    'fract_y' : 1,
    'fract_z' : 2,
    'u': 0,
    'v': 1,
    'w': 2,
    'x': 3,
    'y': 4,
    'p1': 0,
    'p2': 1,
    'p3': 2,
    'p4': 3,
}


class Cryspy:
    def __init__(self):
        # temporary cludge before `beta` branch merged properly
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
        self.storage = {} # name -> cryspy object
        self.current_crystal = {}
        self.model = None
        self.phases = cryspy.PhaseL()
        self.type = "powder1DCW"
        self.additional_data = {"phases": {}}
        self.polarized = False
        self._inOutDict = {}
        self._cryspyObject = None
        self.experiment_cif = ""
        self._first_experiment_name = ""
        self.exp_obj = None
        self.chisq = None
        self.excluded_points = []
        self._cryspyData = Data() # {phase_name: CryspyPhase, exp_name: CryspyExperiment}
        self._cryspyObject = self._cryspyData._cryspyObj
        self._counter = 0

    @property
    def cif_str(self, index=0) -> str:
        key = list(self.current_crystal.keys())[index]
        return self.storage[key].to_cif()

    @cif_str.setter
    def cif_str(self, value: str):
        self.createCrystal_fromCifStr(value)

    def set_pattern(self, pattern):
        self.pattern = pattern

    def set_exp_cif(self, value: str):
        if value == self.experiment_cif:
            return
        cryspyCif = cifV2ToV1(value)
        self.experiment_cif = value
        if self._cryspyObject is None:
            self._cryspyObject = cryspy.str_to_globaln(cryspyCif)

    def createModel(self, model_type: str = "powder1DCW"):
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
        phase = self.storage[phase_name]
        self.phases.items.append(phase)

    def removePhase(self, model_name: str, phase_name: str):
        # NEED FIX: Check if all phases are removed!
        if phase_name not in self.storage.keys():
            # already removed
            return
        short_phase_name = phase_name[:-len('_phase')]
        phase = self.storage[phase_name]
        del self.storage[phase_name]
        del self.storage[f"{short_phase_name}_scale"]
        self.phases.items.pop(self.phases.items.index(phase))
        name = self.current_crystal.pop(short_phase_name)
        if name in self.additional_data["phases"].keys():
            del self.additional_data["phases"][name]
        cryspyObjBlockNames = [item.data_name for item in self._cryspyObject.items]
        if phase_name not in cryspyObjBlockNames:
            return
        cryspyObjBlockIdx = cryspyObjBlockNames.index(phase_name)
        cryspyDictBlockName = f'crystal_{phase_name}'

        del self._cryspyObject.items[cryspyObjBlockIdx]
        del self._cryspyData._cryspyDict[cryspyDictBlockName]

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
        msp = cryspy.AtomSiteSusceptibility(chi_type=msp_name, **msp_args)
        ref_name = str(atom_name) + "_" + msp_name
        self.storage[ref_name] = msp
        return ref_name

    def attachADP(self, atom_name: str, adp_args: Dict[str, float]):
        adp = cryspy.AtomSiteAniso(**adp_args)
        ref_name = str(atom_name) + "_" + "Uani"
        self.storage[ref_name] = adp
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
            # update corresponding element in _cryspyDict
            self.updateCryspyDict(item_key, key, value)

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

    def set_job_type(self, tof=False, pol=False):
        self.type = "powder1DCW"
        self.polarized = False
        if tof:
            self.type = "powder1DTOF"
        if pol:
            self.polarized = True

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
        for key_inner in ["pd_instr_resolution", "pd_instr_reflex_asymmetry", "setup"]:
            if not hasattr(self.model, key_inner):
                setattr(self.model, key_inner, self.storage[key_inner])
        norm = normalization
        if self.polarized:
            norm = 1.0
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
            scale = self.pattern.scale.raw_value / norm
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array - offset

        if 'excluded_points' in kwargs:
            setattr(self.model, 'excluded_points', kwargs['excluded_points'])

        if borg.debug:
            print("CALLING FROM Cryspy\n----------------------")

        results, additional = self.do_calc_setup(scale, this_x_array, pol_fn)
        if full_return:
            return results, additional
        return results

    def powder_1d_tof_calculate(
        self, x_array: np.ndarray, pol_fn=None, full_return: bool = False,
        **kwargs
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

        this_x_array = x_array - offset
        # background
        self.model["tof_background"].time_max = this_x_array[-1]

        if 'excluded_points' in kwargs:
            setattr(self.model, 'excluded_points', kwargs['excluded_points'])

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
                l_key = str(storage_invert[atom]) + "_Cani"
                if l_key in self.storage.keys():
                    i = self.storage[l_key]
                l_key = str(storage_invert[atom]) + "_Ciso"
                if l_key in self.storage.keys():
                    i = self.storage[l_key]
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
                self.model, self.polarized, this_x_array, crystal, phasesL, bg
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
        norm = normalization
        if self.polarized:
            norm = 1.0
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
        self.additional_data["excluded"] = self.excluded_points

        scaled_dependents = [scale * dep / norm for dep in dependents]
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
        self._counter += 1
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

    def updateModelCif(self, cif_string: str):
        # Update the model with the cif string
        cryspyCif = cifV2ToV1_tof(cif_string) # contains phase-specific conversions
        cryspyModelsObj = cryspy.str_to_globaln(cryspyCif)
        self._cryspyObject.add_items(cryspyModelsObj.items)
        cryspyModelsDict = cryspyModelsObj.get_dictionary()
        self._cryspyData._cryspyDict.update(cryspyModelsDict)
        pass # debug

    def updateExpCif(self, edCif, modelNames):
        cryspyObj = self._cryspyObject
        cryspyCif = cifV2ToV1_tof(edCif)
        cryspyExperimentsObj = cryspy.str_to_globaln(cryspyCif)

        # Add/modify CryspyObj with ranges based on the measured data points in _pd_meas loop
        range_min = 0  # default value to be updated later
        range_max = 180  # default value to be updated later
        defaultEdRangeCif = f'_pd_meas.2theta_range_min {range_min}\n_pd_meas.2theta_range_max {range_max}'
        cryspyRangeCif = cifV2ToV1(defaultEdRangeCif)
        cryspyRangeObj = cryspy.str_to_globaln(cryspyRangeCif).items
        for dataBlock in cryspyExperimentsObj.items:
            cryspyExperimentType = type(dataBlock)
            if cryspyExperimentType == cryspy.E_data_classes.cl_2_pd.Pd:
                for item in dataBlock.items:
                    if isinstance(item, cryspy.C_item_loop_classes.cl_1_pd_meas.PdMeasL):
                        range_min = item.items[0].ttheta
                        range_max = item.items[-1].ttheta
                        cryspyRangeObj[0].ttheta_min = range_min
                        cryspyRangeObj[0].ttheta_max = range_max
            elif cryspyExperimentType == cryspy.E_data_classes.cl_2_tof.TOF:
                range_min = 2000  # default value to be updated later
                range_max = 20000  # default value to be updated later
                cryspyRangeCif = f'_range_time_min {range_min}\n_range_time_max {range_max}'
                cryspyRangeObj = cryspy.str_to_globaln(cryspyRangeCif).items
                for item in dataBlock.items:
                    if type(item) is cryspy.C_item_loop_classes.cl_1_tof_meas.TOFMeasL:
                        range_min = item.items[0].time
                        range_max = item.items[-1].time
                        cryspyRangeObj[0].time_min = range_min
                        cryspyRangeObj[0].time_max = range_max
                for idx, item in enumerate(dataBlock.items):
                    if type(item) is cryspy.C_item_loop_classes.cl_1_tof_background.TOFBackground:
                        dataBlock.items[idx].time_max = range_max

            dataBlock.add_items(cryspyRangeObj)

        # Add/modify CryspyObj with phases based on the already loaded phases
        # loadedModelNames = [block['name']['value'] for block in self._dataBlocks]
        for dataBlock in cryspyExperimentsObj.items:
            for itemIdx, item in enumerate(dataBlock.items):
                if isinstance(item, cryspy.C_item_loop_classes.cl_1_phase.PhaseL):
                    cryspyModelNames = [phase.label for phase in item.items]
                    for modelIdx, modelName in enumerate(cryspyModelNames):
                        if modelName not in modelNames:
                            del item.items[modelIdx]
                    if not len(item.items):
                        del dataBlock.items[itemIdx]
            itemTypes = [type(item) for item in dataBlock.items]
            if cryspy.C_item_loop_classes.cl_1_phase.PhaseL not in itemTypes:
                if modelNames:
                    defaultEdModelsCif = 'loop_\n_pd_phase_block.id\n_pd_phase_block.scale'
                    for modelName in modelNames:
                        defaultEdModelsCif += f'\n{modelName} 1.0'
                    cryspyPhasesCif = cifV2ToV1(defaultEdModelsCif)
                    cryspyPhasesObj = cryspy.str_to_globaln(cryspyPhasesCif).items
                    dataBlock.add_items(cryspyPhasesObj)

        cryspyObj.add_items(cryspyExperimentsObj.items)
        cryspyExperimentsDict = cryspyExperimentsObj.get_dictionary()
        self._cryspyData._cryspyDict.update(cryspyExperimentsDict)

    def replaceExpCif(self, edCif, currentExperimentName):
        calcCif = cifV2ToV1(edCif)
        calcExperimentsObj = cryspy.str_to_globaln(calcCif)
        calcExperimentsDict = calcExperimentsObj.get_dictionary()

        calcDictBlockName = f'pd_{currentExperimentName}'

        _, edExperimentsNoMeas = CryspyParser.calcObjAndDictToEdExperiments(calcExperimentsObj,
                                                                            calcExperimentsDict)

        # self._cryspyData._cryspyObj.items[calcObjBlockIdx] = calcExperimentsObj.items[0]
        self._cryspyData._cryspyObj.items[0] = calcExperimentsObj.items[0]
        self._cryspyData._cryspyDict[calcDictBlockName] = calcExperimentsDict[calcDictBlockName]
        sdataBlocksNoMeas = edExperimentsNoMeas[0]

        return sdataBlocksNoMeas

    def updateCryspyDict(self, item, key, value):
        '''
        Update the input cryspy dictionary with the key
            referenced by the item-key pair
        '''
        if not self._cryspyData._inOutDict:
            return
        if not self._cryspyData._cryspyDict:
            return
        # check the direct mapping first
        if key in CRYSPY_MODEL_PHASE_KEYS:
            # phase param
            # TODO: remove assumption that the phase is the first block
            phase_name = list(self._cryspyData._cryspyDict.keys())[0]
            cryspy_dict = self._cryspyData._cryspyDict[phase_name]
            cryspy_key = CRYSPY_MODEL_PHASE_KEYS[key]
            loc = cryspy_dict[cryspy_key]
            # find the text in `item` after the last underscore
            atom_index = int(item[item.rfind('_') + 1:])
            # is this a fractional coordinate?
            if 'fract' in key:
                coord_index = CRYSPY_MODEL_COORD_INDEX[key]
                loc[coord_index][atom_index] = value
            elif 'length' in key:
                coord_index = CRYSPY_MODEL_COORD_INDEX[key]
                loc[coord_index] = value
            else:
                loc[atom_index] = value
            return
        elif key in CRYSPY_MODEL_INSTR_KEYS:
            # instrument param
            exp_name = list(self._cryspyData._cryspyDict.keys())[1]
            cryspy_dict = self._cryspyData._cryspyDict[exp_name]
            cryspy_key = CRYSPY_MODEL_INSTR_KEYS[key]
            loc = cryspy_dict[cryspy_key]
            if 'pd_instr' in item:
                coord_index = CRYSPY_MODEL_COORD_INDEX[key]
                loc[coord_index] = value
            else:
                loc = np.array([value])
        else:
            return

    def calculate_profile(self):
        # use data from the current dictionary to calculate profile
        result = rhochi_calc_chi_sq_by_dictionary(
            self._cryspyData._cryspyDict,
            dict_in_out=self._cryspyData._inOutDict,
            flag_use_precalculated_data=False,
            flag_calc_analytical_derivatives=False)
        return result

    @staticmethod
    def nonPolarized_update(crystals, profiles, peak_dat, scales, x_str):
        dependent = np.array([profile[0] for profile in profiles])
        output = {}
        for idx, profile in enumerate(profiles):
            output.update(
                {
                    crystals[idx].data_name: {
                        "hkl": {
                            x_str: peak_dat[idx][x_str+'_hkl'],
                            "h": peak_dat[idx]['index_hkl'][0],
                            "k": peak_dat[idx]['index_hkl'][1],
                            "l": peak_dat[idx]['index_hkl'][2],
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
        up = np.array([profile[0] for profile in profiles])
        down = np.array([profile[1] for profile in profiles])

        dependent = np.array([func(u, d) for u, d in zip(up, down)])

        output = {}
        for idx, profile in enumerate(profiles):
            output.update(
                {
                    crystals[idx].data_name: {
                        "hkl": {
                            x_str: peak_dat[idx][x_str+'_hkl'],
                            "h": peak_dat[idx]['index_hkl'][0],
                            "k": peak_dat[idx]['index_hkl'][1],
                            "l": peak_dat[idx]['index_hkl'][2],
                        },
                        "profile": scales[idx] * dependent[idx, :],
                        "components": {
                            "total": dependent[idx, :],
                            "up": scales[idx] * up[idx, :],
                            "down": scales[idx] * down[idx, :],
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
                bg
                ):
        idx = [
            idx for idx, item in enumerate(model.items) if isinstance(item, cryspy.PhaseL)
        ][0]
        model.items[idx] = phase_list

        data_name = crystals.data_name
        setattr(self.model, 'data_name', data_name)

        is_tof = False
        if self.model.PREFIX.lower() == 'tof':
            is_tof = True

        if is_tof:
            ttheta = x_array
        else:
            ttheta = np.radians(x_array) # needs recasting into radians for CW

        # model -> dict
        experiment_dict_model = self.model.get_dictionary()
        exp_name_model = experiment_dict_model['type_name']

        if not self._cryspyData._cryspyDict:
            return None

        self._cryspyDict = self._cryspyData._cryspyDict
        self._cryspyDict[exp_name_model] = experiment_dict_model

        self.excluded_points = np.full(len(ttheta), False)
        if hasattr(self.model, 'excluded_points'):
            self.excluded_points = self.model.excluded_points
        self._cryspyDict[exp_name_model]['excluded_points'] = self.excluded_points
        self._cryspyDict[exp_name_model]['radiation'] = [RAD_MAP[self.pattern.radiation]]
        if is_tof:
            self._cryspyDict[exp_name_model]['time'] = np.array(ttheta) # required for TOF
            self._cryspyDict[exp_name_model]['time_max'] = ttheta[-1]
            self._cryspyDict[exp_name_model]['time_min'] = ttheta[0]
            self._cryspyDict[exp_name_model]['background_time'] = self.pattern.backgrounds[0].x_sorted_points
            self._cryspyDict[exp_name_model]['background_intensity'] = self.pattern.backgrounds[0].y_sorted_points
            self._cryspyDict[exp_name_model]['flags_background_intensity'] = \
                np.full(len(self.pattern.backgrounds[0].x_sorted_points), False)
            for i, point in enumerate(self.pattern.backgrounds[0]):
                self._cryspyDict[exp_name_model]['flags_background_intensity'][i] = not point.y.fixed

        else:
            self._cryspyDict[exp_name_model]['ttheta'] = ttheta
            self._cryspyDict[exp_name_model]['background_ttheta'] = ttheta
            self._cryspyDict[exp_name_model]['background_intensity'] = bg
            self._cryspyDict[exp_name_model]['flags_background_intensity'] = np.full(len(ttheta), True)

        # interestingly, experimental signal is required, although not used for simple profile calc
        self._cryspyDict[exp_name_model]['signal_exp'] = np.array([np.zeros(len(ttheta)), np.zeros(len(ttheta))])

        res = rhochi_calc_chi_sq_by_dictionary(self._cryspyDict,
                                        dict_in_out=self._cryspyData._inOutDict,
                                        flag_use_precalculated_data=False,
                                        flag_calc_analytical_derivatives=False)
        chi2 = res[0]
        point_count = res[1]
        free_param_count = len(res[4])
        self.chisq = chi2 / (point_count - free_param_count)

        if self._cryspyData._inOutDict:
            self._cryspyDict = self._cryspyData._cryspyDict
        self._inOutDict = self._cryspyData._inOutDict

        y_plus = self._inOutDict[exp_name_model]['signal_plus']
        y_minus = self._inOutDict[exp_name_model]['signal_minus']

        result1 = y_plus, y_minus
        result2 = self._inOutDict[exp_name_model]['dict_in_out_' + data_name.lower()]

        return result1, result2


class Data():
    def __init__(self):
        self._cryspyObj = cryspy.str_to_globaln('')
        self._cryspyDict = {}
        self._inOutDict = {}


    def reset(self):
        self._cryspyObj = cryspy.str_to_globaln('')
        self._cryspyDict = {}
        self._inOutDict = {}

    @staticmethod
    def cryspyDictParamPathToStr(p):
        block = p[0]
        group = p[1]
        idx = '__'.join([str(v) for v in p[2]])  # (1,0) -> '1__0', (1,) -> '1'
        s = f'{block}___{group}___{idx}'  # name should match the regular expression [a-zA-Z_][a-zA-Z0-9_]
        return s

    @staticmethod
    def strToCryspyDictParamPath(s):
        label = s.split('___')
        block = label[0]
        group = label[1]
        idx = tuple(np.fromstring(label[2], dtype=int, sep='__'))
        return block, group, idx
