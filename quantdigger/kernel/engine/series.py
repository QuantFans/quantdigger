# -*- coding: utf8 -*-
import numpy as np
from quantdigger.errors import SeriesIndexError, BreakConstError
    
class NumberSeries(object):
    """docstring for NumberSeries"""
    DEFAULT_NUMBER = 0.0
    def __init__(self, tracker, data=[], system_var=False):
        # 为当天数据预留空间。
        # 系统序列变量总是预留空间。向量化运行中，非系统序列变量的长度
        # 计算中会与系统序列变量的长度对齐。非向量化运行的普通序列变量
        # 无需预留空间。
        if system_var:
            self._data = np.append(data, tracker.container_day)
        else:
            self._data = data

        # 非向量化运行的普通序列变量的_length_history的值为0.
        self._length_history = len(data)

        self._curbar = 0
        self._tracker = tracker
        self._system_var = system_var
        self._added_to_tracker(tracker, system_var)
        # begin_index
        # end_index


    @property
    def length_history(self):
        return self._length_history

    @property
    def curbar(self):
        return self._curbar


    def update_curbar(self, curbar):
        """ 被tracker调用。 """
        self._curbar = curbar


    def _added_to_tracker(self, tracker, system_var):
        """
        如果是系统变量open,close,high,low,volume 
        那么tracker为None,不负责更新数据。
        系统变量的值有ExcuteUnit更新。 
        """
        if not system_var:
            tracker.add_series(self)


    def update(self, v):
        """ 赋值操作

        非系统序列变量。
        python没有'='运算符重载:(
        """
        if self._system_var:
            raise BreakConstError 
        self._data[self._curbar] = v
        

    def __size__(self):
        """""" 
        return len(self._data)


    def duplicate_last_element(self):
        """ 只有非系统系列变量才会运行这个 """

        # 非向量化运行。
        if self.length_history ==  0:
            if self._curbar == 0:
                self._data.append(self.DEFAULT_NUMBER) 
            else:
                self._data.append(self._data[-1])
            return

        # 向量化运行。
        if self._curbar > self.length_history:
            self._data[self._curbar] = self._data[self._curbar-1]


    def __str__(self):
        return str(self._data[self._curbar])


    def __getitem__(self, index):
        try:
            i = self._curbar - index
            if i < 0:
                return self.DEFAULT_NUMBER
            else:
                return self._data[i]
        except SeriesIndexError:
            raise SeriesIndexError


    #def __call__(self, *args):
        #length = len(args)
        #if length  == 0:
            #return float(self) 
        #elif length == 1:
            #return self._data[self._curbar - args[0]]


    def __float__(self):
        return self._data[self._curbar]

    #
    def __eq__(self, v):
        return self._data[self._curbar] == v

    def __lt__(self, other):
        return float(self) < other

    def __le__(self, other):
        return float(self) <= other

    def __ne__(self, other):
        return float(self) != other

    def __gt__(self, other):
        return float(self) > other

    def __ge__(self, other):
        return float(self) >= other

    #
    def __iadd__(self, r):
        self._data[self._curbar] += r
        return self

    def __isub__(self, r):
        self._data[self._curbar] -= r
        return self

    def __imul__(self, r):
        self._data[self._curbar] *= r
        return self

    def __idiv__(self, r):
        self._data[self._curbar] /= r
        return self

    def __ifloordiv__(self, r):
        self._data[self._curbar] %= r
        return self

    #
    def __add__(self, r):
        return self._data[self._curbar] + r

    def __sub__(self, r):
        return self._data[self._curbar] - r

    def __mul__(self, r):
        return self._data[self._curbar] * r

    def __div__(self, r):
        return self._data[self._curbar] / r

    def __mod__(self, r):
        return self._data[self._curbar] % r

    def __pow__(self, r):
        return self._data[self._curbar] ** r

    #
    def __radd__(self, r):
        return self._data[self._curbar] + r

    def __rsub__(self, r):
        return self._data[self._curbar] - r

    def __rmul__(self, r):
        return self._data[self._curbar] * r

    def __rdiv__(self, r):
        return self._data[self._curbar] / r

    def __rmod__(self, r):
        return self._data[self._curbar] % r

    def __rpow__(self, r):
        return self._data[self._curbar] ** r


#class DateTimeSeries(object):
    #"""docstring for NumberSeries"""
    #DEFAULT_NUMBER = 0.0
    #def __init__(self, tracker, data=[], system_var=False):
        ## 为当天数据预留空间。
        ## 系统序列变量总是预留空间。向量化运行中，非系统序列变量的长度
        ## 计算中会与系统序列变量的长度对齐。非向量化运行的普通序列变量
        ## 无需预留空间。
        #if system_var:
            #self._data = np.append(data, tracker.container_day)
        #else:
            #self._data = data

        ## 非向量化运行的普通序列变量的_length_history的值为0.
        #self._length_history = len(data)

        #self._curbar = 0
        #self._tracker = tracker
        #self._system_var = system_var
        #self._added_to_tracker(tracker, system_var)
        ## begin_index
        ## end_index


    #@property
    #def length_history(self):
        #return self._length_history

    #@property
    #def curbar(self):
        #return self._curbar


    #def update_curbar(self, curbar):
        #""" 被tracker调用。 """
        #self._curbar = curbar


    #def _added_to_tracker(self, tracker, system_var):
        #"""
        #如果是系统变量open,close,high,low,volume 
        #那么tracker为None,不负责更新数据。
        #系统变量的值有ExcuteUnit更新。 
        #"""
        #if not system_var:
            #tracker.add_series(self)


    #def update(self, v):
        #""" 赋值操作

        #非系统序列变量。
        #python没有'='运算符重载:(
        #"""
        #if self._system_var:
            #raise BreakConstError 
        #self._data[self._curbar] = v
        

    #def __size__(self):
        #"""""" 
        #return len(self._data)


    #def duplicate_last_element(self):
        #""" 只有非系统系列变量才会运行这个 """

        ## 非向量化运行。
        #if self.length_history ==  0:
            #if self._curbar == 0:
                #self._data.append(self.DEFAULT_NUMBER) 
            #else:
                #self._data.append(self._data[-1])
            #return

        ## 向量化运行。
        #if self._curbar > self.length_history:
            #self._data[self._curbar] = self._data[self._curbar-1]


    #def __str__(self):
        #return str(self._data[self._curbar])


    #def __getitem__(self, index):
        #try:
            #i = self._curbar - index
            #if i < 0:
                #return self.DEFAULT_NUMBER
            #else:
                #return self._data[i]
        #except SeriesIndexError:
            #raise SeriesIndexError
