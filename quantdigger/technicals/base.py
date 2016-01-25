# -*- coding: utf8 -*-
# @file base.py
# @brief 指标基类
# @author wondereamer
# @version 0.1
# @date 2015-12-23

import inspect
import numpy as np
import pandas
from collections import OrderedDict
from quantdigger.engine import series
from quantdigger.widgets.widget_plot import PlotInterface
from quantdigger.errors import SeriesIndexError, DataFormatError

def transform2ndarray(data):
    """ 如果是序列变量，返回ndarray
        ,浅拷贝
    """
    if isinstance(data, series.NumberSeries):
        data = data.data
        #data = data.data[:len(data)]
    elif isinstance(data, pandas.Series):
        # 处理pandas.Series
        data = np.asarray(data)
    if not isinstance(data, np.ndarray):
        raise  DataFormatError(type=type(data))
    return data

def tech_init(method):
    """ 根据被修饰函数的参数构造属性。  
        并且触发向量计算。
    """
    def wrapper(self, *args, **kwargs):
        magic = inspect.getargspec(method)
        arg_names = magic.args[1:]
        # 默认参数
        default =  dict((x, y) for x, y in zip(magic.args[-len(magic.defaults):], magic.defaults))
        # 调用参数
        method_args = { }
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)
        # 
        default.update(method_args)
        # 属性创建
        for key, value in default.iteritems():
            setattr(self, key, value)
        # 运行构造函数
        rst =  method(self, *args, **kwargs)
        self.compute()
        return rst
    return wrapper

def plot_init(method):
    """ 根据被修饰函数的参数构造属性。  
        并且触发绘图范围计算。
    """
    def wrapper(self, *args, **kwargs):
        magic = inspect.getargspec(method)
        arg_names = magic.args[1:]
        # 默认参数
        default =  dict((x, y) for x, y in zip(magic.args[-len(magic.defaults):], magic.defaults))
        # 调用参数
        method_args = { }
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)
        # 
        default.update(method_args)
        # 属性创建
        for key, value in default.iteritems():
            setattr(self, key, value)
        # 运行构造函数
        rst =  method(self, *args, **kwargs)
        self._init_bound()
        return rst
    return wrapper

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


class TechnicalBase(PlotInterface):
    """
    指标基类。

    :ivar name: 指标对象名称
    :ivar values: 向量化运行结果, 用于处理历史数据。
    :ivar series: 单值指标的序列变量或多值指标的序列变量数组。
    :ivar _algo: 逐步指标函数。
    :ivar _args: 逐步指标函数的参数。
    """
    def __init__(self, name='',  widget=None):
        super(TechnicalBase, self).__init__(name, widget)
        self.name = name
        self.count = 0
        #if isinstance(data, series.NumberSeries) and series.g_rolling:
            #data.set_shift()
            ## 指标周期
            #data.reset_data([], n+series.g_window)
            ##(curbar, values)
            #self._cache = [(-1, None)] * (series.g_window+1)
        self._args = None
        ## @TODO 去掉逐步运算后删除
        # 只在逐步运算中必须初始化
        self.values = []    

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。""" 
        raise NotImplementedError

    def _vector_algo(self, data, n):
        """向量化运行, 结果必须赋值给self.values。
        
        Args:
            data (np.ndarray): 数据
            n (int): 时间窗口大小
        """
        raise NotImplementedError

    def compute(self):
        """ 
         构建时间序列变量，执行指标的向量算法。
        """
        if not hasattr(self, '_args'):
            raise Exception("每个指标都必须有_args属性，代表指标计算的参数！")
        self.data = self._args[0]
        if not series.g_rolling:
            # 数据转化成ta-lib能处理的格式
            self._args[0] = transform2ndarray(self._args[0])
            apply(self._vector_algo, tuple(self._args))
        if not hasattr(self, 'values'):
            raise Exception("每个指标都必须有value属性，代表指标计算结果！")
        if isinstance(self.values, dict):
            self.series = OrderedDict()
            for key, value in self.values.iteritems():
                self.series[key] = series.NumberSeries(value, len(value),
                                                    self.name, self, float('nan'))
            for key, value in self.series.iteritems():
                setattr(self, key, value)
            self.multi_value = True
        else:
            self.series = [series.NumberSeries(self.values, len(self.values),
                            self.name, self, float('nan'))]
            self.multi_value = False
        if series.g_rolling:
            if self.multi_value:
                for key, value in self.series.iteritems():
                    value.reset_data([], 1+series.g_window)
            else:
                for s in self.series:
                    s.reset_data([], 1+series.g_window)
        self._init_bound()
        

    def compute_element(self, cache_index, rolling_index):
        """ 计算一个回溯值, 被Series延迟调用。
        
        Args:
            cache_index (int): 缓存索引

            rolling_index (int): 回溯索引
        """
        if series.g_rolling:
            rolling_index = min(len(self.data)-1, self.curbar)
            values = None
            if self._cache[cache_index][0] == self.curbar:
                values = self._cache[cache_index][1] # 缓存命中
            else:
                self._rolling_data = transform2ndarray(self.data)  # 输入
                # 指标一次返回多个值
                args =  (self._rolling_data, ) + self._args + (rolling_index,)
                values = apply(self._rolling_algo, args)
                self._cache[cache_index] = (self.curbar, values)

            for i, v in enumerate(values):
                if self.multi_value:
                    self.series.values()[i].update(v) 
                else:
                    self.series[i].update(v)
        else:
            ## @todo 如果是实时数据，还是要计算
            return

    @property
    def curbar(self):
        if self.multi_value:
            return self.series.itervalues().next().curbar
        return self.series[0].curbar

    def __size__(self):
        """""" 
        if self.multi_value:
            return len(self.series.itervalues().next())
        return len(self.series[0])
    
    #def debug_data(self):
        #""" 主要用于调试""" 
        #return [s.data for s in self.series]

    def _added_to_tracker(self, tracker):
        if tracker:
            tracker.add_indicator(self)

    #def __tuple__(self):
        #""" 返回元组。某些指标，比如布林带有多个返回值。
            #这里以元组的形式返回多个序列变量。
        #"""
        #if isinstance(self.series, list):
            #return tuple(self.series)
        #else:
            #return (self.series,)

    #def __iter__(self):
        #return self

    #def next(self):
        #"""docstring for next""" 
        #iter(self.series)

    def __call__(self, index):
        return self[index]

    def __getitem__(self, index):
        # 解析多元值, 返回series
        # python 3.x 有这种机制？
        #print self.name, index
        #print self.series[0].data
        if self.multi_value:
            return self.series[index]
        # 返回单变量的值。
        if index >= 0:
            return self.series[0][index]
        else:
            raise SeriesIndexError

    def __float__(self):
        return self.series[0][0]

    def __str__(self):
        return str(self.series[0][0])

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

    #
    def __add__(self, r):
        return self.series[0][0] + float(r)

    def __sub__(self, r):
        return self.series[0][0] - float(r)

    def __mul__(self, r):
        return self.series[0][0] * float(r)

    def __div__(self, r):
        return self.series[0][0] / float(r)

    def __mod__(self, r):
        return self.series[0][0] % float(r)

    def __pow__(self, r):
        return self.series[0][0] ** float(r)

    #
    def __radd__(self, r):
        return self.series[0][0] + float(r)

    def __rsub__(self, r):
        return self.series[0][0] - float(r)

    def __rmul__(self, r):
        return self.series[0][0] * float(r)

    def __rdiv__(self, r):
        return self.series[0][0] / float(r)

    def __rmod__(self, r):
        return self.series[0][0] % float(r)

    def __rpow__(self, r):
        return self.series[0][0] ** float(r)

    ## 不该被改变。
    #def __iadd__(self, r):
        #self.series[0] += r
        #return self

    #def __isub__(self, r):
        #self.series[0] -= r
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
