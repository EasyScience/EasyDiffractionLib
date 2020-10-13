import os, sys

import CFML_api
import matplotlib.pyplot as plt


def main():
    print("AAA")
    powder_pattern = CFML_api.PowderPatternSimulator()
    powder_pattern.compute("../CFML_api/Examples/Data/SrTiO3.cif")
    plt.plot(powder_pattern.x, powder_pattern.y, label="CIF with default conditions")
    plt.show()

if __name__ == '__main__':
    main()
