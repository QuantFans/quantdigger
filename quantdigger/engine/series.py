# -*- coding: utf-8 -*-
import numpy as np
from quantdigger.errors import SeriesIndexError, BreakConstError

class SeriesBase(object):
    """ 序列变量的基类。
    
        :ivar _curbar: 当前Bar索引。
        :vartype _curbar: int

        :ivar _tracker: 负责维护次时间序列变量的跟踪器。
        :vartype _tracker: BarTracker

        :ivar _system_var: 是否是策略内置变量如Strategy.open, Strategy.close
        :vartype _system_var: bool

        :ivar data: 数据，类型为支持索引的数据结构，如list, ndarray, pandas.Series等。
    """
    DEFAULT_VALUE = None
    def __init__(self, tracker, data=[], system_var=False):
        # 非向量化运行的普通序列变量的_length_history的值为0.
        self._length_history = len(data)

        self._curbar = 0
        self._tracker = tracker
        self._system_var = system_var
        self._added_to_tracker(tracker, system_var)
        self.data = data

    @property
    def length_history(self):
        """ 历史数据长度。 """
        return self._length_history

    @property
    def curbar(self):
        """ 当前Bar索引。 """
        return self._curbar


    def update_curbar(self, curbar):
        """ 更新当前Bar索引， 被tracker调用。 """
        self._curbar = curbar


    def _added_to_tracker(self, tracker, system_var):
        """ 添加到跟踪器的时间序列变量列表。
            
        如果是系统变量open,close,high,low,volume 
        那么tracker为None,不负责更新数据。
        系统变量的值有ExcuteUnit更新。 
        """
        if not system_var:
            tracker.add_series(self)

    def append(self, v):
        """ 赋值操作

        非系统序列变量。
        python没有'='运算符重载:(
        """
        if self._system_var:
            raise BreakConstError 
        self.data[self._curbar] = v
        
    def __len__(self):
        """""" 
        return len(self.data)

    def duplicate_last_element(self):
        """ 更新非系统变量最后一个单元的值。 """
        # 非向量化运行。
        if self.length_history ==  0:
            if self._curbar == 0:
                self.data.append(self.DEFAULT_VALUE) 
            else:
                self.data.append(self.data[-1])
            return
        # 向量化运行, 并且收到了实时数据。
        if self._curbar > self.length_history:
            ## @bug 这里假设非系统变量也预留了空间。和子类构造函数不符合。
            self.data[self._curbar] = self.data[self._curbar-1]

    def __str__(self):
        return str(self.data[self._curbar])

    def __getitem__(self, index):
        try:
            i = self._curbar - index
            if i < 0:
                return self.DEFAULT_VALUE
            else:
                # index >= len(self.data)
                return self.data[i]
        except SeriesIndexError:
            raise SeriesIndexError

    #def __call__(self, *args):
        #length = len(args)
        #if length  == 0:
            #return float(self) 
        #elif length == 1:
            #return self.data[self._curbar - args[0]]
    
    
class NumberSeries(SeriesBase):
    """ 数字序列变量"""
    DEFAULT_VALUE = 0.0
    value_type = float
    def __init__(self, tracker, data=[], system_var=False):
        super(NumberSeries, self).__init__(tracker, data, system_var)
        # 为当天数据预留空间。
        # 系统序列变量总是预留空间。向量化运行中，非系统序列变量的长度
        # 计算中会与系统序列变量的长度对齐。非向量化运行的普通序列变量
        # 无需预留空间。
        if system_var:
            self.data = np.append(data, tracker.container_day)
        else:
            self.data = data

    def __float__(self):
        return self.data[self._curbar]

    #
    def __eq__(self, r):
        return self.data[self._curbar] == float(r)

    def __lt__(self, r):
        return self.data[self._curbar] < float(r)

    def __le__(self, r):
        return self.data[self._curbar] <= float(r)

    def __ne__(self, r):
        return self.data[self._curbar] != float(r)

    def __gt__(self, r):
        return self.data[self._curbar] > float(r)

    def __ge__(self, r):
        return self.data[self._curbar] >= float(r)

    #
    def __iadd__(self, r):
        self.data[self._curbar] += float(r)
        return self

    def __isub__(self, r):
        self.data[self._curbar] -= float(r)
        return self

    def __imul__(self, r):
        self.data[self._curbar] *= float(r)
        return self

    def __idiv__(self, r):
        self.data[self._curbar] /= float(r)
        return self

    def __ifloordiv__(self, r):
        self.data[self._curbar] %= float(r)
        return self

    #
    def __add__(self, r):
        return self.data[self._curbar] + float(r)

    def __sub__(self, r):
        return self.data[self._curbar] - float(r)

    def __mul__(self, r):
        return self.data[self._curbar] * float(r)

    def __div__(self, r):
        return self.data[self._curbar] / float(r)

    def __mod__(self, r):
        return self.data[self._curbar] % float(r)

    def __pow__(self, r):
        return self.data[self._curbar] ** float(r)

    #
    def __radd__(self, r):
        return float(r) + self.data[self._curbar]

    def __rsub__(self, r):
        return float(r) - self.data[self._curbar]

    def __rmul__(self, r):
        return float(r) * self.data[self._curbar]

    def __rdiv__(self, r):
        return float(r) / self.data[self._curbar]

    def __rmod__(self, r):
        return float(r) % self.data[self._curbar]

    def __rpow__(self, r):
        return float(r) ** self.data[self._curbar]

class DateTimeSeries(SeriesBase):
    """ 时间序列变量 """
    ## @todo utc 技时起点
    DEFAULT_VALUE = 0.0
    def __init__(self, tracker, data=[], system_var=False):
        super(DateTimeSeries, self).__init__(tracker, data, system_var)
        ## @todo 预留空间
        # 为当天数据预留空间。
        # 系统序列变量总是预留空间。向量化运行中，非系统序列变量的长度
        # 计算中会与系统序列变量的长度对齐。非向量化运行的普通序列变量
        # 无需预留空间。
        #if system_var:
            #self.data = np.append(data, tracker.container_day)
        #else:
        self.data = data
