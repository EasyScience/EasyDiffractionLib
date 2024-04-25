import matplotlib.pyplot as plt
import numpy as np

from easydiffraction import Phases
from easydiffraction.interface import InterfaceFactory as Calculator
from easydiffraction.Profiles.P1D import Instrument1DCWPolParameters as CWParamsPol
from easydiffraction.Profiles.P1D import PolPowder1DParameters
from easydiffraction.sample import Sample

calculator = Calculator()
calculator.switch("CrysPy")

def pol_sum(a, b):
    # Which component needs bringing back from cryspy?
    return a+b

def pol_diff(a, b):
    # Which component needs bringing back from cryspy?
    return a-b

# this has to be full path to not confuse the CIF file reader that we are loading a string...
cif_fname = 'd:\\projects\\easyScience\\easyDiffractionLib\\tests\\structure.cif'
phases = Phases.from_cif_file(cif_fname)
phase = phases[0]

parameters = CWParamsPol.default()
parameters.length_a = 10.266
parameters.length_c = 10.266
parameters.length_b = 10.266

parameters.resolution_u = 0.1447
parameters.resolution_v = -0.4252
parameters.resolution_w = 0.3864
parameters.resolution_x = 0.0
parameters.resolution_y = 0.0

pattern = PolPowder1DParameters.default()
pattern.zero_shift = 0.0
pattern.scale = 1.0
pattern.polarization = 0.1
pattern.efficiency = 0.5

S = Sample(phases=phases, parameters=parameters, pattern=pattern)
S.interface = calculator

x_data = np.linspace(1, 120, 500)
y_data = calculator.fit_func(x_data, pol_fn=pol_sum)

plt.plot(x_data, y_data, label="CW (alpha+beta)")
plt.show()

y_data = calculator.fit_func(x_data, pol_fn=pol_diff)

plt.plot(x_data, y_data, label="CW (alpha-beta)")
plt.show()

