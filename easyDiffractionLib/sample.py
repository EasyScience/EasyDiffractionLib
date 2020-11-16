__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import os, tempfile
from typing import Union

from easyCore.Objects.Base import BaseObj
from easyDiffractionLib import Crystal, Crystals
from easyDiffractionLib.Elements.Experiments.Experiment import Pars1D
from easyDiffractionLib.Elements.Experiments.Pattern import Pattern1D


class Sample(BaseObj):
    def __init__(self, phases: Union[Crystal, Crystals] = None,
                 parameters=None, pattern=None,
                 interface=None, name: str = 'easySample'):
        if isinstance(phases, Crystal):
            phases = Crystals('Phases', phases)
        elif phases is None:
            phases = Crystals('Phases')

        if not isinstance(phases, Crystals):
            raise AttributeError('`phases` must be a Crystal or Crystals')

        if pattern is None:
            pattern = Pattern1D.default()

        super(Sample, self).__init__(name, _phases=phases, _parameters=parameters, _pattern=pattern)

        self.interface = interface
        self.filename = os.path.join(tempfile.gettempdir(), 'easydiffraction_temp.cif')
        print(f"Temp CIF: {self.filename}")
        self.output_index = None
        self._updateInterface()

    def _updateInterface(self, interface_call: str = None):
        if self.interface is not None:
            if self._phases is not None and \
                    (interface_call is None or interface_call == 'phases'):
                self.interface.generate_bindings(self._phases, self, ifun=self.interface.generate_sample_binding)
            if self._parameters is not None and \
                    (interface_call is None or interface_call == 'pars'):
                self.interface.generate_bindings(self._parameters, ifun=self.interface.generate_instrument_binding)
                self.interface.generate_bindings(self._pattern, self._pattern, ifun=self.interface.generate_pattern_binding)
            if len(self._pattern.backgrounds) > 0 and \
                    self.interface is not None and \
                    (interface_call is None or interface_call == 'background'):
                # TODO: At the moment we're only going to support 1 BG as there are no experiments yet.
                self.interface.generate_bindings(self._pattern.backgrounds, self._pattern.backgrounds[0], ifun=self.interface.generate_background_binding)

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)
        self._updateInterface(interface_call='background')

    def remove_background(self, background):
        if background.linked_experiment.raw_value in self._pattern.backgrounds.linked_experiments:
            del self._pattern.backgrounds[background.linked_experiment.raw_value]
            self._updateInterface(interface_call='background')
        else:
            raise ValueError

    @property
    def backgrounds(self):
        return self._pattern.backgrounds

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
        self._updateInterface(interface_call='phases')

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        if not isinstance(value, Pars1D):
            raise ValueError
        self._parameters = value
        self._updateInterface(interface_call='pars')

    def update_bindings(self):
        self._updateInterface()

    @property
    def pattern(self):
        return self._pattern
