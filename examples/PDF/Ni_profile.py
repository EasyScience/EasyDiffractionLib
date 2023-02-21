
import os

from easyCore.Fitting.Fitting import Fitter
from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Phases
from easyDiffractionLib.interface import InterfaceFactory as Calculator
from easyDiffractionLib.Profiles.P1D import PDFParameters
from easyDiffractionLib.Jobs import Powder1DCW
from easyDiffractionLib.Interfaces.pdffit2 import readGRData


data_fname = "D:\\projects\\easyScience\\easyDiffractionLib\\examples\\PDF\\Ni-xray.gr"
# data_fname = os.path.realpath('Ni-xray.gr')
data = readGRData(data_fname)

phase_cif_name = "D:\\projects\\easyScience\\easyDiffractionLib\\examples\\PDF\\Ni.cif"
# phase_cif_name = "Ni.cif"
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


