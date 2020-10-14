__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from easyCore import np
from CFML_api import PowderPatternSimulation as CFML_api


class CFML:
    def __init__(self, filename: str = None):
        self.filename = filename
        self.simulator = CFML_api.PowderPatternSimulator()
        self.conditions = CFML_api.PowderPatternSimulationConditions()
        self.conditions.bkg = 0.0

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y
        :param x_array: array of data points to be calculated
        :type x_array: np.ndarray
        :return: points calculated at `x`
        :rtype: np.ndarray
        """
        if self.filename is None:
            raise AttributeError

        x0 = x_array[0]
        xF = x_array[-1]
        nX = np.prod(x_array.shape)

        self.conditions.theta_min = x0
        self.conditions.theta_max = xF
        self.conditions.theta_step = (xF-x0)/(nX - 1)

        self.simulator.compute(self.filename, simulation_conditions=self.conditions)
        return self.simulator.y
