import os
import sys

ed_path = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
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
import easydiffraction as ed

def set_some_params(job):
    # Modify model-related parameters
    phase = job.phases['si']
    phase.scale = 10
    phase.cell.length_a = 5.43
    # Modify experiment-related parameters
    pattern_params = job.pattern
    pattern_params.zero_shift = 0
    experiment_params = job.parameters
    experiment_params.dtt1 = 7476.91
    experiment_params.dtt2 = -1.54
    experiment_params.ttheta_bank = 144.845
    experiment_params.alpha0 = 0.024
    experiment_params.alpha1 = 0.204
    experiment_params.beta0 = 0.038
    experiment_params.beta1 = 0.011
    experiment_params.sigma0 = 0
    experiment_params.sigma1 = 0
    experiment_params.sigma2 = 0
    job.set_background([(2000.0, 221.1),
                        (4000.0, 169.5),
                        (6000.0, 135.4),
                        (10000.0, 121.4),
                        (14000.0, 132.2),
                        (18000.0, 134.0),
                        (22000.0, 143.0),
                        (25000.0, 183.0),
                        (28000.0, 165.0),
                        (29995.0, 204.0)])

def free_some_params(job):
    # Select the model-related parameters to be fitted
    phase = job.phases['si']
    phase.scale.free = True
    phase.cell.length_a.free = True
    # Select the experiment-related parameters to be fitted
    pattern_params = job.pattern
    pattern_params.zero_shift.free = True
    experiment_params = job.parameters
    experiment_params.sigma0.free = True
    experiment_params.sigma1.free = True
    experiment_params.sigma2.free = True

@print_durations()
def fitting(job):
    #job.fit(method='leastsq', minimizer_kwargs={'ftol': 1e-5, 'xtol': 1e-5})
    job.fit(method='leastsq', tolerance=1e-4)

if __name__ == "__main__" :
    # Create a job - the main object to store all the information
    job = ed.Job(type='tof')

    # Load a phase from CIF file
    job.add_phase_from_file('si.cif')
    exit()

    # Show phase info in CIF format
    print('\n*** Phase:')
    print(job.phases['si'].cif)

    # Display the crystal structure of a given model
    job.show_crystal_structure(id='si')

    # Load experimentally measured data from a file in XYE format
    job.add_experiment_from_file('sepd.xye')

    # Print data
    print('\n*** Measured and calculated data:')
    job.print_data()

    # Display the experiment chart
    job.show_experiment_chart()

    # Display the analysis chart before setting initial parameter values
    job.show_analysis_chart()

    # Modify some parameters
    set_some_params(job)

    # Display the analysis chart after modifying parameters
    job.show_analysis_chart()

    # Allow some parameters to be fitted
    free_some_params(job)

    # Print parameters before fitting
    print('\n*** Parameters before fitting:')
    job.print_free_parameters()

    # Start Least-Squares minimization to fit the selected parameters
    print("\n*** Fitting...")
    fitting(job)
    print(f"*** success: {job.fitting_results.success}")

    # Print parameters after fitting
    print('\n*** Parameters after fitting:')
    job.print_free_parameters()

    # Display the analysis chart after fitting
    job.show_analysis_chart()
