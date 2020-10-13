import os, sys

#import CFML_api


def main():
    print("without CFML_api")
    exit()

    simulation_conditions = CFML_api.PowderPatternSimulationConditions()
    print("simulation_conditions.theta_max", simulation_conditions.theta_max)

    powder_pattern = CFML_api.PowderPatternSimulator()
    print("powder_pattern.x", powder_pattern.x)
    print("powder_pattern.y", powder_pattern.y)

    powder_pattern.compute("../CFML_api/Examples/Data/SrTiO3.cif")
    print("powder_pattern.x", powder_pattern.x)
    print("powder_pattern.y", powder_pattern.y)

if __name__ == '__main__':
    main()
