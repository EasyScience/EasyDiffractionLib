__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore import np


class Factorial:
    def __init__(self, *args):
        self._args = args

    def calculate(self, x_data: np.ndarray) -> np.ndarray:
        y_data = np.ones_like(x_data) * self._args[-1]
        for pow, arg in self._args[-2::-1]:
            y_data += arg * x_data ** pow
        return y_data


class Line(Factorial):
    def __init__(self, m=0, c=0):
        super(Line, self).__init__(m, c)