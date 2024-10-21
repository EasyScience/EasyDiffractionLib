import cryspy
import matplotlib.pyplot as plt
import os

fname = 'cryspy_unpolarized_tof_powder_Si.rcif'
#fname = 'rhochi_unpolarized_tof_powder_CeCuAl.rcif'
fpath = fname  # os.path.abspath(os.path.join(os.path.dirname(__file__), fname))

cryspy_obj = cryspy.load_file(fpath)
cryspy_dict = cryspy_obj.get_dictionary()
cryspy_in_out_dict = {}
cryspy.procedure_rhochi.rhochi_by_dictionary.rhochi_calc_chi_sq_by_dictionary(
            cryspy_dict,
            dict_in_out=cryspy_in_out_dict,
            flag_use_precalculated_data=False,
            flag_calc_analytical_derivatives=False)
