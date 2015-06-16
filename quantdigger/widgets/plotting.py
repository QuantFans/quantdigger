# -*- coding: utf8 -*-
##
# @file plotting.py
# @brief 
# @author wondereamer
# @version 0.15
# @date 2015-06-13

from matplotlib.axes import Axes
import numpy as np

class AxWidget(object):
    """ matplotlib绘图容器 """
    def __init__(self, name):
        self.name = name;

    def plot_line(self, widget, data, color, lw, style='line' ):
        widget.plot(data, color=color, lw=lw, label=self.name)


class QtWidget(object):
    """ pyqt绘图容器 """
    def __init__(self, name):
        self.name = name;

    def plot_line(self, widget, data, color, lw, style='line' ):
        """ 使用matplotlib容器绘线 """
        raise NotImplementedError


class PlotingActions(object):
    """
    系统会提基类。


    :ivar upper: 坐标上界（绘图用）
    :vartype upper: float
    :ivar lower: 坐标上界（绘图用）
    :vartype lower: float
    :ivar widget: 绘图容器，暂定Axes
    """
    def __init__(self, name, widget):
        self.ax_widget = AxWidget(name)
        self.qt_widget = QtWidget(name)
        self.widget = widget
        self.upper = self.lower = None

    def plot_line(self, data, color, lw, style='line'):
        """ 画线    

            :ivar data: 浮点数组。
            :vartype data: list
            :ivar color: 画线颜色
            :vartype color: str 
            :ivar lw: 线宽
            :vartype lw: int
        """
        # 区分向量绘图和逐步绘图。
        if len(data) > 0:
            # 区分绘图容器。
            if isinstance(self.widget, Axes):
                self.ax_widget.plot_line(self.widget, data, color, lw, style) 
            else:
                self.qt_widget.plot_line(self.widget, data, color, lw, style)
        else:
            pass

    def plot(self, widget):
        """ 如需绘制指标，则需重载此函数。 """
        ## @todo 把plot_line等绘图函数分离到widget类中。
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
    

