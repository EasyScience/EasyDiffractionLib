from __future__ import annotations

__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import TypeVar, List, Optional, Union, TYPE_CHECKING, ClassVar

from easyCore.Datasets.xarray import xr
from easyCore.Objects.ObjectClasses import BaseObj, Parameter
from easyDiffractionLib.Profiles.common import JobSetup, _DataClassBase
from easyDiffractionLib.components.polarization import PolarizedBeam
from easyDiffractionLib.elements.Backgrounds.Background import BackgroundContainer

T = TypeVar("T")

if TYPE_CHECKING:
    from easyCore.Utils.typing import iF


class Powder1DSim(_DataClassBase):
    def __init__(self, dataset):
        super(Powder1DSim, self).__init__(dataset)
        self._simulation_prefix = "sim_"
        self.name = ""

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
        exps = [
            a
            for a in self._dataset.variables.keys()
            if not a.startswith(self.simulation_prefix) and not a in self._dataset.dims
        ]
        return exps


class Powder1DPolSim(Powder1DSim):
    def __init__(self, dataset):
        super(Powder1DPolSim, self).__init__(dataset)


class Powder1DPolExp(Powder1DExp):
    def __init__(self, dataset, simulation_prefix):
        super(Powder1DPolExp, self).__init__(dataset, simulation_prefix)


class Powder1DParameters(BaseObj):
    _name = "1DPowderProfile"
    _defaults = {
        "zero_shift": {
            "name": "zero_shift",
            "units": "degree",
            "value": 0.0,
            "fixed": True,
        },
        "scale": {
            "name": "scale",
            "value": 1,
            "fixed": True,
            "enabled": False,
        },
    }

    zero_shift: ClassVar[Parameter]
    scale: ClassVar[Parameter]
    backgrounds: ClassVar[BackgroundContainer]

    def __init__(
        self,
        zero_shift: Optional[Union[Parameter, float]] = None,
        scale: Optional[Union[Parameter, float]] = None,
        backgrounds: Optional[BackgroundContainer] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):
        super().__init__(
            self.__class__.__name__,
            **{k: Parameter(**self._defaults[k]) for k in self._defaults.keys()},
            backgrounds=BackgroundContainer(),
            **kwargs,
        )
        if zero_shift is not None:
            self.zero_shift = zero_shift
        if scale is not None:
            self.scale = scale
        if backgrounds is not None:
            self.backgrounds = backgrounds

        self.name = self._name
        self.interface = interface


class PolPowder1DParameters(Powder1DParameters):
    polarization: ClassVar[Parameter]
    efficiency: ClassVar[Parameter]

    _defaults = {
        "polarization": PolarizedBeam._defaults["polarization"],
        "efficiency": PolarizedBeam._defaults["efficiency"],
    }
    _defaults.update(Powder1DParameters._defaults)

    def __init__(
        self,
        zero_shift: Optional[Union[Parameter, float]] = None,
        scale: Optional[Union[Parameter, float]] = None,
        backgrounds: Optional[BackgroundContainer] = None,
        polarization: Optional[Union[Parameter, float]] = None,
        efficiency: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
        **kwargs,
    ):
        super().__init__(
            zero_shift=zero_shift,
            scale=scale,
            backgrounds=backgrounds,
            interface=interface,
            polarization=Parameter(**self._defaults["polarization"]),
            efficiency=Parameter(**self._defaults["efficiency"]),
            **kwargs,
        )

        if polarization is not None:
            self.polarization = polarization
        if efficiency is not None:
            self.efficiency = efficiency


class Instrument1DCWParameters(BaseObj):
    _name = "InstrumentalParameters"
    _defaults = {
        "wavelength": {
            "name": "wavelength",
            "units": "angstrom",
            "value": 1.54056,
            "fixed": True,
        },
        "resolution_u": {
            "name": "resolution_u",
            "value": 0.0002,
            "fixed": True,
        },
        "resolution_v": {
            "name": "resolution_v",
            "value": -0.0002,
            "fixed": True,
        },
        "resolution_w": {
            "name": "resolution_w",
            "value": 0.012,
            "fixed": True,
        },
        "resolution_x": {
            "name": "resolution_x",
            "value": 0.0,
            "fixed": True,
        },
        "resolution_y": {
            "name": "resolution_y",
            "value": 0.0,
            "fixed": True,
        },
    }

    wavelength: ClassVar[Parameter]
    resolution_u: ClassVar[Parameter]
    resolution_v: ClassVar[Parameter]
    resolution_w: ClassVar[Parameter]
    resolution_x: ClassVar[Parameter]
    resolution_y: ClassVar[Parameter]

    def __init__(
        self,
        wavelength: Optional[Union[Parameter, float]] = None,
        resolution_u: Optional[Union[Parameter, float]] = None,
        resolution_v: Optional[Union[Parameter, float]] = None,
        resolution_w: Optional[Union[Parameter, float]] = None,
        resolution_x: Optional[Union[Parameter, float]] = None,
        resolution_y: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
    ):
        super(Instrument1DCWParameters, self).__init__(
            name=self.__class__.__name__,
            **{k: Parameter(**self._defaults[k]) for k in self._defaults.keys()},
        )

        if wavelength is not None:
            self.wavelength = wavelength
        if resolution_u is not None:
            self.resolution_u = resolution_u
        if resolution_v is not None:
            self.resolution_v = resolution_v
        if resolution_v is not None:
            self.resolution_v = resolution_v
        if resolution_w is not None:
            self.resolution_w = resolution_w
        if resolution_x is not None:
            self.resolution_x = resolution_x
        if resolution_y is not None:
            self.resolution_y = resolution_y
        self.name = self._name
        self.interface = interface


class Instrument1DTOFParameters(BaseObj):
    _name = "InstrumentalParameters"
    _defaults = {
        "ttheta_bank": {
            "name": "ttheta_bank",
            "units": "deg",
            "value": 145.00,
            "fixed": True,
        },
        "dtt1": {
            "name": "dtt1",
            "units": "deg",
            "value": 6167.24700,
            "fixed": True,
        },
        "dtt2": {
            "name": "dtt2",
            "units": "deg",
            "value": -2.28000,
            "fixed": True,
        },
        "sigma0": {
            "name": "sigma0",
            "value": 0.409,
            "fixed": True,
        },
        "sigma1": {
            "name": "sigma1",
            "value": 8.118,
            "fixed": True,
        },
        "sigma2": {
            "name": "sigma2",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma0": {
            "name": "gamma0",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma1": {
            "name": "gamma1",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "gamma2": {
            "name": "gamma2",
            "value": 0.0,
            "fixed": True,
            "enabled": False,
        },
        "alpha0": {
            "name": "alpha0",
            "value": 0.0,
            "fixed": True,
        },
        "alpha1": {
            "name": "alpha1",
            "value": 0.29710,
            "fixed": True,
        },
        "beta0": {
            "name": "beta0",
            "value": 0.04182,
            "fixed": True,
        },
        "beta1": {
            "name": "beta1",
            "value": 0.00224,
            "fixed": True,
        },
    }

    ttheta_bank: ClassVar[Parameter]
    dtt1: ClassVar[Parameter]
    dtt2: ClassVar[Parameter]
    sigma0: ClassVar[Parameter]
    sigma1: ClassVar[Parameter]
    sigma2: ClassVar[Parameter]
    gamma0: ClassVar[Parameter]
    gamma1: ClassVar[Parameter]
    gamma2: ClassVar[Parameter]
    alpha0: ClassVar[Parameter]
    alpha1: ClassVar[Parameter]
    beta0: ClassVar[Parameter]
    beta1: ClassVar[Parameter]

    def __init__(
        self,
        ttheta_bank: Optional[Union[Parameter, float]] = None,
        dtt1: Optional[Union[Parameter, float]] = None,
        dtt2: Optional[Union[Parameter, float]] = None,
        sigma0: Optional[Union[Parameter, float]] = None,
        sigma1: Optional[Union[Parameter, float]] = None,
        sigma2: Optional[Union[Parameter, float]] = None,
        gamma0: Optional[Union[Parameter, float]] = None,
        gamma1: Optional[Union[Parameter, float]] = None,
        gamma2: Optional[Union[Parameter, float]] = None,
        alpha0: Optional[Union[Parameter, float]] = None,
        alpha1: Optional[Union[Parameter, float]] = None,
        beta0: Optional[Union[Parameter, float]] = None,
        beta1: Optional[Union[Parameter, float]] = None,
        interface: Optional[iF] = None,
    ):
        super().__init__(
            self.__class__.__name__,
            **{k: Parameter(**self._defaults[k]) for k in self._defaults.keys()},
        )

        if ttheta_bank is not None:
            self.ttheta_bank = ttheta_bank
        if dtt1 is not None:
            self.dtt1 = dtt1
        if dtt2 is not None:
            self.dtt2 = dtt2
        if sigma0 is not None:
            self.sigma0 = sigma0
        if sigma1 is not None:
            self.sigma1 = sigma1
        if sigma2 is not None:
            self.sigma2 = sigma2
        if gamma0 is not None:
            self.gamma0 = gamma0
        if gamma1 is not None:
            self.gamma1 = gamma1
        if gamma2 is not None:
            self.gamma2 = gamma2
        if alpha0 is not None:
            self.alpha0 = alpha0
        if alpha1 is not None:
            self.alpha1 = alpha1
        if beta0 is not None:
            self.beta0 = beta0
        if beta1 is not None:
            self.beta1 = beta1

        self.name = self._name
        self.interface = interface


class Instrument1DCWPolParameters(Instrument1DCWParameters):
    pass


Unpolarized1DClasses = JobSetup(
    [Powder1DSim, Powder1DExp], Powder1DParameters, Instrument1DCWParameters
)

Unpolarized1DTOFClasses = JobSetup(
    [Powder1DSim, Powder1DExp], Powder1DParameters, Instrument1DTOFParameters
)

Polarized1DClasses = JobSetup(
    [Powder1DSim, Powder1DExp], PolPowder1DParameters, Instrument1DCWParameters
)

Polarized1DTOFClasses = JobSetup(
    [Powder1DSim, Powder1DExp], PolPowder1DParameters, Instrument1DTOFParameters
)
