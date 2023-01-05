
import os

from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Phases
from easyDiffractionLib.interface import InterfaceFactory as Calculator
from easyDiffractionLib.Profiles.P1D import Powder1DParameters, PDFParameters
from easyDiffractionLib.Interfaces.pdffit2 import readGRData


calculator = Calculator()
calculator.switch("Pdffit2")

data_fname = os.path.realpath('Ni-xray.gr')
data = readGRData(data_fname)

cif_fname = os.path.realpath('Ni.cif')
phases = Phases.from_cif_file(cif_fname)

parameters = PDFParameters()

# PDF parameters
parameters.qmax = 70
parameters.qdamp = 0.01

pattern = Powder1DParameters()

S = Sample(phases=phases, parameters=parameters, pattern=pattern)
S.interface = calculator

# x_data = np.linspace(0.5, 30, 2000)
x_data = data[:, 0]

# profile calculation
y_data = calculator.fit_func(x_data)


###########################################################################
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