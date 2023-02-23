
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
parameters.qmax = 70
parameters.qdamp = 0.01
parameters.wavelength = 1.9122

pattern = job.pattern
pattern.zero_shift = 0.16
pattern.scale = 1.4473

x_data = data[:, 0]

y_data = job.create_simulation(x_data)

# fitting
# params to optimize
parameters.qdamp.fixed = False
job.phases[0].cell.length_a.fixed = False
job.phases[0].scale.fixed = False
job.phases[0].atoms[0].adp.Uiso.fixed = False

l_old = job.phases[0].cell.length_a.raw_value
s_old = job.phases[0].scale.raw_value
q_old = parameters.qdamp.raw_value
u_iso = job.phases[0].atoms[0].adp.Uiso.raw_value

fit_parameters = job.get_fit_parameters()

result = fitter.fit(x_data, data[:, 1], 
                    method='least_squares', minimizer_kwargs={'diff_step': 1e-5})

print("The fit has been successful: {}".format(result.success))  
print("The gooodness of fit (chi2) is: {}".format(result.reduced_chi))

print("The optimized parameters are:")
print("{} -> {}".format(l_old, job.phases[0].cell.length_a.raw_value))
print("{} -> {}".format(s_old, job.phases[0].scale.raw_value))
print("{} -> {}".format(q_old, parameters.qdamp.raw_value))
print("{} -> {}".format(u_iso, job.phases[0].atoms[0].adp.Uiso.raw_value))


y_data = calculator.fit_func(x_data)

import pylab
# obtain data from PdfFit calculator object
r = x_data
Gobs = data[:, 1]
Gfit = y_data

Gdiff = pylab.array(Gobs) - pylab.array(Gfit)
Gdiff_baseline = -10

# pylab.plot(r, Gobs, 'ko')
pylab.plot(r, Gobs, '.')
pylab.plot(r, Gfit, 'b-')
pylab.plot(r, Gdiff + Gdiff_baseline, 'r-')

pylab.xlabel(u'r (Å)')
pylab.ylabel(u'G (Å$^{-2}$)')
pylab.title('Fit of nickel to x-ray experimental PDF')

# display plot window, this must be the last command in the script
pylab.show()