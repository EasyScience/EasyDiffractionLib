__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore import np
from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Phases
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Elements.Experiments.Experiment import Pars1D
from easyDiffractionLib.Elements.Experiments.Pattern import Pattern1D
from easyDiffractionLib.Elements.Backgrounds.Point import PointBackground, BackgroundPoint

from easyCore.Fitting.Fitting import Fitter
from easyCore.Datasets.xarray import xr

interface = InterfaceFactory()
c = Phases.from_cif_file('PbSO4.cif')
S = Sample(phases=c, parameters=Pars1D.default(), pattern=Pattern1D.default(), interface=interface)

file_path = 'PbSO4_neutrons_short.xye'
data_x, data_y, data_e = np.loadtxt(file_path, unpack=True)

data_set = xr.Dataset()
data_set.easyCore.add_coordinate('tth', data_x)
data_set.easyCore.add_variable('I', ['tth'], data_y)
data_set.easyCore.sigma_attach('I', data_e)


S.parameters.wavelength = 1.912
S.parameters.u_resolution = 1.4
S.parameters.v_resolution = -0.42
S.parameters.w_resolution = 0.38
S.parameters.x_resolution = 0.0
S.parameters.y_resolution = 0.0

bg = PointBackground(linked_experiment='PbSO4')
bg.append(BackgroundPoint.from_pars(data_x[0], 200))
bg.append(BackgroundPoint.from_pars(data_x[-1], 200))

S.set_background(bg)
f = Fitter(S, interface.fit_func)

# Vary the scale and the BG points
S.pattern.scale.fixed = False
S.parameters.resolution_u.fixed = False
S.parameters.resolution_v.fixed = False
S.parameters.resolution_w.fixed = False
S.backgrounds[0][0].y.fixed = False
S.backgrounds[0][1].y.fixed = False

# result = f.fit(data_x, data_y, weights=1/data_e)
result = data_set['I'].easyCore.fit(f)

if result.success:
    print("The fit has been successful: {}".format(result.success))
    print("The gooodness of fit is: {}".format(result.goodness_of_fit))

sim_y_data = interface.fit_func(data_x)
