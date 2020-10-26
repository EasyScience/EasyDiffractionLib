__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

import os, pathlib
import GSASIIscriptable as G2sc

from easyCore import np

class GSASII:

    def __init__(self, filename: str = None):
        self.prm_file_name = 'temp.prm'
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
        self.prm_dir_path = os.path.dirname(os.path.abspath(self.filename))
        self.prm_file_path = os.path.join(self.prm_dir_path, self.prm_file_name)
        with open(self.prm_file_path, 'w') as f:
            f.write(prm_base)

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        self.create_temp_prm()

        gpx = G2sc.G2Project(newgpx=os.path.join(self.prm_dir_path, 'temp.gpx'))  # create a project

        # step 1, setup: add a phase to the project
        cif_file = self.filename
        phase_name = 'Phase'
        gpx.add_phase(cif_file, phasename=phase_name, fmthint='CIF')

        # step 2, setup: add a simulated histogram and link it to the previous phase(s)
        x0 = x_array[0]
        xF = x_array[-1]
        nX = np.prod(x_array.shape)
        x_step = (xF-x0)/(nX - 1)
        hist1 = gpx.add_simulated_powder_histogram(f"{phase_name} simulation",
                                                   self.prm_file_path,
                                                   x0, xF, x_step,
                                                   phases=gpx.phases())

        # Set instrumental parameters
        multiplier = 1000
        wl = self.conditions["wavelength"]
        u = self.conditions["resolution"]["u"] * multiplier
        v = self.conditions["resolution"]["v"] * multiplier
        w = self.conditions["resolution"]["w"] * multiplier
        x = self.conditions["resolution"]["x"] * multiplier
        y = self.conditions["resolution"]["y"] * multiplier
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['Lam'] = [wl,wl,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['U'] = [u,u,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['V'] = [v,v,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['W'] = [w,w,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['X'] = [x,x,0]
        gpx.data[f'PWDR {phase_name} simulation']['Instrument Parameters'][0]['Y'] = [y,y,0]

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
            pathlib.Path(os.path.join(self.prm_dir_path, 'temp.lst')).unlink()
            pathlib.Path(os.path.join(self.prm_dir_path, 'temp.gpx')).unlink()
            pathlib.Path(os.path.join(self.prm_dir_path, 'temp.bak0.gpx')).unlink()

        return ycalc
