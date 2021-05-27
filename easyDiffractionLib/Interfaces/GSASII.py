__author__ = "github.com/wardsimon"
__version__ = "0.0.2"

from easyCore import borg, np
from ..Interfaces.interfaceTemplate import InterfaceTemplate
from easyCore.Objects.Inferface import ItemContainer
from ..Calculators.GSASII import GSASII as GSAS_calc
from easyDiffractionLib.Elements.Experiments.Experiment import Pars1D
from easyDiffractionLib.Elements.Experiments.Pattern import Pattern1D
from easyDiffractionLib.sample import Sample
from easyDiffractionLib import Lattice, SpaceGroup, Site, Phases


class GSASII(InterfaceTemplate):
    """
    A simple FILE interface using GSASII
    """

    _sample_link = {
        'filename': 'filename'}

    _crystal_link = {
        "length_a": "length_a",
        "length_b": "length_b",
        "length_c": "length_c",
        "angle_alpha": "angle_alpha",
        "angle_beta": "angle_beta",
        "angle_gamma": "angle_gamma",
    }

    _instrument_link = {
        'resolution_u': 'u_resolution',
        'resolution_v': 'v_resolution',
        'resolution_w': 'w_resolution',
        'resolution_x': 'x_resolution',
        'resolution_y': 'y_resolution',
        'wavelength': 'wavelength'
    }

    _atom_link = {
       'label': 'label',
       'specie': 'specie',
       'fract_x': 'fract_x',
       'fract_y': 'fract_y',
       'fract_z': 'fract_z',
       'occupancy': 'occupancy',
       'adp_type': 'adp_type',
       'Uiso': 'Uiso',
       'Biso': 'Biso',
       'Uani': 'Uani',
       'Bani': 'Bani'
    }
    _pattern_link = {
        'scale': 'scale',
        'x_offset': 'x_offset'
    }

    name = 'GSASII'

    def __init__(self):
        self.calculator = GSAS_calc()
        self._phase = None
        self._filename = None

    def create(self, model):
        r_list = []
        t_ = type(model)
        model_key = self.__identify(model)
        if issubclass(t_, Pars1D):
            # These parameters are linked to the Resolution and Setup CFML objects. Note that we can set the job type!
            self.calculator.createConditions(job_type='N')
            keys = self._instrument_link.copy()
            r_list.append(
                ItemContainer(model_key, keys,
                              self.calculator.conditionsReturn,
                              self.calculator.conditionsUpdate)
            )
        elif issubclass(t_, Pattern1D):
            # These parameters do not link directly to CFML objects.
            self.calculator.pattern = model
        elif issubclass(t_, Lattice):
            keys = self._crystal_link.copy()
            r_list.append(
                ItemContainer(model_key, keys,
                              self.get_value,
                              self.dump_cif)
            )
        elif issubclass(t_, SpaceGroup):
            keys = {'_space_group_HM_name': '_space_group_HM_name'}
            r_list.append(
                ItemContainer(model_key, keys,
                              self.get_value,
                              self.dump_cif)
            )
        elif issubclass(t_, Site):
            keys = self._atom_link.copy()
            r_list.append(ItemContainer(model_key, keys,
                                        self.get_value,
                                        self.dump_cif))
        elif issubclass(t_, Phases):
            self._phase = model
        elif issubclass(t_, Sample):
            self._filename = model.filename
            self.calculator.filename = model.filename
            self.dump_cif()
        else:
            if self._borg.debug:
                print(f"I'm a: {type(model)}")
        return r_list

    def link_atom(self, crystal_obj, atom):
        pass

    def remove_atom(self, crystal_obj, atom):
        pass

    def add_phase(self, phases_obj, phase_obj):
        pass

    def remove_phase(self, phases_obj, phase_obj):
        pass

    def fit_func(self, x_array: np.ndarray) -> np.ndarray:
        """
        Function to perform a fit
        :param x_array: points to be calculated at
        :type x_array: np.ndarray
        :return: calculated points
        :rtype: np.ndarray
        """
        return self.calculator.calculate(x_array)

    def get_hkl(self, x_array: np.ndarray = None) -> dict:
        return self.calculator.get_hkl(x_array)
    
    def dump_cif(self, *args, **kwargs):
        if self._filename is None:
            return
        with open(self._filename, 'w') as fid:
            fid.write(str(self._phase.cif))

    def get_value(self, key, item_key):
        item = borg.map.get_item_by_key(key)
        return getattr(item, item_key).raw_value

    @staticmethod
    def __identify(obj):
        return borg.map.convert_id_to_key(obj)
