#%% md
# <a target="_blank" href="https://colab.research.google.com/github/EasyScience/EasyDiffractionLib/blob/new_job_dev2/examples/Fitting_PD-TOF_Si-SEPD@Argonne/fitting.ipynb">
#   <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
# </a>
#%% md
# # Fitting TOF-PD
#%% md
# This example shows how to refine the crystal structure parameters of Si from neutron diffraction data in a time-of-flight experiment performed on SEPD diffractometer at Argonne.
#%% md
# ## Import
#%%
# Google Colab related imports
import os
import importlib.util

if os.getenv("COLAB_RELEASE_TAG"):
   print("Running in Google Colab")
   # Install the easydiffraction library if it is not installed (including charts extras)
   if importlib.util.find_spec("easydiffraction") is None:
       !pip install 'easydiffraction[charts] @ git+https://github.com/easyscience/easydiffractionlib.git@new_job_dev2'
   # Download the data files to be read in notebook
   if not os.path.exists('si.cif'):
       !wget https://raw.githubusercontent.com/EasyScience/EasyDiffractionLib/refs/heads/new_job_dev/examples/Fitting_PD-TOF_Si-SEPD@Argonne/si.cif
   if not os.path.exists('sepd.xye'):
       !wget https://raw.githubusercontent.com/EasyScience/EasyDiffractionLib/refs/heads/new_job_dev/examples/Fitting_PD-TOF_Si-SEPD@Argonne/sepd.xye
#%%
# Import the easydiffraction library
import easydiffraction as ed
#%% md
# ## Job
#%%
# Create a job - the main object to store all the information
job = ed.Job(type='tof')
#%% md
# ## Model
#%%
# Load a phase from CIF file
job.add_phase_from_file('si.cif')
print(job.phases)
#%%
# Show phase info in CIF format
phase = job.phases['si']
print(phase.cif)
#%%
# Display the crystal structure of a given model
job.show_crystal_structure(id='si')
#%% md
# ## Experiment
#%%
# Load experimentally measured data from a file in XYE format
job.add_experiment_from_file('sepd.xye')
#%%
pattern_params = job.pattern
experiment_params = job.parameters
#%%
job.show_experiment_chart()
#%% md
# ## Analysis
#%%
# Display the analysis chart before setting initial parameter values
job.show_analysis_chart()
#%%
# Modify model-related parameters
phase.scale = 10
phase.cell.length_a = 5.43

# Modify experiment-related parameters
pattern_params.zero_shift = 0

experiment_params.dtt1 = 7476.91
experiment_params.dtt2 = -1.54
experiment_params.ttheta_bank = 144.845

experiment_params.alpha0 = 0.024
experiment_params.alpha1 = 0.204
experiment_params.beta0 = 0.038
experiment_params.beta1 = 0.011
experiment_params.sigma0 = 0.01
experiment_params.sigma1 = 0.01
experiment_params.sigma2 = 0.01

job.set_background([( 2000.0, 221.1),
                    ( 4000.0, 169.5),
                    ( 6000.0, 135.4),
                    (10000.0, 121.4),
                    (14000.0, 132.2),
                    (18000.0, 134.0),
                    (22000.0, 143.0),
                    (25000.0, 183.0),
                    (28000.0, 165.0),
                    (29995.0, 204.0)])
#%%
# Display the analysis chart after modifying parameters
job.show_analysis_chart()
#%%
# Select the model-related parameters to be fitted
phase.scale.free = True
phase.cell.length_a.free = True

# Select the experiment-related parameters to be fitted
pattern_params.zero_shift.free = True

experiment_params.sigma0.free = True
experiment_params.sigma1.free = True
experiment_params.sigma2.free = True
#%%
# Print parameters before fitting
job.print_free_parameters()
#%%
# Start Least-Squares minimization to fit the selected parameters
job.fit(method='leastsq', tolerance=1e-4)
#%%
# Print parameters after fitting
job.print_free_parameters()
#%%
# Display the analysis chart after fitting
job.show_analysis_chart()