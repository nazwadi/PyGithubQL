#!/usr/bin/env python3.7
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod
from pprint import pprint


class Collector(object, metaclass=ABCMeta):
    """Base class for a data collector."""

    def __init__(self, *args, **kwargs):
        """initialize configuration and api keys"""
        self.config = ConfigParser()
        self.config.read('collectors.cfg')

    @abstractmethod
    def __repr__(self):
        """An exact, printable representation of the object"""
        pass

    @abstractmethod
    def __str__(self):
        """A more informal, printable representation of the object"""
        pass

    @abstractmethod
    def save_user(self, username):
        """This function should be used to retrieve user account data"""
        pass

    @abstractmethod
    def verify(self):
        """Verify API credentials work"""
        pass


if __name__ == "__main__":
    pass
