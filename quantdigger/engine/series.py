# -*- coding: utf-8 -*-
import numpy as np
from quantdigger.errors import SeriesIndexError
import datetime


class SeriesBase(object):
    def __init__(self, data=[], name='series', indic=None, default=None):
        """ 序列变量的基类。
        name用来跟踪
        """
        self.curbar = 0
        self._window_size = len(data)
        self._indic = indic
        self._default = default
        self._realtime = False
        self.name = name
        if len(data) == 0:
            self.data = np.array([self._default] * self._window_size)
        else:
            self.data = data

    def reset_data(self, data, wsize):
        """ 初始化值和窗口大小

        Args:
            data (list|ndarray|pd.Series): 数据，类型为支持索引的数据结构
            wwsize (int): 窗口大小
        """
        self._window_size = wsize
        if len(data) == 0:
            self.data = np.array([self._default] * self._window_size)
        else:
            # 序列系统变量
            self.data = data

    #def _sort_data(self):
        #temp = self.data[self._index]
        #max_index = self.window_size-1
        #for i in range(0, max_index):
            #ordered_index = (self.curbar - (max_index-self._index)) % self._window_size
            #self.data[self._index] = self.data[ordered_index]
            #self._index = ordered_index
        #self.data[max_index] = temp
        #self._index = max_index
        #return

    def update_curbar(self, curbar):
        """ 更新当前Bar索引 """
        self.curbar = curbar

    def update(self, v):
        """ 更新最后一个值 """
        self.data[self.curbar] = v

    def __len__(self):
        return len(self.data)

    def duplicate_last_element(self):
        """
           非指标序列变量才会运行
        """
        try:
            pre_elem = self.data[(self.curbar-1) % self._window_size]
        except KeyError:
            return
        else:
            self.data[self.curbar] = pre_elem

    def __str__(self):
        return str(self[0])

    def __getitem__(self, index):
        raise NotImplementedError

    #def __call__(self, *args):
        #length = len(args)
        #if length  == 0:
            #return float(self)
        #elif length == 1:
            #return self.data[self.curbar - args[0]]


class NumberSeries(SeriesBase):
    """ 数字序列变量"""
    DEFAULT_VALUE = 0.0
    value_type = float

    def __init__(self, data=[], name='NumberSeries', indic=None, default=0.0):
        super(NumberSeries, self).__init__(data, name, indic, default)
        return

    def __float__(self):
        return self[0]

    #
    def __eq__(self, r):
        return self[0] == float(r)

    def __lt__(self, r):
        return self[0] < float(r)

    def __le__(self, r):
        return self[0] <= float(r)

    def __ne__(self, r):
        return self[0] != float(r)

    def __gt__(self, r):
        return self[0] > float(r)

    def __ge__(self, r):
        return self[0] >= float(r)

    #
    def __iadd__(self, r):
        self[0] += float(r)
        return self

    def __isub__(self, r):
        self[0] -= float(r)
        return self

    def __imul__(self, r):
        self[0] *= float(r)
        return self

    def __idiv__(self, r):
        self[0] /= float(r)
        return self

    def __ifloordiv__(self, r):
        self[0] %= float(r)
        return self

    #
    def __add__(self, r):
        return self[0] + float(r)

    def __sub__(self, r):
        return self[0] - float(r)

    def __mul__(self, r):
        return self[0] * float(r)

    def __div__(self, r):
        return self[0] / float(r)

    def __mod__(self, r):
        return self[0] % float(r)

    def __pow__(self, r):
        return self[0] ** float(r)

    #
    def __radd__(self, r):
        return float(r) + self[0]

    def __rsub__(self, r):
        return float(r) - self[0]

    def __rmul__(self, r):
        return float(r) * self[0]

    def __rdiv__(self, r):
        return float(r) / self[0]

    def __rmod__(self, r):
        return float(r) % self[0]

    def __rpow__(self, r):
        return float(r) ** self[0]

    def __getitem__(self, index):
        try:
            if self._realtime:
                #if index<0:
                    #return self._default
                #if self._shift:
                    ## 输入
                    #return self.data[self._index-index]
                ## 输出
                #i = self.curbar - index
                #if self._indic:
                    ## 延迟计算
                    #self._indic.compute_element(i%self._window_size, index)
                #return self.data[i%self._window_size]
                assert(False)
            else:
                i = self.curbar - index
                if i < 0 or index < 0:
                    return self._default
                else:
                    return float(self.data[i])
        except SeriesIndexError:
            raise SeriesIndexError

    def __call__(self, index):
        return self[index]


class DateTimeSeries(SeriesBase):
    """ 时间序列变量 """
    DEFAULT_VALUE = datetime.datetime(1980, 1, 1)

    def __init__(self, data=[], name='DateTimeSeries'):
        super(DateTimeSeries, self).__init__(data, name,
                                             default=self.DEFAULT_VALUE)
        return

    def __getitem__(self, index):
        try:
            i = self.curbar - index
            if i < 0 or index < 0:
                return self._default
            #return datetime.fromtimestamp(self.data[i%self._window_size]/1000)
            return self.data[i]
        except SeriesIndexError:
            raise SeriesIndexError

    def __str__(self):
        return str(self.data[self.curbar])

    def __eq__(self, r):
        if isinstance(r, DateTimeSeries):
            return self[0] == r[0]
        return self[0] == r

    def __lt__(self, r):
        if isinstance(r, DateTimeSeries):
            return self[0] < r[0]
        return self[0] < r

    def __le__(self, r):
        if isinstance(r, DateTimeSeries):
            return self[0] <= r[0]
        return self[0] <= r

    def __ne__(self, r):
        if isinstance(r, DateTimeSeries):
            return self[0] != r[0]
        return self[0] != r

    def __gt__(self, r):
        if isinstance(r, DateTimeSeries):
            return self[0] > r[0]
        return self[0] > r

    def __ge__(self, r):
        if isinstance(r, DateTimeSeries):
            return self[0] >= r[0]
        return self[0] >= r
