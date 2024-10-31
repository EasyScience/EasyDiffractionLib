from funcy import print_durations
import easydiffraction as ed

def set_phase_manually(job):
    # Create a phase object
    phase = ed.Phase(name='lbco')
    # Set space group
    phase.space_group.name_hm_alt = 'P m -3 m'
    # Set cell parameters
    phase.cell.length_a = 3.88
    # Add atoms
    phase.atom_sites.append(label='La',
                            type_symbol='La',
                            fract_x=0,
                            fract_y=0,
                            fract_z=0,
                            occupancy=0.5,
                            b_iso_or_equiv=0.4958)
    phase.atom_sites.append(label='Ba',
                            type_symbol='Ba',
                            fract_x=0,
                            fract_y=0,
                            fract_z=0,
                            occupancy=0.5,
                            b_iso_or_equiv=0.4943)
    phase.atom_sites.append(label='Co',
                            type_symbol='Co',
                            fract_x=0.5,
                            fract_y=0.5,
                            fract_z=0.5,
                            b_iso_or_equiv=0.2567)
    phase.atom_sites.append(label='O',
                            type_symbol='O',
                            fract_x=0,
                            fract_y=0.5,
                            fract_z=0.5,
                            b_iso_or_equiv=1.4041)
    # Add phase to the job object
    job.add_phase(phase=phase)

def set_some_params(job):
    # Modify model-related parameters
    phase = job.phases[0]
    phase.scale = 8.5
    phase.cell.length_a = 3.88
    # Modify experiment-related parameters
    pattern_params = job.pattern
    pattern_params.zero_shift = 0
    experiment_params = job.parameters
    experiment_params.wavelength = 1.494
    experiment_params.resolution_u = 0.1
    experiment_params.resolution_v = -0.1
    experiment_params.resolution_w = 0.2
    experiment_params.resolution_x = 0
    experiment_params.resolution_y = 0
    job.set_background([(10.0, 174.3),
                        (20.0, 159.8),
                        (30.0, 167.9),
                        (50.0, 166.1),
                        (70.0, 172.3),
                        (90.0, 171.1),
                        (110.0, 172.4),
                        (130.0, 182.5),
                        (150.0, 173.0),
                        (165.0, 171.1)])

def free_some_params(job):
    # Select the model-related parameters to be fitted
    phase = job.phases[0]
    phase.scale.free = True
    phase.cell.length_a.free = True
    # Select the experiment-related parameters to be fitted
    pattern_params = job.pattern
    pattern_params.zero_shift.free = True
    experiment_params = job.parameters
    experiment_params.resolution_u.free = True
    experiment_params.resolution_v.free = True
    experiment_params.resolution_w.free = True
    experiment_params.resolution_y.free = True

@print_durations()
def fitting(job):
    #job.fit(method='leastsq', minimizer_kwargs={'ftol': 1e-5, 'xtol': 1e-5})
    job.fit(method='leastsq', tolerance=1e-4)

if __name__ == "__main__" :
    # Create a job - the main object to store all the information
    job = ed.Job()

    # Set phase manually
    set_phase_manually(job)

    # Show phase info in CIF format
    print('\n*** Phase:')
    print(job.phases['lbco'].cif)

    # Display the crystal structure of a given model
    job.show_crystal_structure(id='lbco')

    # Load experimentally measured data from a file in XYE format
    job.add_experiment_from_file('hrpt.xye')

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
