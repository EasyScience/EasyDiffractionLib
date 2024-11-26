__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import matplotlib.pyplot as plt
import numpy as np

from easydiffraction import Phases
from easydiffraction.calculators.wrapper_factory import WrapperFactory
from easydiffraction.job.experiment.pd_1d import Instrument1DCWParameters
from easydiffraction.job.old_sample.old_sample import Sample

i = WrapperFactory()

c = Phases.from_cif_file('tests/SrTiO3.cif')

S = Sample(phases=c, parameters=Instrument1DCWParameters.default(), interface=i)

x_data = np.linspace(5, 150, 10000)
y_data = i.fit_func(x_data)

i.switch('CrysPy')
S._updateInterface()

y_data2 = np.array(i.fit_func(x_data))

fig = plt.figure()
axprops = dict()
ax1 = fig.add_axes([0.1, 0.5, 0.8, 0.4], **axprops)
ax1.plot(x_data, y_data, label="CrysFML")
ax1.legend()
axprops['sharex'] = ax1
# axprops['sharey'] = ax1
# force x axes to remain in register, even with toolbar navigation
ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.4], **axprops)
ax2.plot(x_data, y_data2, label="Cryspy")
ax2.legend()
fig.show()
fig.savefig('CFML_Cryspy.png')
