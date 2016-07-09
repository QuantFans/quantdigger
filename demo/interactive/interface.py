# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class BackendInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_contracts(self, pcontract):
        pass

    @abstractmethod
    def get_pcontract(self, pcontract):
        pass

    @abstractmethod
    def run_strategy(self, name):
        pass

    @abstractmethod
    def run_technical(self, name):
        pass

    @abstractmethod
    def get_technicals(self):
        pass

    @abstractmethod
    def get_strategies(self):
        pass


class UIInterface(object):
    __metaclass__ = ABCMeta
    def __init__(self):
        pass
    
    @abstractmethod
    def plot(self):
        pass
