__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np
from easyscience.Datasets.xarray import xr
from easyscience.fitting.fitter import Fitter

from easydiffraction import Phases
from easydiffraction.job.experiment.backgrounds.point import BackgroundPoint
from easydiffraction.job.experiment.backgrounds.point import PointBackground
from easydiffraction.elements.Experiments.Experiment import Pars1D
from easydiffraction.elements.Experiments.Pattern import Pattern1D
from easydiffraction.calculators.wrapper_factory import WrapperFactory
from easydiffraction.job.old_sample.old_sample import Sample

interface = WrapperFactory()
c = Phases.from_cif_file('PbSO4.cif')
S = Sample(phases=c, parameters=Pars1D.default(), pattern=Pattern1D.default(), interface=interface)

file_path = 'PbSO4_neutrons_short.xye'
data_x, data_y, data_e = np.loadtxt(file_path, unpack=True)

data_set = xr.Dataset()
data_set.easyscience.add_coordinate('tth', data_x)
data_set.easyscience.add_variable('I', ['tth'], data_y)
data_set.easyscience.sigma_attach('I', data_e)


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
S.pattern.zero_shift.fixed = False
S.parameters.resolution_u.fixed = False
S.parameters.resolution_v.fixed = False
S.parameters.resolution_w.fixed = False
S.backgrounds[0][0].y.fixed = True
S.backgrounds[0][1].y.fixed = True

result = f.fit(data_x, data_y)
# result = data_set['I'].easyscience.fit(f)

if result.success:
    print("The fit has been successful: {}".format(result.success))
    print("The gooodness of fit is: {}".format(result.goodness_of_fit))

sim_y_data = interface.fit_func(data_x)

import matplotlib.pyplot as plt # noqa E402

plt.plot(data_x, data_y, label='Data')
plt.plot(data_x, result.y_calc, label='Calculate')
plt.show()
