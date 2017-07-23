# -*- coding: utf-8 -*-
##
# @file plotting.py
# @brief 统一绘图接口, 帮助指标类的绘图。
# @author wondereamer
# @version 0.15
# @date 2015-06-13

import six
import inspect
from matplotlib.axes import Axes
import numpy as np

def plot_init(method):
    """ 根据被修饰函数的参数构造属性。
        并且触发绘图范围计算。
    """
    def wrapper(self, *args, **kwargs):
        magic = inspect.getargspec(method)
        arg_names = magic.args[1:]
        # 默认参数
        default = dict(
            (x, y) for x, y in zip(magic.args[-len(magic.defaults):],
                                   magic.defaults))
        # 调用参数
        method_args = {}
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)
        #
        default.update(method_args)
        # 属性创建
        for key, value in six.iteritems(default):
            setattr(self, key, value)
        # 运行构造函数
        rst = method(self, *args, **kwargs)
        self._init_bound()
        return rst
    return wrapper

import bisect
def sub_interval(start, end, array):
    """ 寻找满足区间[start, end]的array值

    Args:
        start (int): 区间左侧
        end (int): 区间右侧
        array (list): 有序数组

    >>> array = [0,1,3, 4, 5, 6, 8]
    >>> rst = sub_interval(2, 5, array)
    >>> six.print_(array[rst[0]: rst[1]])
    """
    i = bisect.bisect_left(array, start)
    if i != len(array):
        t_start = i
    else:
        raise ValueError
    i = bisect.bisect_right(array, end)
    if i:
        t_end = i
    else:
        raise ValueError
    return (t_start, t_end)


class AxWidget(object):
    """ matplotlib绘图容器 """
    def __init__(self, name):
        self.name = name

    def plot_line(self, widget, ydata, style, lw, ms):
        widget.plot(ydata, style, lw=lw, ms=ms, label=self.name)

    def plot_line_withx(self, widget, _xdata, ydata, style, lw, ms):
        widget.plot(_xdata, ydata, style, lw=lw, ms=ms, label=self.name)


class QtWidget(object):
    """ pyqt绘图容器 """
    def __init__(self, name):
        self.name = name

    def plot_line(self, widget, ydata, style, lw, ms):
        raise NotImplementedError

    def plot_line_withx(self, widget, _xdata, ydata, style, lw, ms):
        raise NotImplementedError


class Plotter(object):
    """
    系统绘图基类。

    :ivar _upper: 坐标上界（绘图用）
    :vartype _upper: float
    :ivar lower: 坐标上界（绘图用）
    :vartype lower: float
    :ivar widget: 绘图容器，暂定Axes
    """
    def __init__(self, name, widget):
        self.ax_widget = AxWidget(name)
        self.qt_widget = QtWidget(name)
        self.widget = widget
        self._upper = self._lower = None
        self._xdata = None

    def plot_line(self, *args, **kwargs):
        """ 画线

        Args:
            *args (tuple): [_xdata], ydata, style
            **kwargs (dict): lw, ms
        """
        # 区分向量绘图和逐步绘图。
        lw = kwargs.get('lw', 1)
        ms = kwargs.get('ms', 10)
        if len(args[0]) > 0:
            if len(args) == 2:
                ydata = args[0]
                style = args[1]
                # 区分绘图容器。
                if isinstance(self.widget, Axes):
                    self.ax_widget.plot_line(self.widget, ydata, style, lw, ms)
                else:
                    self.qt_widget.plot_line(self.widget, ydata, style, lw, ms)
            elif len(args) == 3:
                _xdata = args[0]
                ydata = args[1]
                style = args[2]
                # 区分绘图容器。
                if isinstance(self.widget, Axes):
                    self.ax_widget.plot_line_withx(self.widget, _xdata, ydata, style, lw, ms)
                else:
                    self.qt_widget.plot_line_withx(self.widget, _xdata, ydata, style, lw, ms)

    def plot(self, widget):
        """ 如需绘制指标，则需重载此函数。 """
        # @todo 把plot_line等绘图函数分离到widget类中。
        raise NotImplementedError

    def stick_yrange(self, y_range):
        """ 固定纵坐标范围。如RSI指标。

        :ivar y_range: 纵坐标范围。
        :vartype y_range: list
        """
        self._lower = y_range
        self._upper = y_range

    def y_interval(self, w_left, w_right):
        """ 可视区域[w_left, w_right]移动时候重新计算纵坐标范围。 """
        # @todo 只存储上下界, 每次缩放的时候计算一次, 在移动时候无需计算。
        if len(self._upper) == 2:
            # 就两个值，分别代表上下界。
            return max(self._upper), min(self._lower)
        try:
            if self._xdata:
                w_left, w_right = sub_interval(w_left, w_right, self._xdata)
        except ValueError:
            # 标志不在可视区间，确保不会被采纳。
            return -1000000, 1000000
        else:
            ymax = np.max(self._upper[w_left: w_right])
            ymin = np.min(self._lower[w_left: w_right])
            return ymax, ymin

    def _init_bound(self):
        # 绘图中的y轴范围未被设置，使用默认值。
        if not self._upper:
            self._upper = self._lower = []
            if isinstance(self.values, dict):
                # 多值指标
                values = zip(*six.itervalues(self.values))
                self._upper = [max(value) for value in values]
                self._lower = [min(value) for value in values]
            else:
                self._upper = self.values
                self._lower = self.values
            if self._xdata:
                # 用户使用plot_line接口的时候触发这里
                # @NOTE 重排，强制绘图点是按x有序的。
                temp = zip(self._xdata, self.values)
                sdata = sorted(temp, key=lambda x: x[0])
                temp = zip(*sdata)
                l_temp = list(temp)
                self._xdata = l_temp[0]
                self.values = l_temp[1]
