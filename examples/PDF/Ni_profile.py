
import os

from easyCore.Fitting.Fitting import Fitter
from easyDiffractionLib import Phases
from easyDiffractionLib.interface import InterfaceFactory as Calculator
from easyDiffractionLib.Profiles.P1D import PDFParameters
from easyDiffractionLib.Jobs import Powder1DCW
from easyDiffractionLib.Interfaces.pdffit2 import readGRData


data_fname = "Ni-xray.gr"
# data_fname = os.path.realpath('examples\\PDF\\Ni-xray.gr')
data = readGRData(data_fname)

phase_cif_name = "Ni.cif"
# phase_cif_name = "examples\\PDF\\Ni.cif"
phases = Phases.from_cif_file(phase_cif_name)

parameters = PDFParameters()

calculator = Calculator()
calculator.switch("Pdffit2")

job = Powder1DCW('Ni', parameters=parameters, phases=phases, interface=calculator)

fitter = Fitter(job, calculator.fit_func)

parameters = job.parameters
parameters.qmax = 30
parameters.qdamp = 0.063043
parameters.wavelength = 1.9122
parameters.delta2 = 2.253193
parameters.delta1 = 0.0

pattern = job.pattern
# pattern.zero_shift = 0.16

phase = job.phases[0]
# phase.scale = 5.0
job.phases[0].atoms[0].adp.Uiso = 0.005445
job.phases[0].scale = 0.366013

x_data = data[:, 0]

y_data = job.create_simulation(x_data)

# plotting
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


