import matplotlib.pyplot as plt
import numpy as np

import easydiffraction as ed

job = ed.Job()

# change the calculator to CrysFML
job.calculator = 'CrysFML'

job.add_phase_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\pbso4.cif')

x = np.linspace(10.0, 140.0, 2601)
y = job.calculate_profile(x=x)

plt.plot(x, y)
plt.show()
