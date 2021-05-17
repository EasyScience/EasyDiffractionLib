__author__ = "github.com/wardsimon"
__version__ = "0.0.1"


import cryspy
import warnings
from easyCore import np, borg
from easyCore.Objects.Inferface import ItemContainer
warnings.filterwarnings('ignore')



class Cryspy:

    def __init__(self):
        self._cif_str = ""
        self.conditions = {
            'wavelength': 1.25,
            'resolution': {
                'u': 0.001,
                'v': 0.001,
                'w': 0.001,
                'x': 0.000,
                'y': 0.000
            }

        }
        self.background = None
        self.pattern = None
        self.hkl_dict = {
            'ttheta': np.empty(0),
            'h': np.empty(0),
            'k': np.empty(0),
            'l': np.empty(0)
        }
        self.storage = {}
        self.powder1D = cryspy.Pd(background=cryspy.PdBackgroundL(), phase=cryspy.PhaseL())

    @property
    def cif_str(self):
        return self._cif_str

    @cif_str.setter
    def cif_str(self, value):
        self._cif_str = value
        key = self.createCrystal()
        self.createPhase(key)

    def createPhase(self, crystal_name, key='phase'):
        phase = cryspy.Phase(label=crystal_name, scale=1, igsize=0)
        self.storage[key] = phase
        return key

    def createCrystal(self):
        crystal = cryspy.Crystal.from_cif(self.cif_str)
        key = crystal.data_name
        self.storage[key] = crystal
        self.createPhase(key)
        return key

    def createEmptyCrystal(self, crystal_name):
        crystal = cryspy.Crystal(crystal_name, atom_site=cryspy.AtomSiteL())
        self.storage[crystal_name] = crystal
        self.createPhase(crystal_name)
        return crystal_name

    def createCell(self, key='cell'):
        cell = cryspy.Cell()
        self.storage[key] = cell
        return key

    def assignCell_toCrystal(self, cell_name, crystal_name):
        crystal = self.storage[crystal_name]
        cell = self.storage[cell_name]
        crystal.cell = cell

    def createSpaceGroup(self, key='spacegroup', **kwargs):
        sg = cryspy.SpaceGroup(**kwargs)
        self.storage[key] = sg
        return key

    def assignSpaceGroup_toCrystal(self, spacegroup_name, crystal_name):
        crystal = self.storage[crystal_name]
        space_group = self.storage[spacegroup_name]
        setattr(crystal, 'space_group', space_group)

    def updateSpacegroup(self, crystal_name, **kwargs):
        # This has to be done as sg.name_hm_alt = 'blah' doesn't work :-(
        sg_key = self.createSpaceGroup(**kwargs)
        sg = self.storage[sg_key]
        crystal = self.storage[crystal_name]
        crystal.space_group = sg

    def createAtom(self, atom_name, **kwargs):
        atom = cryspy.AtomSite(label=atom_name, **kwargs)
        self.storage[atom_name] = atom

    def assignAtom_toCrystal(self, atom_label, crystal_name):
        crystal = self.storage[crystal_name]
        atom = self.storage[atom_label]
        atom_list = crystal.atom_site


    def createBackground(self, background_obj):
        key = 'background'
        self.storage[key] = background_obj
        return key

    def createSetup(self, key='setup', attach=True):
        setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
        self.storage[key] = setup
        if attach:
            setattr(self.powder1D, 'setup', setup)
        return key

    def genericUpdate(self, item_key, **kwargs):
        item = self.storage[item_key]
        for key, value in kwargs.items():
            setattr(item, key, kwargs[key])

    def genericReturn(self, item_key, value_key):
        item = self.storage[item_key]
        value = getattr(item, value_key)
        return value

    def createResolution(self, attach=True):
        key = 'resolution'
        resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
        self.storage[key] = resolution
        if attach:
            setattr(self.powder1D, 'resolution', resolution)
        return key

    def updateResolution(self, key, **kwargs):
        resolution = self.storage[key]
        for r_key in kwargs.keys():
            setattr(resolution, r_key, kwargs[key])

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        if not self.cif_str:
            raise AttributeError

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value / 500.0
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array + offset

        if borg.debug:
            print('CALLING FROM Cryspy\n----------------------')
            print(self.conditions)
            print(self.cif_str)

        crystal = self.storage['crystal']

        if self.background is None:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.background.calculate(this_x_array)

        if crystal is None:
            return bg

        profile = self.powder1D.calc_profile(this_x_array, [crystal], True, False)

        self.hkl_dict = {
            'ttheta': pd.d_internal_val['peak_' + crystal.data_name].numpy_ttheta,
            'h': pd.d_internal_val['peak_'+crystal.data_name].numpy_index_h,
            'k': pd.d_internal_val['peak_'+crystal.data_name].numpy_index_k,
            'l': pd.d_internal_val['peak_'+crystal.data_name].numpy_index_l,
        }

        res = scale * np.array(profile.intensity_total) + bg

        np.set_printoptions(precision=3)
        if borg.debug:
            print(f"y_calc: {res}")

        return res

    def get_hkl(self, tth: np.array = None) -> dict:

        hkl_dict = self.hkl_dict

        if tth is not None:
            crystal = cryspy.Crystal.from_cif(self.cif_str)
            phase_list = cryspy.PhaseL()
            phase = cryspy.Phase(label=crystal.data_name, scale=1, igsize=0)
            phase_list.items.append(phase)
            setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
            background = cryspy.PdBackgroundL()
            resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
            pd = cryspy.Pd(setup=setup, resolution=resolution, phase=phase_list, background=background)
            _ = pd.calc_profile(tth, [crystal], True, False)

            hkl_dict = {
                'ttheta': pd.d_internal_val['peak_' + crystal.data_name].numpy_ttheta,
                'h': pd.d_internal_val['peak_' + crystal.data_name].numpy_index_h,
                'k': pd.d_internal_val['peak_' + crystal.data_name].numpy_index_k,
                'l': pd.d_internal_val['peak_' + crystal.data_name].numpy_index_l,
            }

        return hkl_dict