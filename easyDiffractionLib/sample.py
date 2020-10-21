__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from typing import Union

from easyCore.Objects.Base import BaseObj
from easyDiffractionLib import Crystal, Crystals
from easyDiffractionLib.Elements.Instruments.Instrument import Pattern
from easyDiffractionLib.Elements.Backgrounds.Linear import Line


class Sample(BaseObj):
    def __init__(self, phases: Union[Crystal, Crystals] = None, parameters=None, interface=None, name: str = 'easySample'):
        if isinstance(phases, Crystal):
            phases = Crystals('Phases', phases)
        elif phases is None:
            phases = Crystals('Phases')

        if not isinstance(phases, Crystals):
            raise AttributeError('`phases` must be a Crystal or Crystals')
        
        super(Sample, self).__init__(name, _phases=phases, _parameters=parameters)
        self.background = Line()
        self.interface = interface
        self.filename = './temp.cif'
        self.output_index = None
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
            value = Crystals('Phases', value)
        if not isinstance(value, Crystals):
            raise ValueError
        self._phases = value
        self._borg.map.add_edge(self, value)
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

    def update_bindings(self):
        self._updateInterface()
