from easyCore import np
from easyCore.Fitting.Fitting import Fitter

# esyScience, diffraction
from easyDiffractionLib import Phases
from easyDiffractionLib.sample import Sample
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters as CWParams
from bokeh.io import show, output_notebook
from bokeh.plotting import figure

cif_fname = r"D:\projects\easyScience\easyDiffractionLib\examples\PbSO4.cif"
phases = Phases.from_cif_file(cif_fname)
FIGURE_WIDTH = 990
FIGURE_HEIGHT = 300
fig = figure(width=FIGURE_WIDTH, height=FIGURE_HEIGHT)

calculator = InterfaceFactory(interface_name='CrysPy')

job = Sample(phases=phases, parameters=CWParams(), interface=calculator)
x = np.linspace(20, 170, 500)
y = calculator.fit_func(x)

fitter = Fitter(job, calculator.fit_func)

job.interface.switch('CrysFML', fitter=fitter)
y_n = calculator.fit_func(x)
fig.line(x, y_n, legend_label='Neutron Simulation', color='orangered', line_width=2)
show(fig)

fig2 = figure(width=FIGURE_WIDTH, height=FIGURE_HEIGHT)
job.interface.switch('CrysFML - Xray', fitter=fitter)
y_xray = calculator.fit_func(x)

hkl = job.interface.get_hkl(x_array=x, encoded_name=True)

fig2.line(x, y_xray, legend_label='XRay Simulation', color='orangered', line_width=2)
show(fig2)

pass