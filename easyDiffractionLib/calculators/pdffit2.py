import os
from easyCore import np

from diffpy.pdffit2 import PdfFit as pdf_calc
from diffpy.structure.parsers.p_cif import P_cif as cif_parser
from diffpy.pdffit2 import redirect_stdout

# silence the C++ engine output
redirect_stdout(open(os.path.devnull, 'w'))

class Pdffit2:

    def __init__(self):
        self.pattern = None
        self.conditions = {
            "qmax": 30.0,
            "qdamp": 0.01,
            "delta1": 0.0,
            "delta2": 0.0,
            "qbroad": 0.0,
            "spdiameter": 8.0,
        }
        self.background = None
        self.phases = None
        self.storage = {}
        self.current_crystal = {}
        self.model = None
        self.type = "N"
        self.cif_string = ""

    def conditionsSet(self, model):
        self.model = model

    def conditionsReturn(self, _, name):
        return self.conditions.get(name)

    def calculate(self, x_array: np.ndarray) -> np.ndarray:
        """
        For a given x calculate the corresponding y.

        :param x_array: array of data points to be calculated
        :param model_name: Name for the model
        :return: points calculated at `x`
        """
        P = pdf_calc()

        structure = cif_parser().parse(self.cif_string)
        P.add_structure(structure)

        # extract conditions from the model
        qmax = self.model.qmax.raw_value
        qdamp = self.model.qdamp.raw_value
        delta1 = self.model.delta1.raw_value
        delta2 = self.model.delta2.raw_value
        qbroad = self.model.qbroad.raw_value
        spdiameter = self.model.spdiameter.raw_value

        stype = self.type

        # scale
        scale = self.phases[0].scale.raw_value
        P.setvar("pscale", scale)
        P.setvar("delta1", delta1)
        P.setvar("delta2", delta2)
        P.setvar("spdiameter", spdiameter)

        # set the Uiso (current limitation to isotropic ADP)
        for i_atom, atom in enumerate(self.phases[0].atoms):
            Uiso = atom.adp.Uiso.raw_value
            for i in range(1,4):
                u_str = "u{}{}({})".format(i, i, i_atom+1)
                P.setvar(u_str, Uiso)

        # Errors
        noise_array = np.zeros(len(x_array))

        # P.read_data_string(x_array, stype, qmax, qdamp)
        # Assign the data to the pdf calculator
        P.read_data_lists(stype, qmax, qdamp, list(x_array), list(noise_array))
        # qbroad must be set after read_data_string
        P.setvar("qbroad", qbroad)

        P.calc()

        pdf = np.array(P.getpdf_fit())

        return pdf


