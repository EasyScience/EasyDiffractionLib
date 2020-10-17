__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from easyCore import np
import cryspy


class Cryspy:

    def __init__(self):
        self.cif_str = ""
        self.conditions = {
            'wavelength': 1.25,
            'resolution': {
                'u': 0.001,
                'v': 0.001,
                'w': 0.001,
                'x': 0.001,
                'y': 0.001
            }

        }

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

        crystal = cryspy.Crystal.from_cif(self.cif_str)
        phase_list = cryspy.PhaseL()
        phase = cryspy.Phase(label=crystal.data_name, scale=1, igsize=0)
        phase_list.items.append(phase)
        setup = cryspy.Setup(wavelength=self.conditions['wavelength'], offset_ttheta=0)
        background = cryspy.PdBackgroundL()
        resolution = cryspy.PdInstrResolution(**self.conditions['resolution'])
        pd = cryspy.Pd(setup=setup, resolution=resolution, phase=phase_list, background=background)
        profile = pd.calc_profile(x_array, [crystal], True, False)
        return profile.intensity_total
