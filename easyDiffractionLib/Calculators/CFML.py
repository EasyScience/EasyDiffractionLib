__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, pathlib, math

import CFML_api

from easyCore import np, borg


class CFML:
    def __init__(self, filename: str = None):
        self.filename = filename
        self.conditions = CFML_api.PowderPatternSimulationConditions()
        self.conditions.job = CFML_api.PowderPatternSimulationSource.Neutrons
        self.conditions.lorentzian_size = 10000.0
        self.conditions.bkg = 0.0
        self.background = None
        self.pattern = None
        self.hkl_dict = {
            'ttheta': np.empty(0),
            'h': np.empty(0),
            'k': np.empty(0),
            'l': np.empty(0)
        }
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

        #print("self.filename", self.filename)

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array + offset

        # Sample parameters
        cif_file = CFML_api.CIFFile(self.filename)
        cell = cif_file.cell
        space_group = cif_file.space_group
        atom_list = cif_file.atom_list

        #cell.print_description()
        #space_group.print_description()
        #atom_list.print_description()
        #print(self.conditions)

        # Experiment/Instrumnet/Simulation parameters
        x_min = this_x_array[0]
        x_max = this_x_array[-1]
        num_points = np.prod(x_array.shape)
        self.conditions.theta_min = x_min
        self.conditions.theta_max = x_max
        self.conditions.theta_step = (x_max - x_min) / (num_points - 1)

        #print("self.conditions", self.conditions)
        #print("self.conditions.theta_min", self.conditions.theta_min)
        #print("self.conditions.theta_max", self.conditions.theta_max)
        #print("self.conditions.theta_step", self.conditions.theta_step)

        sin_theta_over_lambda_max = math.sin(math.radians(0.5 * self.conditions.theta_max)) / self.conditions.lamb
        sin_theta_over_lambda_max = max(1.0, sin_theta_over_lambda_max)
        #print(f"Manually sin_theta_over_lambda_max: {sin_theta_over_lambda_max} for lambda: {self.conditions.lamb}")
        #sin_theta_over_lambda_max = self.conditions.getSinThetaOverLambdaMax()
        #print(f"CFML self.conditions.getSinThetaOverLambdaMax(): {sin_theta_over_lambda_max} for lambda: {self.conditions.lamb}")

        # Calculations
        try:
            reflection_list = CFML_api.ReflectionList(cell, space_group, True, 0, sin_theta_over_lambda_max)
            reflection_list.compute_structure_factors(space_group, atom_list)
            diffraction_pattern = CFML_api.DiffractionPattern(self.conditions, reflection_list, cell.reciprocal_cell_vol)
        except:
            raise ArithmeticError
        finally:
            # Clean up
            for p in pathlib.Path(os.path.dirname(self.filename)).glob("easydiffraction_temp*"):
                if os.path.basename(p) != "easydiffraction_temp.cif":
                    p.unlink()

        self.hkl_dict = {
            'ttheta': np.array([]),
            'h': np.array([]),
            'k': np.array([]),
            'l': np.array([])
        }

        if self.background is None:
            bg = np.zeros_like(this_x_array)
        else:
            bg = self.background.calculate(this_x_array)

        res = scale * diffraction_pattern.ycalc + bg

        np.set_printoptions(precision=3)
        if borg.debug:
            print(f"y_calc: {res}")

        return res

    def get_hkl(self, tth: np.array = None) -> dict:
        hkl_dict = self.hkl_dict
        if tth is not None:
            pass
        return hkl_dict
