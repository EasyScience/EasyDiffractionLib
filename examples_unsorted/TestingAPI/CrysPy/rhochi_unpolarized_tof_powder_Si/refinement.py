import cryspy
import matplotlib.pyplot as plt
import os

fname = 'cryspy_unpolarized_tof_powder_Si.rcif'
#fname = 'rhochi_unpolarized_tof_powder_CeCuAl.rcif'
fpath = fname  # os.path.abspath(os.path.join(os.path.dirname(__file__), fname))

cryspy_obj = cryspy.load_file(fpath)
res = cryspy.rhochi_rietveld_refinement(cryspy_obj)
print(res)
