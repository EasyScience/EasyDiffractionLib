__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyDiffractionLib import Crystal, Crystals
from easyDiffractionLib.Elements.Instruments.Instrument import Pattern
from easyDiffractionLib.Elements.Backgrounds.Linear import Line
from tempfile import NamedTemporaryFile


class Sample:
    def __init__(self, phases=None, parameters=None, interface=None):
        if isinstance(phases, Crystal):
            phases = Crystals('Generated', phases)
        elif phases is None:
            phases = Crystals('Generated')

        if not isinstance(phases, Crystals):
            raise AttributeError('`phases` must be a Crystal or Crystals')
        self._phases = phases
        self.background = Line()
        self._parameters = parameters
        self.interface = interface
        self.filename = './temp.cif'
        self._updateInterface()

    def _updateInterface(self):
        if self.interface is not None:
            if self._phases is not None:
                self.interface.generate_bindings(self._phases, self, ifun=self.interface.generate_sample_binding)
            if self._parameters is not None:
                self.interface.generate_bindings(self._parameters, ifun=self.interface.generate_instrument_binding)

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    @property
    def phases(self):
        return self._phases

    @phases.setter
    def phases(self, value):
        if isinstance(value, Crystal):
            self._phases.append(value)
        elif isinstance(value, Crystals):
            self._phases = value
        else:
            raise ValueError
        self._updateInterface()

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        if not isinstance(value, Pattern):
            raise ValueError
        self._parameters = value
        self._updateInterface()

    @property
    def name(self):
        name = ''
        if isinstance(self.phase, Crystal):
            name = self.phase.name
        return name

    def update_bindings(self):
        self._updateInterface()
