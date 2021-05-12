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

    @property
    def cif_str(self):
        return self._cif_str

    @cif_str.setter
    def cif_str(self, value):
        self._cif_str = value
        self.createPhase()

    def createPhase(self):
        crystal = cryspy.Crystal.from_cif(self.cif_str)
        self.storage['crystal'] = crystal
        phase = cryspy.Phase(label=crystal.data_name, scale=1, igsize=0)
        # label = crystal.data_name + '_phase'
        self.storage['phase'] = phase
        return 'phase'

    def updateCrystal(self, name='crystal', **kwargs):
        c = self.storage[name]
        for key in kwargs.keys():
            setattr(c, key, kwargs[key])

    def createSetup(self, key='setup'):
        setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
        self.storage[key] = setup
        return key

    def updateSetup(self, key='setup', **kwargs):
        setup = self.storage[key]
        for r_key in kwargs.keys():
            setattr(setup, r_key, kwargs[key])

    def genericUpdate(self, item_key, **kwargs):
        item = self.storage[item_key]
        for key, value in kwargs.items():
            setattr(item, key, kwargs[key])

    def genericReturn(self, item_key, value_key):
        item = self.storage[item_key]
        value = getattr(item, value_key)
        return value

    def createResolution(self):
        key = 'resolution'
        self.storage[key] = cryspy.PdInstrResolution(**self.conditions['resolution'])
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

        phase_list = cryspy.PhaseL()
        phase_list.items.append(self.storage['phase'])
        background = cryspy.PdBackgroundL()
        resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
        pd = cryspy.Pd(setup=self.storage['setup'], resolution=resolution, phase=phase_list, background=background)
        crystal = self.storage['crystal']

        if self.background is None:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.background.calculate(this_x_array)

        if crystal is None:
            return bg

        profile = pd.calc_profile(this_x_array, [crystal], True, False)

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