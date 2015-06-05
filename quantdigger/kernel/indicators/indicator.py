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
    """ 根据被修饰函数的参数构造属性。"""
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
        if not hasattr(self, 'value'):
            raise Exception("每个指标都必须有value属性，代表指标值！")
        else:
            # 序列变量
            if self.tracker:
                if self.value.__class__.__name__ == 'tuple':
                    self._series = [series.NumberSeries(self.tracker, value) for value in self.value]
                else:
                    self._series = series.NumberSeries(self.tracker, self.value)
            # 绘图中的y轴范围未被设置，使用默认值。
            if not self.upper:
                upper = lower = []
                if self.value.__class__.__name__ == 'tuple':
                    # 多值指标
                    upper = [ max([value[i] for value in self.value ]) for i in xrange(0, len(self.value[0]))]
                    lower = [ min([value[i] for value in self.value ]) for i in xrange(0, len(self.value[0]))]
                else:
                    upper = self.value
                    lower = self.value
                self.set_yrange(lower, upper)
            return rst
    return wrapper


class IndicatorBase(object):
    ## @todo 把绘图函数分类到父类中。
    """
    指标基类。每个指标的内部数据为序列变量。所以每个指标对象都会与一个跟踪器相关联，
    负责更新其内部的序列变量。 如果是MA这样的单值指标, 重载函数可以使指标对象像序列变量一样被使用。
    如果是多值指标，如布林带，那么会以元组的形式返回多一个序列变量。

    :ivar name: 指标对象名称
    :vartype name: str
    :ivar upper: 坐标上界（绘图用）
    :vartype upper: float
    :ivar lower: 坐标上界（绘图用）
    :vartype lower: float
    :ivar _tracker: 关联跟踪器
    :vartype _tracker: BarTracker
    :ivar widget: 绘图容器，暂定Axes
    :ivar value: 向量化运行结果, 用于处理历史数据。
    :ivar _series: 单值指标的序列变量或多值指标的序列变量数组。
    :ivar _algo: 逐步指标函数。
    :ivar _args: 逐步指标函数的参数。
    """
    def __init__(self, tracker, name,  widget=None):
        self.name = name
        # 可能是qt widget, Axes, WebUI
        self.widget = widget
        self.upper = self.lower = None
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
        if self._series.__class__.__name__ == 'list':
            s = self._series[0] 
            m = True
        if s.curbar >= s.length_history:
            if not m:
                self._series.update(apply(self._algo, self._args))
            else:
                rst = apply(self._algo, self._args)
                for i, v in enumerate(rst):
                    self._series[i].update(v)

    def plot(self, widget):
        """ 如需绘制指标，则需重载此函数。 """
        ## @todo 把plot_line等绘图函数分离到widget类中。
        pass

    # api
    def plot_line(self, data, color, lw, style='line'):
        """ 画线    

            :ivar data: 浮点数组。
            :vartype data: list
            :ivar color: 画线颜色
            :vartype color: str 
            :ivar lw: 线宽
            :vartype lw: int
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

    def set_yrange(self, lower, upper):
        """ 设置纵坐标范围。 """
        self.lower = lower
        self.upper = upper

    def stick_yrange(self, y_range):
        """ 固定纵坐标范围。如RSI指标。 

        :ivar y_range: 纵坐标范围。
        :vartype y_range: list
        """
        self.lower = y_range
        self.upper = y_range

    def y_interval(self, w_left, w_right):
        """ 可视区域移动时候重新计算纵坐标范围。 """
        ## @todo 只存储上下界, 每次缩放的时候计算一次, 在移动时候无需计算。
        if len(self.upper) == 2:
            # 就两个值，分别代表上下界。
            return max(self.upper), min(self.lower) 
        ymax = np.max(self.upper[w_left: w_right])
        ymin = np.min(self.lower[w_left: w_right])
        return ymax, ymin

    def __size__(self):
        """""" 
        if self._series.__class__.__name__ == 'list':
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
        if self._series.__class__.__name__ == 'list':
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

