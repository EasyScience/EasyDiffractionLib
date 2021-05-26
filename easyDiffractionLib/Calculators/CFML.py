__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, pathlib

import CFML_api
import timeit

from easyCore import np, borg


class CFML:
    def __init__(self, filename: str = None):
        self.filename = filename
        self.conditions = None
        self.background = None
        self.pattern = None
        self.hkl_dict = {
            'ttheta': np.empty(0),
            'h': np.empty(0),
            'k': np.empty(0),
            'l': np.empty(0)
        }

    def createConditions(self, job_type='N'):
        self.conditions = {
            'lamb':         1.54,
            'u_resolution': 0.01,
            'v_resolution': 0.0,
            'w_resolution': 0.0,
            'x_resolution': 0.0,
            'y_resolution': 0.0,
            'z_resolution': 0.0
        }

    def conditionsUpdate(self, _, **kwargs):
        for key, value in kwargs.items():
            self.conditions[key]= value

    def conditionsReturn(self, _, name):
        self.conditions.get(name)

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
        #job_info.print_description()

        # Experiment/Instrument/Simulation parameters
        x_min = this_x_array[0]
        x_max = this_x_array[-1]
        num_points = np.prod(x_array.shape)
        x_step = (x_max - x_min) / (num_points - 1)
        job_info.range_2theta = (x_min, x_max)
        job_info.theta_step = x_step
        job_info.u_resolution = self.conditions['u_resolution']
        job_info.v_resolution = self.conditions['v_resolution']
        job_info.w_resolution = self.conditions['w_resolution']
        job_info.x_resolution = self.conditions['x_resolution']
        job_info.y_resolution = self.conditions['y_resolution']
        job_info.lambdas = (self.conditions['lamb'], self.conditions['lamb'])
        job_info.bkg = 0.0

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

            start_time = timeit.default_timer()
            reflection_list.compute_structure_factors(space_group,
                                                      atom_list,
                                                      job_info)
            end_time = timeit.default_timer()
            print("+ reflection_list.compute_structure_factors: {0:.4f} s".format(end_time - start_time))

            start_time = timeit.default_timer()
            ttheta_list = []
            h_list = []
            k_list = []
            l_list = []
            for i in range(reflection_list.nrefs):
                reflection = reflection_list[i]
                h = reflection.hkl[0]
                k = reflection.hkl[1]
                l = reflection.hkl[2]
                h_list.append(h)
                k_list.append(k)
                l_list.append(l)
                ttheta = np.rad2deg(np.arcsin(reflection.stl * job_info.lambdas[0])) * 2
                ttheta_list.append(ttheta)
            self.hkl_dict['ttheta'] = np.asarray(ttheta_list)
            self.hkl_dict['h'] = np.asarray(h_list)
            self.hkl_dict['k'] = np.asarray(k_list)
            self.hkl_dict['l'] = np.asarray(l_list)
            end_time = timeit.default_timer()
            print("+ set reflection_list: {0:.4f} s".format(end_time - start_time))

            start_time = timeit.default_timer()
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
