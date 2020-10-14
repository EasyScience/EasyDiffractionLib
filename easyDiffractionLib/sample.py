__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyDiffractionLib import Crystal
from easyDiffractionLib.Elements.Instruments.Instrument import Pattern
from easyDiffractionLib.Elements.Backgrounds.Linear import Line
from tempfile import NamedTemporaryFile


class Sample:
    def __init__(self, phase=None, parameters=None, interface=None):
        self._phase = phase
        self.background = Line()
        self._parameters = parameters
        self.interface = interface
        self.filename = './temp.cif'
        self._updateInterface()

    def _updateInterface(self):
        if self.interface is not None:
            if self._phase is not None:
                self.interface.generate_bindings(self._phase, self, ifun=self.interface.generate_sample_binding)
            if self._parameters is not None:
                self.interface.generate_bindings(self._parameters, ifun=self.interface.generate_instrument_binding)

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value):
        if not isinstance(value, Crystal):
            raise ValueError
        self._phase = value
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
