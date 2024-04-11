
from easyDiffractionLib.interface import InterfaceFactory


def main():
    interface = InterfaceFactory()
    print(f"Available interfaces: {interface.available_interfaces}")

if __name__ == '__main__':
    main()
