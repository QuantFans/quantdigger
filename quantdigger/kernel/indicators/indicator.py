# -*- coding: utf8 -*-
##
# @file indicator.py
# @brief 
# @author dingjie.wang@foxmail.com
# @version 0.1
# @date 2015-02-22

import numpy as np
import inspect
from matplotlib.axes import Axes
from quantdigger.kernel.engine import series
from quantdigger.errors import SeriesIndexError, DataFormatError

def transform2ndarray(data):
    """ 如果是series变量，返回ndarray """
    if data.__class__.__name__ == 'NumberSeries':
        data = data.data[:data.length_history]
    elif data.__class__.__name__ == 'Series':
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

def override_attributes(method):
    # 如果plot函数不带绘图参数，则使用属性值做为参数。
    # 如果带参数，者指标中的plot函数参数能够覆盖本身的属性。
    def wrapper(self, widget, *args, **kwargs):
        self.widget = widget
        # 用函数中的参数覆盖属性。
        arg_names = inspect.getargspec(method).args[2:]
        method_args = { }
        obj_attrs = { }
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)

        try:
            for attr in arg_names:
                obj_attrs[attr] = getattr(self, attr)
        except Exception, e:
            print e
            print("构造函数和绘图函数的绘图属性参数不匹配。" )
        obj_attrs.update(method_args)
        return method(self, widget, **obj_attrs)
    return wrapper


def create_attributes(method):
    # 根据构造函数的参数和默认参数构造属性。
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
        # 构造函数
        rst =  method(self, *args, **kwargs)
        # 序列变量
        if self.tracker:
            self._series = series.NumberSeries(self.tracker, self.value)
        # 绘图中的y轴范围
        if hasattr(self, 'value') and not self.upper:
            self.set_yrange(self.value)
        return rst
    return wrapper


class IndicatorBase(object):
    """docstring for Indicator"""
    def __init__(self, tracker, name,  widget=None):
        """
        
        Args:
            name (str): description
            value (np.dataarray): 值
            widget (widget): Axes or QtGui.Widget。
        
        """
        self.name = name
        # 可能是qt widget, Axes, WebUI
        self.widget = widget
        self.upper = self.lower = None
        ## @todo 判断tracker是否为字符串。
        if tracker:
            self._added_to_tracker(tracker)
        self._tracker = tracker


    def calculate_latest_element(self):
        """ 被tracker调用，确保series总是最新的。 """
        if self._series.curbar >= self._series.length_history:
            self._series.update(apply(self._algo, self._args))


    def __size__(self):
        """""" 
        return len(self._series)


    def __getitem__(self, index):
        # 大于当前的肯定被运行过。
        if index >= 0:
            return self._series[index]
        else:
            raise SeriesIndexError


    def _added_to_tracker(self, tracker):
        if tracker:
            tracker.add_indicator(self)


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

    # api
    def plot_line(self, data, color, lw, style='line'):
        """ 画线    
        
        Args:
            data (list): 浮点数组。
            color (str): 颜色。
            lw (int): 线宽。
        """
        ## @todo 放到两个类中。
        def mplot_line(data, color, lw, style='line' ):
            """ 使用matplotlib容器绘线 """
            self.widget.plot(data, color=color, lw=lw, label=self.name)

        def qtplot_line(self, data, color, lw):
            """ 使用pyqtq容器绘线 """
            raise NotImplementedError

        # 区分向量绘图和逐步绘图。
        if len(data) > 0:
            # 区分绘图容器。
            if isinstance(self.widget, Axes):
                mplot_line(data, color, lw, style) 
            else:
                qtplot_line(data, color, lw, style)
        else:
            pass

    def set_yrange(self, upper, lower=[]):
        self.upper = upper
        self.lower = lower if len(lower)>0 else upper

    def y_interval(self, w_left, w_right):
        if len(self.upper) == 2:
            return max(self.upper), min(self.lower) 
        ymax = np.max(self.upper[w_left: w_right])
        ymin = np.min(self.lower[w_left: w_right])
        return ymax, ymin
