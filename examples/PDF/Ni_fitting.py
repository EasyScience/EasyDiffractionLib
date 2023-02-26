
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
parameters.wavelength = 1.9122
parameters.delta2 = 2.253193
parameters.delta1 = 0.0

pattern = job.pattern
# pattern.zero_shift = 0.16
pattern.zero_shift = 0.0
job.phases[0].atoms[0].adp.Uiso = 0.005445
job.phases[0].scale = 0.366013

x_data = data[:, 0]

# define params to optimize
pattern.zero_shift.fixed = False
job.phases[0].cell.length_a.fixed = False
job.phases[0].scale.fixed = False
job.phases[0].atoms[0].adp.Uiso.fixed = False

parameters.qdamp.fixed = True
parameters.delta1.fixed = True
parameters.delta2.fixed = True

l_old = job.phases[0].cell.length_a.raw_value
s_old = job.phases[0].scale.raw_value
q_old = parameters.qdamp.raw_value
u_iso = job.phases[0].atoms[0].adp.Uiso.raw_value
d1_old = parameters.delta1.raw_value
d2_old = parameters.delta2.raw_value

fit_parameters = job.get_fit_parameters()

result = fitter.fit(x_data, data[:, 1], 
                    method='least_squares', minimizer_kwargs={'diff_step': 1e-5})

print("The fit has been successful: {}".format(result.success))  
print("The gooodness of fit (chi2) is: {}".format(result.reduced_chi))

print("The optimized parameters are:")
print("Length_a: {} -> {}".format(l_old, job.phases[0].cell.length_a.raw_value))
print("scale: {} -> {}".format(s_old, job.phases[0].scale.raw_value))
print("qdamp: {} -> {}".format(q_old, parameters.qdamp.raw_value))
print("Uiso: {} -> {}".format(u_iso, job.phases[0].atoms[0].adp.Uiso.raw_value))
print("delta1: {} -> {}".format(d1_old, parameters.delta1.raw_value))
print("delta2: {} -> {}".format(d2_old, parameters.delta2.raw_value))


y_data = calculator.fit_func(x_data)

import pylab
# obtain data from PdfFit calculator object
r = x_data
Gobs = data[:, 1]
Gfit = y_data

Gdiff = pylab.array(Gobs) - pylab.array(Gfit)
Gdiff_baseline = -10

# pylab.plot(r, Gobs, '.')
pylab.plot(r, Gobs, 'r-')
pylab.plot(r, Gfit, 'b-')
pylab.plot(r, Gdiff + Gdiff_baseline, 'r-')

pylab.xlabel(u'r (Å)')
pylab.ylabel(u'G (Å$^{-2}$)')
pylab.title('Fit of nickel to x-ray experimental PDF')

# display plot window, this must be the last command in the script
pylab.show()