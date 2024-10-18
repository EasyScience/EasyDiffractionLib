import os
import sys

ed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ec_path = os.path.abspath(os.path.join(ed_path, '..', 'EasyCrystallography', 'src'))
es_path = os.path.abspath(os.path.join(ed_path, '..', 'EasyScience', 'src'))
print(f'Current working directory: {os.getcwd()}')
print(f'easydiffraction path:      {ed_path}')
print(f'easycrystallography path:  {ec_path}')
print(f'easyscience path:          {es_path}')
sys.path.append(ed_path)
sys.path.append(ec_path)
sys.path.append(es_path)

from funcy import print_durations
import matplotlib.pyplot as plt
import easydiffraction as ed

def set_some_params(job):
    # job.phases[0].scale = 1.460
    job.phases['PbSO4'].cell.length_a = 8.45
    job.pattern.zero_shift = 0.1406  # now -0.1406
    # job.parameters.resolution_u = 0.139
    # job.parameters.resolution_v = -0.4124
    # job.parameters.resolution_w = 0.386
    # job.parameters.resolution_y = 0.0878
    job.set_background([(11.0, 206.1624), (15.0, 194.75), (20.0, 194.505), (30.0, 188.4375), (50.0, 207.7633), (70.0, 201.7002), (120.0, 244.4525), (153.0, 226.0595)])

def free_some_params(job):
    job.phases[0].scale.fixed = False
    job.phases['PbSO4'].cell.length_a.fixed = False
    job.phases['PbSO4'].atom_sites['Pb'].fract_x.fixed = False
    job.phases['PbSO4'].atom_sites['Pb'].fract_z.fixed = False
    job.phases['PbSO4'].atom_sites['S'].fract_x.fixed = False
    job.phases['PbSO4'].atom_sites['S'].fract_z.fixed = False
    job.phases['PbSO4'].atom_sites['O1'].fract_x.fixed = False
    job.phases['PbSO4'].atom_sites['O1'].fract_z.fixed = False
    job.phases['PbSO4'].atom_sites['O2'].fract_x.fixed = False
    job.phases['PbSO4'].atom_sites['O2'].fract_z.fixed = False
    job.phases['PbSO4'].atom_sites['O3'].fract_x.fixed = False
    job.phases['PbSO4'].atom_sites['O3'].fract_y.fixed = False
    job.phases['PbSO4'].atom_sites['O3'].fract_z.fixed = False
    job.pattern.zero_shift.fixed = False
    job.parameters.resolution_u.fixed = False
    job.parameters.resolution_v.fixed = False
    job.parameters.resolution_w.fixed = False
    job.parameters.resolution_y.fixed = False

def print_some_params(job):
    print(job.phases[0].scale)
    print(job.phases['PbSO4'].cell.length_a)
    print(job.pattern.zero_shift)
    print(job.parameters.resolution_u)
    print(job.parameters.resolution_v)
    print(job.parameters.resolution_w)
    print(job.parameters.resolution_x)
    print(job.parameters.resolution_y)

@print_durations()
def fitting(job):
    job.fit(method='leastsq',
            minimizer_kwargs={'ftol': 1e-5, 'xtol': 1e-5})

# create a job
job = ed.Job()

# add a phase and a measured dataset
job.add_phase_from_file('PbSO4.cif')
job.add_experiment_from_file('D1A@ILL.xye')

# set some parameters
set_some_params(job)

# allow some parameters to be fitted
free_some_params(job)

# print some parameters
print('Parameters before fitting:')
print_some_params(job)

# fitting
fitting(job)
print(job.fitting_results.success)

# print some parameters
print('Parameters after fitting:')
print_some_params(job)

# plot the results
plt.plot(job.experiment.x, job.experiment.y)
plt.plot(job.experiment.x, job.calculate_profile())
plt.show()


#method              minimizer_kwargs           execution time
# EasyDiffractionBeta
#'leastsq'           {'ftol':1e-5,'xtol':1e-5}  5.14s
# EasyDiffractionLib
#'least_squares'     {'diff_step': 1e-5}        13.94s
#'least_squares'     {}                         23.21s
#'leastsq'           {}                         10.07s
#'leastsq'           {'ftol':1e-5,'xtol':1e-5}  8.52s

## + refine all xyz coordinates

#method              minimizer_kwargs           execution time
# EasyDiffractionBeta
#'leastsq'           {'ftol':1e-5,'xtol':1e-5}  12.40s
# EasyDiffractionLib
#'leastsq'           {'ftol':1e-5,'xtol':1e-5}  22.66s
