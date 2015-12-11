# -*- coding: utf8 -*-
##
# @file common.py
# @brief 
# @author wondereamer
# @version 0.1
# @date 2015-12-23
import talib
import numpy as np
import matplotlib.finance as finance
from collections import OrderedDict
from quantdigger.indicators.base import IndicatorBase, transform2ndarray, create_attributes
from quantdigger.engine import series
class MA(IndicatorBase):
    """ 移动平均线指标。 """
    @create_attributes
    def __init__(self, data, n, name='MA',
                 color='y', lw=1, style="line"):
        super(MA, self).__init__(data, n, name)
        # 数据转化成ta-lib能处理的格式
        # self.value为任何支持index的数据结构。
        # 在策略中，price变量可能为NumberSeries，需要用NUMBER_SERIES_SUPPORT处理，
        # 转化为numpy.ndarray等能被指标函数处理的参数。
        if not series.g_rolling:
            # 向量化运行的均值函数
            data = transform2ndarray(data)
            self.value = talib.SMA(data, n)
        # 支持逐步运行必须函数的参数
        self._rolling_args = (n,)

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。""" 
        ## @todo 用了向量化方法，速度降低
        return (talib.SMA(data, n)[i], )

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        self.plot_line(self.value, self.color, self.lw, self.style)



class BOLL(IndicatorBase):
    """ 布林带指标。 """
    ## @todo assure name is unique, it there are same names,
    # modify the repeat name.
    @create_attributes
    def __init__(self, data, n, name='BOLL', color='y', lw=1, style="line"):
        super(BOLL, self).__init__(data, n, name)
        # self.value为任何支持index的数据结构。
        # 在策略中，price变量可能为NumberSeries，需要用NUMBER_SERIES_SUPPORT处理，
        # 转化为numpy.ndarray等能被指标函数处理的参数。
        self.value = OrderedDict([
                ('upper', []),
                ('middler', []),
                ('lower', [])
                ])
        if not series.g_rolling:
            # 向量化运行的均值函数
            data = transform2ndarray(data)
            u, m, l = talib.BBANDS(data, n, 2, 2)
            self.value = {
                    'upper': u,
                    'middler': m,
                    'lower': l
                    }
        # 支持逐步运行必须函数的参数
        self._rolling_args = (n,)

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。""" 
        ## @todo 用了向量化方法，速度降低
        upper, middle, lower =  talib.BBANDS(data, n, 2, 2)
        return (upper[i], middle[i], lower[i])

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        #self.plot_line(self.value, self.color, self.lw, self.style)


class RSI(IndicatorBase):
    @create_attributes
    def __init__(self, tracker, prices, n=14, name="RSI", fillcolor='b'):
        super(RSI, self).__init__(tracker, name)
        self.value = self._relative_strength(prices, n)
        ## @todo 一种绘图风格
        # 固定的y范围
        self.stick_yrange([0, 100])

    def _relative_strength(self, prices, n=14):
        deltas = np.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed>=0].sum()/n
        down = -seed[seed<0].sum()/n
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100./(1.+rs)

        for i in range(n, len(prices)):
            delta = deltas[i-1] # cause the diff is 1 shorter
            if delta>0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(n-1) + upval)/n
            down = (down*(n-1) + downval)/n

            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)
        return rsi

    def plot(self, widget):
        textsize = 9
        widget.plot(self.value, color=self.fillcolor, lw=2)
        widget.axhline(70, color=self.fillcolor, linestyle='-')
        widget.axhline(30, color=self.fillcolor, linestyle='-')
        widget.fill_between(self.value, 70, where=(self.value>=70),
                            facecolor=self.fillcolor, edgecolor=self.fillcolor)
        widget.fill_between(self.value, 30, where=(self.value<=30),
                            facecolor=self.fillcolor, edgecolor=self.fillcolor)
        widget.text(0.6, 0.9, '>70 = overbought', va='top', transform=widget.transAxes, fontsize=textsize, color = 'k')
        widget.text(0.6, 0.1, '<30 = oversold', transform=widget.transAxes, fontsize=textsize, color = 'k')
        widget.set_ylim(0, 100)
        widget.set_yticks([30,70])
        widget.text(0.025, 0.95, 'rsi (14)', va='top', transform=widget.transAxes, fontsize=textsize)


class MACD(IndicatorBase):
    @create_attributes
    def __init__(self, tracker, prices, nslow, nfast, name='MACD'):
        super(MACD, self).__init__(tracker, name)
        self.emaslow, self.emafast, self.macd = self._moving_average_convergence(prices, nslow=nslow, nfast=nfast)
        self.value = (self.emaslow, self.emafast, self.macd)

    def _moving_average_convergence(x, nslow=26, nfast=12):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = MA(x, nslow, type='exponential').value
        emafast = MA(x, nfast, type='exponential').value
        return emaslow, emafast, emafast - emaslow
        
    def plot(self, widget):
        self.widget = widget
        fillcolor = 'darkslategrey'
        nema = 9
        ema9 = MA(self.macd, nema, type='exponential').value
        widget.plot(self.macd, color='black', lw=2)
        widget.plot(self.ema9, color='blue', lw=1)
        widget.fill_between(self.macd-ema9, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

    #def _qtplot(self, widget, fillcolor):
        #raise  NotImplementedError

from quantdigger.widgets.widget_plot import PlotInterface
class Volume(PlotInterface):
    """ 柱状图。 """
    @create_attributes
    def __init__(self, open, close, volume, name='volume', colorup='r', colordown='b', width=1):
        super(Volume, self).__init__(name, None)
        self.value = transform2ndarray(volume)

    def plot(self, widget):
        finance.volume_overlay(widget, self.open, self.close, self.volume,
                               self.colorup, self.colordown, self.width)

