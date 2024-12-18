import matplotlib.pyplot as plt

# import numpy as np
import easydiffraction as ed

job = ed.Job()

# change the calculator to CrysFML
job.calculator = 'CrysFML'

### Define phase manually
# phase = ed.Phase(name='si')
# phase.space_group.name_hm_alt = 'F d -3 m'
# phase.cell.length_a = 5.43146
# phase.atom_sites.append(label='Si',
#                         type_symbol='Si',
#                         fract_x=0,
#                         fract_y=0,
#                         fract_z=0,
#                         occupancy=1,
#                         b_iso_or_equiv=0.529)
# job.add_phase(phase=phase)


### Define phase from CIF file
job.add_phase_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\pbso4.cif')
# job.add_phase_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\ncaf.cif')
# job.add_phase_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\lbco.cif')
# job.add_phase_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\si.cif')

### Define experiment from XYE file
# job.add_experiment_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\hrpt.xye')
job.add_experiment_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\D1A.xye')

### Define experiment from CIF file
# job.add_experiment_from_file(r'C:\\projects\\easy\\cfml\\EasyDiffractionLib\\examples\\data\\d1a.cif')

y_cfml = job.calculate_profile()
x = job.experiment.x

# plt.plot(x, y_cfml)
# plt.show()


# change the calculator to CrysFML
job.calculator = 'CrysPy'


# hand waving for the scale between the two calculators
job.phases[0].scale = 1.0 / 222.0

y_cryspy = job.calculate_profile()

y_diff = y_cryspy - y_cfml

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# Plot the first chart (upper chart)
ax1.plot(x, y_cryspy, label='Cryspy')
ax1.plot(x, y_cfml, label='CrysFML', linestyle='--')
ax1.set_ylabel('Values')
ax1.legend()
ax1.grid(True)

# Plot the second chart (difference chart)
ax2.plot(x, y_diff, color='purple', label='Cryspy - CrysFML')
ax2.set_xlabel('X-axis')
ax2.set_ylabel('Difference')
ax2.legend()
ax2.grid(True)

# Adjust layout
plt.tight_layout()
plt.show()
