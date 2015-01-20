# -*- coding: utf8 -*-

#from flufl.enum import Enum
from quantdigger.errors import PeriodTypeError

class Contract(object):
    """ 合约 """
    def __init__(self, exch_type, code):
        self.exch_type = exch_type
        self.code = code

    def __str__(self):
        """""" 
        return "%s-%s" % (self.exch_type, self.code)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash


class Period(object):
    """ 周期 """
    #class Type(Enum):
        #MilliSeconds = "MilliSeconds" 
        #Seconds = "Seconds" 
        #Minutes = "Minutes" 
        #Hours = "Hours" 
        #Days = "Days" 
        #Months = "Months" 
        #Seasons = "Seasons" 
        #Years = "Years" 
    periods = ["MilliSeconds", "Seconds", "Minutes", "Hours",
               "Days", "Months", "Seasons", "Years"]    
    def __init__(self, type_, length):
        if type_ not in self.periods:
            raise PeriodTypeError
        self._type = type_
        self._length = length

    @property
    def type(self):
        return self._type

    @property
    def length(self):
        return self._length


    def __str__(self):
        return "%s-%d" % (self._type, self._length)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash


class PContract(object):
    def __init__(self, contract, period):
        self.contract = contract
        self.period = period

    def __str__(self):
        """ return string like 'SHEF-IF000-Minutes-10'  """
        return "%s-%s" % (self.contract, self.period)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash
