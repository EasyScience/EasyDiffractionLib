from easyCore import np

from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Site, Phases, Phase
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters

import matplotlib.pyplot as plt


i = InterfaceFactory()

atom = Site.from_pars(label="my_little_pony",
                        specie='O',
                        fract_x=0.05,
                        fract_y=0.05,
                        fract_z=0.05)
atom.add_adp('Uiso', Uiso=0.0)
phase = Phase(name="p1")
phase.add_atom(atom)

phases = Phases()
phases.append(phase)


S = Sample(phases=phases, parameters=Instrument1DCWParameters.default(), interface=i)

x_data = np.linspace(5, 150, 100)
y_data = i.fit_func(x_data)

plt.plot(x_data, y_data, label="CFL")
plt.show()