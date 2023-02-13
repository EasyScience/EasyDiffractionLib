from easyCore import np
from diffpy.pdffit2 import PdfFit as pdf_calc
from diffpy.structure.parsers.p_cif import P_cif as cif_parser


class Pdffit2:

    def __init__(self):
        self.pattern = None
        self.conditions = {
            "qmax": 30.0,
            "qdamp": 0.01,
        }
        self.background = None
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
        qmax = self.model.qmax
        qdamp = self.model.qdamp

        stype = self.type

        # Errors
        noise_array = np.zeros(len(x_array))

        print("QMAX: ", qmax)
        print("QDAMP: ", qdamp)
        # P.read_data_string(x_array, stype, qmax, qdamp)
        # Assign the data to the pdf calculator
        P.read_data_lists(stype, qmax, qdamp, list(x_array), list(noise_array))

        P.calc()

        pdf = P.getpdf_fit()

        return pdf


