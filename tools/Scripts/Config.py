__author__ = "github.com/AndrewSazonov"
__version__ = '0.0.1'

import os, sys
import Functions


class Config():
    def __init__(self):
        # Main
        self.__dict__ = Functions.config()
        self.os = Functions.osName()

    def __getitem__(self, key):
        return self.__dict__[key]
