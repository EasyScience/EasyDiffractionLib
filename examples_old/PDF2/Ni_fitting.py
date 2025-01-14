
import os

from easyCore.Fitting.Fitting import Fitter
from easyDiffractionLib import Phases
from easyDiffractionLib.Jobs import Powder1DCW
from easyDiffractionLib.interface import InterfaceFactory as Calculator
from easyDiffractionLib.Profiles.P1D import PDFParameters
from easyDiffractionLib.Interfaces.pdffit2 import readGRData


# data_fname = "D:\\projects\\easyScience\\easyDiffractionLib\\examples\\PDF\\Ni-xray.gr"
data_fname = os.path.realpath('Ni-xray.gr')
data = readGRData(data_fname)

# phase_cif_name = "D:\\projects\\easyScience\\easyDiffractionLib\\examples\\PDF\\Ni.cif"
phase_cif_name = "Ni.cif"
phases = Phases.from_cif_file(phase_cif_name)

parameters = PDFParameters()

calculator = Calculator()
calculator.switch("Pdffit2")

job = Powder1DCW('Ni', parameters=parameters, phases=phases, interface=calculator)

fitter = Fitter(job, calculator.fit_func)

parameters = job.parameters
# initial values to not be too far from optimized ones
parameters.qmax = 30
parameters.qdamp = 0.063043
parameters.qbroad = 0.1
# let's limit the range of qbroad
parameters.qbroad.min = 0.0
parameters.qbroad.max = 0.5
parameters.wavelength = 0.126514
parameters.delta2 = 2.253193
parameters.delta1 = 0.0
parameters.spdiameter = 0.0

pattern = job.pattern
job.phases[0].atoms[0].adp.Uiso = 0.005445
job.phases[0].scale = 0.366013
job.phases[0].cell.length_a = 3.52

x_data = data[:, 0]

# define params to optimize
job.phases[0].cell.length_a.fixed = False
job.phases[0].scale.fixed = False
job.phases[0].atoms[0].adp.Uiso.fixed = True

parameters.qdamp.fixed = False
parameters.delta1.fixed = False
parameters.delta2.fixed = False
parameters.qbroad.fixed = False

fit_parameters = job.get_fit_parameters()

result = fitter.fit(x_data, data[:, 1], 
                    method='least_squares', minimizer_kwargs={'diff_step': 1e-5})

print("The fit has been successful: {}".format(result.success))  
print("The gooodness of fit (chi2) is: {}".format(result.reduced_chi))

print("The optimized parameters are:")
for param in fit_parameters:
    print("{}: {}".format(param.name, param.value))

y_data = calculator.fit_func(x_data)

# obtain data from PdfFit calculator object
Gobs = data[:, 1]
Gfit = y_data
Gdiff = Gobs - Gfit
Gdiff_baseline = -10

Gdiff_show = Gdiff/5.0 + Gdiff_baseline

from bokeh.io import show
from bokeh.plotting import figure

fig = figure()
fig.xaxis.axis_label = 'r (Å)'
fig.yaxis.axis_label = r"$$G (Å^{-2})\$$"
fig.title.text = 'Fit of nickel to x-ray experimental PDF'

fig.scatter(x_data, Gobs, legend_label='G(r) Data', fill_alpha=0., line_color='steelblue', marker='circle')
fig.line(x_data, Gfit, legend_label='G(r) Fit', color='orangered', line_width=2)
fig.line(x_data, Gdiff_show, legend_label='G(r) Diff', color='grey', line_width=2)
show(fig)
