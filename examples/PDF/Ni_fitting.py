
import os

from easyCore.Fitting.Fitting import Fitter
from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Phases
from easyDiffractionLib.interface import InterfaceFactory as Calculator
from easyDiffractionLib.Profiles.P1D import Powder1DParameters, PDFParameters
from easyDiffractionLib.Interfaces.pdffit2 import readGRData


calculator = Calculator()
calculator.switch("Pdffit2")

# data_fname = os.path.realpath('examples\\PDF\\Ni-xray.gr')
data_fname = os.path.realpath('Ni-xray.gr')
data = readGRData(data_fname)

# cif_fname = os.path.realpath('examples\\PDF\\Ni.cif')
cif_fname = os.path.realpath('Ni.cif')
phases = Phases.from_cif_file(cif_fname)

parameters = PDFParameters()

# PDF parameters
parameters.qmax = 70
parameters.qdamp = 0.01

pattern = Powder1DParameters()

S = Sample(phases=phases, parameters=parameters, pattern=pattern)
S.interface = calculator

x_data = data[:, 0]

# profile calculation
y_data = calculator.fit_func(x_data)


# fitting
# params to optimize
S.phases[0].cell.length_a.fixed = False
S.phases[0].scale.fixed = False
S.pattern.scale.fixed = False

l_old = S.phases[0].cell.length_a.raw_value
s_old = S.phases[0].scale.raw_value
p_old = S.pattern.scale.raw_value


fitter = Fitter(S, calculator.fit_func)

result = fitter.fit(x_data, data[:, 1], 
                    method='least_squares', minimizer_kwargs={'diff_step': 1e-5})

print("The fit has been successful: {}".format(result.success))  
print("The gooodness of fit (chi2) is: {}".format(result.reduced_chi))

print("The optimized parameters are:")
print("{} -> {}".format(l_old, S.phases[0].cell.length_a.raw_value))
print("{} -> {}".format(s_old, S.phases[0].scale.raw_value))
print("{} -> {}".format(p_old, S.pattern.scale.raw_value))



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