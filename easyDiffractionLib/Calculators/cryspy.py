__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from easyCore import np
from easyCore import borg
import cryspy

import warnings

warnings.filterwarnings('ignore')


class Cryspy:

    def __init__(self):
        self.cif_str = ""
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
            scale = self.pattern.scale.raw_value
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array.copy() + offset

        if borg.debug:
            print('CALLING FROM Cryspy\n----------------------')
            print(self.conditions)
            print(self.cif_str)

        crystal = cryspy.Crystal.from_cif(self.cif_str)
        phase_list = cryspy.PhaseL()
        phase = cryspy.Phase(label=crystal.data_name, scale=1, igsize=0)
        phase_list.items.append(phase)
        setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
        background = cryspy.PdBackgroundL()
        resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
        pd = cryspy.Pd(setup=setup, resolution=resolution, phase=phase_list, background=background)
        profile = pd.calc_profile(this_x_array, [crystal], True, False)

        if self.background is None:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.background.calculate(this_x_array)

        return scale * np.array(profile.intensity_total) + bg
