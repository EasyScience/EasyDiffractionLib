__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, pathlib
from easyCore import borg
import GSASIIscriptable as G2sc

from easyCore import np


class GSASII:

    def __init__(self, filename: str = None):
        self.prm_file_name = 'easydiffraction_temp.prm'
        self.prm_file_path = ""
        self.prm_dir_path = ""
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
        self.filename = filename
        self.background = None
        self.pattern = None
        self.hkl_dict = {
            'ttheta': np.empty(0),
            'h': np.empty(0),
            'k': np.empty(0),
            'l': np.empty(0)
        }

    def create_temp_prm(self):
        if self.filename is None:
            return
        prm_base = """
            123456789012345678901234567890123456789012345678901234567890
INS   BANK      1                                                               
INS   HTYPE   PNCR                                                              
INS  1 ICONS  1.909000  0.000000      -0.1         0       0.0    0       0.0
INS  1I HEAD  DUMMY INCIDENT SPECTRUM FOR DIFFRACTOMETER D1A                    
INS  1I ITYP    0    0.0000  180.0000         1                                 
INS  1PRCF1     1    6      0.01                                                
INS  1PRCF11   0.354031E+03  -0.760404E+03   0.651592E+03   0.000000E+00        
INS  1PRCF12   0.000000E+00   0.000000E+00   0.000000E+00   0.000000E+00        
INS  1PRCF2     2    6      0.01                                                
INS  1PRCF21   0.354031E+03  -0.760404E+03   0.651592E+03   0.000000E+00        
INS  1PRCF22   0.000000E+00   0.000000E+00                                              
        """
        self.prm_dir_path = os.path.dirname(self.filename)
        self.prm_file_path = os.path.join(self.prm_dir_path, self.prm_file_name)
        with open(self.prm_file_path, 'w') as f:
            f.write(prm_base)

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        self.create_temp_prm()

        if self.pattern is None:
            scale = 1.0
            offset = 0
        else:
            scale = self.pattern.scale.raw_value
            offset = self.pattern.zero_shift.raw_value

        this_x_array = x_array + offset

        gpx = G2sc.G2Project(newgpx=os.path.join(self.prm_dir_path, 'easydiffraction_temp.gpx'))  # create a project

        # step 1, setup: add a phase to the project
        cif_file = self.filename
        phase_name = 'Phase'
        gpx.add_phase(cif_file, phasename=phase_name, fmthint='CIF')

        # step 2, setup: add a simulated histogram and link it to the previous phase(s)
        x_min = this_x_array[0]
        x_max = this_x_array[-1]
        n_points = np.prod(x_array.shape)
        x_step = (x_max-x_min)/(n_points - 1)
        gpx.add_simulated_powder_histogram(f"{phase_name} simulation",
                                           self.prm_file_path,
                                           x_min, x_max, Tstep=x_step,
                                           phases=gpx.phases())

        # Set instrumental parameters
        resolution_multiplier = 1000
        u = self.conditions["resolution"]["u"] * resolution_multiplier
        v = self.conditions["resolution"]["v"] * resolution_multiplier
        w = self.conditions["resolution"]["w"] * resolution_multiplier
        x = self.conditions["resolution"]["x"] * resolution_multiplier
        y = self.conditions["resolution"]["y"] * resolution_multiplier
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['U'] = [u,u,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['V'] = [v,v,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['W'] = [w,w,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['X'] = [x,x,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['Y'] = [y,y,0]

        wl = self.conditions["wavelength"]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['Lam'] = [wl,wl,0]

        # Step 3: Set the scale factor to adjust the y scale
        #hist1.SampleParameters['Scale'][0] = 1000000.

        # step 4, compute: turn off parameter optimization and calculate pattern
        gpx.data['Controls']['data']['max cyc'] = 0  # refinement not needed

        try:
            gpx.do_refinements(refinements=[{}], makeBack=[])
            # step 5, retrieve results & plot
            ycalc = gpx.histogram(0).getdata('ycalc')
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

        res = scale * ycalc + bg

        np.set_printoptions(precision=3)
        if borg.debug:
            print(f"y_calc: {res}")

        return res

    def get_hkl(self, tth: np.array = None) -> dict:
        hkl_dict = self.hkl_dict
        if tth is not None:
            pass
        return hkl_dict
