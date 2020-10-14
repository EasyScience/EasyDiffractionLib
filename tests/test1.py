__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore import np

from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Crystal
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Elements.Instruments.Instrument import Pattern

import matplotlib.pyplot as plt


i = InterfaceFactory()

c = Crystal.from_cif_file('tests/SrTiO3.cif')

S = Sample(phase=c, parameters=Pattern(), interface=i)
# S.phase.cell.length_a = 5
# S.parameters.wavelength = 1.25
# print(S)

x_data = np.linspace(5, 150, 100)
y_data = i.fit_func(x_data)

plt.plot(x_data, y_data, label="CFL")
plt.show()

S.parameters.wavelength = 2.5
y_data = i.fit_func(x_data)
plt.plot(x_data, y_data, label="CFL")
plt.show()

S.phase.cell.length_a = 10
y_data = i.fit_func(x_data)
plt.plot(x_data, y_data, label="CFL")
plt.show()