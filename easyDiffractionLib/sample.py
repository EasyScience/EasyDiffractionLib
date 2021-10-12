__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from easyCore.Datasets.xarray import xr

from easyCore.Objects.Base import BaseObj
from easyCore.Utils.UndoRedo import property_stack_deco

from easyDiffractionLib import Phase, Phases
from easyDiffractionLib.Profiles.P1D import Instrument1DCWParameters, Instrument1DTOFParameters
from easyDiffractionLib.interface import InterfaceFactory
from easyDiffractionLib.Profiles.P1D import Powder1DParameters as Pattern1D

class Runner:
    def __init__(self):
        self._data = xr.Dataset()
        self._jobs = {}
        self._instrumental_parameters = []
        self._instrumental_parameters_link = {}
        self._experimental_parameters = []
        self._experimental_parameters_link = {}
        self._phases = []
        self._phase_link = {}

class Sample(BaseObj):
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

        self.filename = os.path.join(tempfile.gettempdir(), 'easydiffraction_temp.cif')
        print(f"Temp CIF: {self.filename}")
        self.output_index = None
        if calculator is not None:
            self.interface = calculator
        elif interface is not None:
            self.interface = interface
        else:
            self.interface = InterfaceFactory()

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
            raise NotImplementedError
        job = job_type(name, self._data)
        self._jobs[name] = {
            'object': job,
            'phases': job.phases,
            'instrumental_parameters': job.parameters,
            'experimental_parameters': job.pattern
        }

    @property
    def phases(self):
        return [phase.name for phase in self._phases]

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
    def jobs(self):
        return {key: job['object'] for key, job in self._jobs.items()}

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
        type_str = 'Npowder1D'
        if isinstance(self._parameters, Instrument1DCWParameters):
            type_str += 'CW'
        elif isinstance(self._parameters, Instrument1DTOFParameters):
            type_str += 'TOF'
        else:
            raise TypeError(f'Experiment is of unknown type: {type(self._parameters)}')
        return type_str
