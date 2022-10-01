from dataclasses import dataclass
from collections import OrderedDict
import subprocess
import shlex


@dataclass
class ConfigBase(object):
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance.__odict__ = OrderedDict()
        return instance

    def __setattr__(self, key, value):
        if key != '__odict__':
            self.__odict__[key] = value
        object.__setattr__(self, key, value)

    def print_args(self):
        """
        Print all configurations
        """
        print("[Configuration]")
        for key, value in self.__odict__.items():
            print('\'{0}\' : {1}'.format(key, value))
        print('')

    def parse_args(self):
        """
        Supports to pass arguments from command line
        """
        import argparse

        def str2bool(v):
            if v.lower() in ('true', 't'):
                return True
            elif v.lower() in ('false', 'f'):
                return False
            else:
                raise argparse.ArgumentTypeError('Boolean value expected.')
        parser = argparse.ArgumentParser()
        for key, value in self.__odict__.items():
            if bool == type(value):
                parser.add_argument('--'+key.replace("_", "-"),
                                    default=str(value), type=str2bool)
            else:
                parser.add_argument('--'+key.replace("_", "-"),
                                    default=value, type=type(value))
        args = parser.parse_args()
        args = vars(args)
        # update
        for key in self.__odict__:
            arg = args[key]
            self.__odict__[key] = arg
            object.__setattr__(self, key, arg)
        # print
        self.print_args()
        return self
