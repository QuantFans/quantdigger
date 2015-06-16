# -*- coding: utf8 -*-
##
# @file indicator.py
# @brief 
# @author wondereamer
# @version 0.1
# @date 2015-02-22

import numpy as np
import pandas
from quantdigger.kernel.engine import series
from quantdigger.widgets.plotting import PlotingActions
from quantdigger.errors import SeriesIndexError, DataFormatError

def transform2ndarray(data):
    """ 如果是序列变量，返回ndarray """
    if isinstance(data, series.NumberSeries):
        data = data.data[:data.length_history]
    elif isinstance(data, pandas.Series):
        # 处理pandas.Series
        data = np.asarray(data)
    if type(data) != np.ndarray:
        raise  DataFormatError
    return data

# 带参数decorator
#def invoke_algo(algo, *arg):
    #"""docstring for test""" 
    #def _algo(method):
        #def __algo(self):
            #if not self.series.updated:
                #self.series = algo(*arg)
                #self.series.updated = True
            #return method(self)
        #return __algo
    #return _algo


class IndicatorBase(PlotingActions):
    ## @todo 把绘图函数分类到父类中。
    """
    指标基类。每个指标的内部数据为序列变量。所以每个指标对象都会与一个跟踪器相关联，
    负责更新其内部的序列变量。 如果是MA这样的单值指标, 重载函数可以使指标对象像序列变量一样被使用。
    如果是多值指标，如布林带，那么会以元组的形式返回多一个序列变量。

    :ivar name: 指标对象名称
    :vartype name: str
    :ivar _tracker: 关联跟踪器
    :vartype _tracker: BarTracker
    :ivar value: 向量化运行结果, 用于处理历史数据。
    :ivar _series: 单值指标的序列变量或多值指标的序列变量数组。
    :ivar _algo: 逐步指标函数。
    :ivar _args: 逐步指标函数的参数。
    """
    def __init__(self, tracker, name='',  widget=None):
        super(IndicatorBase, self).__init__(name, widget)
        self.name = name
        self.value = None
        self._algo = None
        self._args = None
        ## @todo 判断tracker是否为字符串。
        if tracker:
            self._added_to_tracker(tracker)
        self._tracker = tracker

    def calculate_latest_element(self):
        """ 被tracker调用，确保内部序列变量总是最新的。 """
        s = self._series
        m = False
        if isinstance(self._series, list):
            s = self._series[0] 
            m = True
        if s.curbar >= s.length_history:
            if not m:
                self._series.update(apply(self._algo, self._args))
            else:
                rst = apply(self._algo, self._args)
                for i, v in enumerate(rst):
                    self._series[i].update(v)


    def __size__(self):
        """""" 
        if isinstance(self._series, list):
            return len(self._series[0])
        else:
            return len(self._series)

    def _added_to_tracker(self, tracker):
        if tracker:
            tracker.add_indicator(self)


    def __tuple__(self):
        """ 返回元组。某些指标，比如布林带有多个返回值。
            这里以元组的形式返回多个序列变量。
        """
        if isinstance(self._series, list):
            return tuple(self._series)
        else:
            return (self._series,)

    #def __iter__(self):
        #"""docstring for __iter__""" 
        #if self._series.__class__.__name__ == 'list':
            #return tuple(self._series)
        #else:
            #return (self._series,)

    def __float__(self):
        return self._series[0]

    def __str__(self):
        return str(self._series[0])

    #
    def __eq__(self, r):
        return float(self) == float(r)

    def __lt__(self, other):
        return float(self) < float(other)

    def __le__(self, other):
        return float(self) <= float(other)

    def __ne__(self, other):
        return float(self) != float(other)

    def __gt__(self, other):
        return float(self) > float(other)

    def __ge__(self, other):
        return float(self) >= float(other)

    # 以下都是单值函数。
    def __getitem__(self, index):
        # 大于当前的肯定被运行过。
        if index >= 0:
            return self._series[index]
        else:
            raise SeriesIndexError

    #
    def __add__(self, r):
        return self._series[0] + float(r)

    def __sub__(self, r):
        return self._series[0] - float(r)

    def __mul__(self, r):
        return self._series[0] * float(r)

    def __div__(self, r):
        return self._series[0] / float(r)

    def __mod__(self, r):
        return self._series[0] % float(r)

    def __pow__(self, r):
        return self._series[0] ** float(r)

    #
    def __radd__(self, r):
        return self._series[0] + float(r)

    def __rsub__(self, r):
        return self._series[0] - float(r)

    def __rmul__(self, r):
        return self._series[0] * float(r)

    def __rdiv__(self, r):
        return self._series[0] / float(r)

    def __rmod__(self, r):
        return self._series[0] % float(r)

    def __rpow__(self, r):
        return self._series[0] ** float(r)

    ## 不该被改变。
    #def __iadd__(self, r):
        #self._series[0] += r
        #return self

    #def __isub__(self, r):
        #self._series[0] -= r
        #return self

    #def __imul__(self, r):
        #self._data[self._curbar] *= r
        #return self

    #def __idiv__(self, r):
        #self._data[self._curbar] /= r
        #return self

    #def __ifloordiv__(self, r):
        #self._data[self._curbar] %= r
        #return self

