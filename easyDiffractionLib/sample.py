__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import os, tempfile
from typing import Union, ClassVar

from easyCore.Objects.Base import BaseObj
from easyCore.Utils.UndoRedo import property_stack_deco

from easyDiffractionLib import Phase, Phases
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters, Instrument1DTOFParameters
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Interfaces.types import Powder, Neutron
from easyDiffractionLib.Profiles.P1D import Powder1DParameters as Pattern1D
from easyDiffractionLib.Profiles.P1D import PolPowder1DParameters as Pattern1D_Pol


class Sample(BaseObj):

    _phases: ClassVar[Phases]
    _parameters: ClassVar
    _pattern: ClassVar

    def __init__(self, phases: Union[Phase, Phases] = None,
                 parameters=None, pattern=None, calculator=None,
                 interface=None, name: str = 'easySample'):
        if isinstance(phases, Phase):
            phases = Phases('Phases', phases)
        elif phases is None:
            phases = Phases('Phases')

        if not isinstance(phases, Phases):
            raise AttributeError('`phases` must be a Crystal or Crystals')

        if parameters is None:
            parameters = Instrument1DCWParameters.default()

        if pattern is None:
            pattern = Pattern1D.default()

        super(Sample, self).__init__(name, _phases=phases, _parameters=parameters, _pattern=pattern)

        # Set bases for easy identification
        self._update_bases(Powder)
        self._update_bases(Neutron)

        if isinstance(pattern, Pattern1D):
            from easyDiffractionLib.Interfaces.types import UPol
            self._update_bases(UPol)
        elif isinstance(pattern, Pattern1D_Pol):
            from easyDiffractionLib.Interfaces.types import Pol
            self._update_bases(Pol)

        if isinstance(parameters, Instrument1DCWParameters):
            from easyDiffractionLib.Interfaces.types import CW
            self._update_bases(CW)
        elif isinstance(parameters, Instrument1DTOFParameters):
            from easyDiffractionLib.Interfaces.types import TOF
            self._update_bases(TOF)

        self.filename = os.path.join(tempfile.gettempdir(), 'easydiffraction_temp.cif')
        print(f"Temp CIF: {self.filename}")
        self.output_index = None
        if calculator is not None:
            self.interface = calculator
        elif interface is not None:
            self.interface = interface
        else:
            self.interface = InterfaceFactory()

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, value):
        self._interface = value
        # This is required so that the type is correctly passes.
        if value is not None:
            self.interface.generate_bindings(self)
            self.generate_bindings()

    def get_phase(self, phase_index):
        return self._phases[phase_index]

    def get_background(self, experiment_name: str):
        return self._pattern.backgrounds[experiment_name]

    def set_background(self, background):
        self._pattern.backgrounds.append(background)

    def remove_background(self, background):
        if background.linked_experiment.raw_value in self._pattern.backgrounds.linked_experiments:
            del self._pattern.backgrounds[background.linked_experiment.raw_value]
        else:
            raise ValueError

    @property
    def backgrounds(self):
        return self._pattern.backgrounds

    @property
    def phases(self):
        return self._phases

    @phases.setter
    @property_stack_deco
    def phases(self, value):
        if isinstance(value, Phase):
            self._phases.append(value)
        elif isinstance(value, Phases):
            self._phases = value
            self._borg.map.add_edge(self, value)
            self._phases.interface = self.interface
        else:
            raise ValueError

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    @property_stack_deco
    def parameters(self, value):
        if not isinstance(value, Instrument1DCWParameters):
            raise ValueError
        self._parameters = value
        self._parameters.interface = self._interface

    def update_bindings(self):
        if not self.interface.current_interface.feature_checker(test_str=self.exp_type_str):
            raise AssertionError('The interface is not suitable for this experiment')
        self.generate_bindings()

    @property
    def pattern(self):
        return self._pattern

    def as_dict(self, skip: list = None) -> dict:
        d = super(Sample, self).as_dict(skip=skip)
        del d['_phases']
        del d['_parameters']
        del d['_pattern']
        return d

    @property
    def exp_type_str(self) -> str:
        from easyDiffractionLib.Interfaces.types import Neutron, XRay, Powder, SingleCrystal, Pol, UPol, CW, TOF
        type_str = ''
        if issubclass(self, Neutron):
            type_str += 'N'
        elif issubclass(self, XRay):
            type_str += 'X'

        if issubclass(self, Powder):
            type_str += 'powder'
        elif issubclass(self, SingleCrystal):
            type_str += 'single'

        type_str += '1D'

        if issubclass(self, CW):
            type_str += 'CW'
        elif issubclass(self, TOF):
            type_str += 'TOF'

        if issubclass(self, Pol):
            type_str += 'pol'
        elif issubclass(self, UPol):
            type_str += 'upol'

        return type_str

    def _update_bases(self, new_base):
        base_class = getattr(self, '__old_class__', self.__class__)
        old_bases = set(self.__class__.__bases__)
        old_bases = old_bases - {base_class, *new_base.__mro__}  # This should fix multiple inheritance
        self.__class__.__bases__ = (new_base, *old_bases, base_class)