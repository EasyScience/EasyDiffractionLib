__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from typing import TypeVar, List

from easyCore.Datasets.xarray import xr
from easyCore.Objects.Base import BaseObj, Parameter
from copy import deepcopy
from easyCore.Utils.json import MontyDecoder
from easyDiffractionLib.Elements.Backgrounds.Background import BackgroundContainer
from easyDiffractionLib.Profiles.common import JobSetup, _DataClassBase

_decoder = MontyDecoder()
T = TypeVar('T')


class Powder1DSim(_DataClassBase):
    def __init__(self, dataset):
        super(Powder1DSim, self).__init__(dataset)
        self._simulation_prefix = 'sim_'
        self.name = ''

    def add_simulation(self, simulation_name, simulation):
        self._dataset[self._simulation_prefix + simulation_name] = simulation

    # @property
    # def simulations(self) -> xr.Dataset:
    #     temp_dataset = xr.Dataset()
    #     for sim in self.simulation_names:
    #         temp_dataset[sim] = self._dataset[sim]
    #     return temp_dataset
    #
    # @property
    # def simulation_names(self) -> List[str]:
    #     sims = [a for a in self._dataset.variables.keys() if a.startswith(self._simulation_prefix)]
    #     return sims


class Powder1DExp(_DataClassBase):
    def __init__(self, dataset, simulation_prefix):
        super(Powder1DExp, self).__init__(dataset)
        self.simulation_prefix = simulation_prefix

    @property
    def experiments(self) -> xr.Dataset:
        temp_dataset = xr.Dataset()
        for exp in self.experiment_names:
            temp_dataset[exp] = self._dataset[exp]
        return temp_dataset

    @property
    def experiment_names(self) -> List[str]:
        exps = [a for a in self._dataset.variables.keys()
                if not a.startswith(self.simulation_prefix) and
                not a in self._dataset.dims]
        return exps


class Powder1DPolSim(Powder1DSim):
    def __init__(self, dataset):
        super(Powder1DPolSim, self).__init__(dataset)


class Powder1DPolExp(Powder1DExp):
    def __init__(self, dataset, simulation_prefix):
        super(Powder1DPolExp, self).__init__(dataset, simulation_prefix)


class Powder1DParameters(BaseObj):
    _name = '1DPowderProfile'
    _defaults = {
        'zero_shift': {
            '@module': 'easyCore.Objects.Base',
            '@class': 'Parameter',
            '@version': '0.0.1',
            'name': 'zero_shift',
            'units': 'degree',
            'value': 0.0,
            'fixed': True
        },
        'scale':   {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'scale',
            'value':    1,
            'fixed': True
        },
        'backgrounds': {
            '@module': 'easyDiffractionLib.Elements.Backgrounds.Background',
            '@class': 'BackgroundContainer',
            '@version': '0.0.1',
            'data': [],
        }
    }

    def __init__(self,
                 zero_shift: Parameter, scale: Parameter,
                 backgrounds: BackgroundContainer,
                 interface=None):
        super().__init__(self.__class__.__name__,
                         zero_shift=zero_shift, scale=scale,
                         backgrounds=backgrounds)
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  zero_shift: float = _defaults['zero_shift']['value'],
                  scale: float = _defaults['scale']['value']
                  ):
        defaults = deepcopy(cls._defaults)
        defaults['zero_shift']['value'] = zero_shift
        zero_shift = _decoder.process_decoded(defaults['zero_shift'])
        defaults['scale']['value'] = scale
        scale = _decoder.process_decoded(defaults['scale'])
        backgrounds = BackgroundContainer()
        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        zero_shift = _decoder.process_decoded(defaults['zero_shift'])
        scale = _decoder.process_decoded(defaults['scale'])
        backgrounds = BackgroundContainer()

        return cls(zero_shift=zero_shift, scale=scale, backgrounds=backgrounds)


class PolPowder1DParameters(Powder1DParameters):
    pass


class Instrument1DParameters(BaseObj):
    _name = 'InstrumentalParameters'
    _defaults = {
        'wavelength':   {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'wavelength',
            'units':    'angstrom',
            'value':    1.54056,
            'fixed': True
        },
        'resolution_u': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_u',
            'value':    0.0002,
            'fixed': True
        },
        'resolution_v': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_v',
            'value':    -0.0002,
            'fixed': True

        },
        'resolution_w': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_w',
            'value':    0.012,
            'fixed': True

        },
        'resolution_x': {
            '@module':  'easyCore.Objects.Base',
            '@class':   'Parameter',
            '@version': '0.0.1',
            'name':     'resolution_x',
            'value':    0.0,
            'fixed': True
        },
        'resolution_y': {
            '@module': 'easyCore.Objects.Base',
            '@class': 'Parameter',
            '@version': '0.0.1',
            'name': 'resolution_y',
            'value': 0.0,
            'fixed': True
        }
    }

    def __init__(self,
                 wavelength: Parameter,
                 resolution_u: Parameter, resolution_v: Parameter, resolution_w: Parameter,
                 resolution_x: Parameter, resolution_y: Parameter,
                 interface=None):
        super().__init__(self.__class__.__name__,
                         wavelength=wavelength,
                         resolution_u=resolution_u, resolution_v=resolution_v, resolution_w=resolution_w,
                         resolution_x=resolution_x, resolution_y=resolution_y)
        self.name = self._name
        self.interface = interface

    @classmethod
    def from_pars(cls,
                  wavelength: float = _defaults['wavelength']['value'],
                  resolution_u: float = _defaults['resolution_u']['value'],
                  resolution_v: float = _defaults['resolution_v']['value'],
                  resolution_w: float = _defaults['resolution_w']['value'],
                  resolution_x: float = _defaults['resolution_x']['value'],
                  resolution_y: float = _defaults['resolution_y']['value']
                  ):
        defaults = deepcopy(cls._defaults)
        defaults['wavelength']['value'] = wavelength
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        defaults['resolution_u']['value'] = resolution_u
        resolution_u = _decoder.process_decoded(defaults['resolution_u'])
        defaults['resolution_v']['value'] = resolution_v
        resolution_v = _decoder.process_decoded(defaults['resolution_v'])
        defaults['resolution_w']['value'] = resolution_w
        resolution_w = _decoder.process_decoded(defaults['resolution_w'])
        defaults['resolution_x']['value'] = resolution_x
        resolution_x = _decoder.process_decoded(defaults['resolution_x'])
        defaults['resolution_y']['value'] = resolution_y
        resolution_y = _decoder.process_decoded(defaults['resolution_y'])
        return cls(wavelength=wavelength,
                   resolution_u=resolution_u, resolution_v=resolution_v, resolution_w=resolution_w,
                   resolution_x=resolution_x, resolution_y=resolution_y)

    @classmethod
    def default(cls):
        defaults = deepcopy(cls._defaults)
        wavelength = _decoder.process_decoded(defaults['wavelength'])
        resolution_u = _decoder.process_decoded(defaults['resolution_u'])
        resolution_v = _decoder.process_decoded(defaults['resolution_v'])
        resolution_w = _decoder.process_decoded(defaults['resolution_w'])
        resolution_x = _decoder.process_decoded(defaults['resolution_x'])
        resolution_y = _decoder.process_decoded(defaults['resolution_y'])
        return cls(wavelength=wavelength,
                   resolution_u=resolution_u, resolution_v=resolution_v, resolution_w=resolution_w,
                   resolution_x=resolution_x, resolution_y=resolution_y)


class Instrument1DPolParameters(Instrument1DParameters):
    pass


Unpolarized1DClasses = JobSetup([Powder1DSim, Powder1DExp],
                                Powder1DParameters,
                                Instrument1DParameters)
