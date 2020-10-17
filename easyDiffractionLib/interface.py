__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from typing import Callable

from easyDiffractionLib.Interfaces import InterfaceTemplate
from easyCore.Objects.Inferface import InterfaceFactoryTemplate


class InterfaceFactory(InterfaceFactoryTemplate):
    def __init__(self):
        super(InterfaceFactory, self).__init__(InterfaceTemplate._interfaces)

    def generate_sample_binding(self, name, *args) -> property:
        """
        Automatically bind a `Parameter` to the corresponding interface.
        :param name: parameter name
        :type name: str
        :return: binding property
        :rtype: property
        """
        fun = self.__set_item(self, 'filename')
        fun(args[0].filename)
        return property(fget=None,
                        fset=self.__set_sample_item(self, name, *args))

    def generate_instrument_binding(self, name) -> property:
        """
        Automatically bind a `Parameter` to the corresponding interface.
        :param name: parameter name
        :type name: str
        :return: binding property
        :rtype: property
        """
        return property(fget=self.__get_instrument_item(self, name),
                        fset=self.__set_instrument_item(self, name))

    def generate_binding(self, name, *args, **kwargs) -> property:
        """
        Automatically bind a `Parameter` to the corresponding interface.
        :param name: parameter name
        :type name: str
        :return: binding property
        :rtype: property
        """
        return property(self.__get_item(self, name), self.__set_item(self, name))

    @staticmethod
    def __get_item(obj, key: str, external: bool = True) -> Callable:
        """
        Access the value of a key by a callable object
        :param key: name of parameter to be retrieved
        :type key: str
        :return: function to get key
        :rtype: Callable
        """

        def inner():
            return obj().get_value(key, external)

        return inner

    @staticmethod
    def __set_item(obj, key) -> Callable:
        """
        Set the value of a key by a callable object
        :param obj: object to be created from
        :type obj: InterfaceFactory
        :param key: name of parameter to be set
        :type key: str
        :return: function to set key
        :rtype: Callable
        """

        def inner(value):
            obj().set_value(key, value)
        return inner

    @staticmethod
    def __get_sample_item(obj, key: str, holder) -> Callable:
        """
        Access the value of a key by a callable object
        :param key: name of parameter to be retrieved
        :type key: str
        :return: function to get key
        :rtype: Callable
        """

        def inner():
            # return obj().get_value(key)
            return None
        return inner

    @staticmethod
    def __set_sample_item(obj, key, holder) -> Callable:
        """
        Set the value of a key by a callable object
        :param obj: object to be created from
        :type obj: InterfaceFactory
        :param key: name of parameter to be set
        :type key: str
        :return: function to set key
        :rtype: Callable
        """

        def inner(value):
            # !!! THIS IS NOT THE WAY TO DO IT !!!
            # !!!       FOR TESTING ONLY      !!!!
            if obj.current_interface_name == 'Cryspy':
                obj().set_value(key, holder.phases.cif.__str__(holder.output_index))
            else:
                holder.phases.cif.to_file(holder.filename, holder.output_index)
            # obj().set_value(key, value)
        return inner

    @staticmethod
    def __get_instrument_item(obj, key: str) -> Callable:
        """
        Access the value of a key by a callable object
        :param key: name of parameter to be retrieved
        :type key: str
        :return: function to get key
        :rtype: Callable
        """

        def inner():
            return obj().get_instrument_value(key)
        return inner

    @staticmethod
    def __set_instrument_item(obj, key) -> Callable:
        """
        Set the value of a key by a callable object
        :param obj: object to be created from
        :type obj: InterfaceFactory
        :param key: name of parameter to be set
        :type key: str
        :return: function to set key
        :rtype: Callable
        """

        def inner(value):
            obj().set_instrument_value(key, value)
        return inner
