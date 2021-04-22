__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, pathlib, math
import timeit

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

        print("\n\n\n")
        start_time = timeit.default_timer()

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value
            offset = self.pattern.zero_shift.raw_value

        end_time = timeit.default_timer()
        print("+ calculate A: {0:.4f} s".format(end_time - start_time))

        start_time = timeit.default_timer()

        this_x_array = x_array + offset

        # Sample parameters
        cif_file = CFML_api.CIFFile(self.filename)
        cell = cif_file.cell
        space_group = cif_file.space_group
        atom_list = cif_file.atom_list
        job_info = cif_file.job_info

        end_time = timeit.default_timer()
        print("+ calculate B: {0:.4f} s".format(end_time - start_time))

        start_time = timeit.default_timer()

        #cell.print_description()
        #space_group.print_description()
        #atom_list.print_description()
        #print("job info", job_info, self.conditions.job, CFML_api.PowderPatternSimulationSource.Neutrons)
        print("conditions", self.conditions)
        job_info.print_description()

        # Experiment/Instrumnet/Simulation parameters
        x_min = this_x_array[0]
        x_max = this_x_array[-1]
        num_points = np.prod(x_array.shape)
        self.conditions.theta_min = x_min
        self.conditions.theta_max = x_max
        self.conditions.theta_step = (x_max - x_min) / (num_points - 1)

        end_time = timeit.default_timer()
        print("+ calculate C: {0:.4f} s".format(end_time - start_time))

        # Calculations
        try:
            start_time = timeit.default_timer()

            reflection_list = CFML_api.ReflectionList(cell,
                                                      space_group,
                                                      True,
                                                      job_info)
            end_time = timeit.default_timer()
            print("+ reflection_list = CFML_api.ReflectionList: {0:.4f} s".format(end_time - start_time))

            reflection_list.compute_structure_factors(space_group,
                                                      atom_list,
                                                      job_info)
            end_time = timeit.default_timer()
            print("+ reflection_list.compute_structure_factors: {0:.4f} s".format(end_time - start_time))

            diffraction_pattern = CFML_api.DiffractionPattern(job_info,
                                                              reflection_list,
                                                              cell.reciprocal_cell_vol)
            end_time = timeit.default_timer()
            print("+ diffraction_pattern = CFML_api.DiffractionPattern: {0:.4f} s".format(end_time - start_time))

        except:
            raise ArithmeticError
        finally:

            start_time = timeit.default_timer()

            # Clean up
            for p in pathlib.Path(os.path.dirname(self.filename)).glob("easydiffraction_temp*"):
                if os.path.basename(p) != "easydiffraction_temp.cif":
                    p.unlink()

            end_time = timeit.default_timer()
            print("+ calculate D: {0:.4f} s".format(end_time - start_time))

        start_time = timeit.default_timer()

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

        end_time = timeit.default_timer()
        print("+ calculate E: {0:.4f} s".format(end_time - start_time))

        start_time = timeit.default_timer()

        np.set_printoptions(precision=3)
        if borg.debug:
            print(f"y_calc: {res}")

        end_time = timeit.default_timer()
        print("+ calculate F: {0:.4f} s".format(end_time - start_time))

        return res

    def get_hkl(self, tth: np.array = None) -> dict:
        hkl_dict = self.hkl_dict
        if tth is not None:
            pass
        return hkl_dict
