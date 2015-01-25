from abc import ABCMeta, abstractmethod

class TraderApi(object):

    __metaclass__ = ABCMeta

    """docstring for Trader"""
    def __init__(self, arg):
        pass

    @abstractmethod
    def connect(self):
        """docstring for """ 
        pass

    @abstractmethod
    def register_handlers(self, handlers):
        """docstring for """ 
        pass
    
    
class CtpTraderApi(TraderApi):
    """docstring for CtpTrader"""
    def __init__(self):
        pass

    def connect(self):
        """docstring for connect""" 
        pass

    def register_handlers(self, handlers):
        """docstring for register_handlers""" 
        pass
    
