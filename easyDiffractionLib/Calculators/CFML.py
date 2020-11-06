__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, pathlib

from easyCore import np
from easyCore import borg

import CFML_api


class CFML:
    def __init__(self, filename: str = None):
        print("CFML __init__")

        self.filename = filename
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

        print("self.filename", self.filename )


        # Sample parameters
        cif_file = CFML_api.CIFFile(self.filename)
        cell = cif_file.cell
        space_group = cif_file.space_group
        atom_list = cif_file.atom_list

        #cell.print_description()
        #space_group.print_description()
        #atom_list.print_description()

        # Experiment/Instrumnet/Simulation parameters
        x_min = x_array[0]
        x_max = x_array[-1]
        num_points = np.prod(x_array.shape)
        self.conditions.theta_min = x_min
        self.conditions.theta_max = x_max
        self.conditions.theta_step = (x_max - x_min) / (num_points - 1)

        #print("self.conditions.theta_min", self.conditions.theta_min)
        #print("self.conditions.theta_max", self.conditions.theta_max)
        #print("self.conditions.theta_step", self.conditions.theta_step)
        #print("self.conditions.getSinThetaOverLambdaMax()", self.conditions.getSinThetaOverLambdaMax())

        # Calculations
        try:
            reflection_list = CFML_api.ReflectionList(cell, space_group, True, 0, self.conditions.getSinThetaOverLambdaMax())
            reflection_list.compute_structure_factors(space_group, atom_list)
            diffraction_pattern = CFML_api.DiffractionPattern(self.conditions, reflection_list, cell.reciprocal_cell_vol)
        except:
            raise ArithmeticError
        finally:
            # Clean up
            for p in pathlib.Path(os.path.dirname(self.filename)).glob("easydiffraction_temp*"):
                p.unlink()

        return diffraction_pattern.y
