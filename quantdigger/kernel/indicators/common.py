# -*- coding: utf8 -*-
##
# @file common.py
# @brief 
# @author dingjie.wang@foxmail.com
# @version 0.1
# @date 2015-12-23
import talib
import numpy as np
from indicator import IndicatorBase, create_attributes, override_attributes, transform2ndarray
            
class MA(IndicatorBase):
    ## @todo assure name is unique, it there are same names,
    # modify the repeat name.
    @create_attributes
    def __init__(self, tracker, prices, n, name='MA', color='y', lw=1, style="line"):
        super(MA, self).__init__(tracker, name)
        # self.value为任何支持index的数据结构。
        # 在策略中，price变量可能为NumberSeries，需要用NUMBER_SERIES_SUPPORT处理，
        # 转化为numpy.ndarray等能被指标函数处理的参数。
        self.value = self._moving_average(prices, n)
        self._algo = self._iter_moving_average
        self._args = (n,)

    def _iter_moving_average(self, price, n):
        """ 逐步运行的均值函数。""" 
        pass

    def _moving_average(self, data, n):
        """ 向量化运行的均值函数。 """
        data = transform2ndarray(data)
        return talib.SMA(data, n)

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        self.plot_line(self.value, self.color, self.lw, self.style)

    #@override_attributes
    #def plot(self, widget, color='y', lw=2, style="line"):
        #""" 绘图，参数可由UI调整。 
        ### @note 构造函数中的绘图参数需与函数
           #的绘图函数一致。这样函数参数可覆盖默认的属性参数。
        #"""
        #self.widget = widget
        #self.plot_line(self.value, color, lw, style)


class BOLL(IndicatorBase):
    ## @todo assure name is unique, it there are same names,
    # modify the repeat name.
    @create_attributes
    def __init__(self, tracker, prices, n, name='BOLL', color='y', lw=1, style="line"):
        super(BOLL, self).__init__(tracker, name)
        # self.value为任何支持index的数据结构。
        # 在策略中，price变量可能为NumberSeries，需要用NUMBER_SERIES_SUPPORT处理，
        # 转化为numpy.ndarray等能被指标函数处理的参数。
        self.value = self._boll(prices, n)
        self._algo = self._iter_boll
        self._args = (n,)

    def _iter_boll(self, price, n):
        """ 逐步运行。""" 
        pass

    def _boll(self, data, n):
        """ 向量化运行的均值函数。 """
        data = transform2ndarray(data)
        upper, middle, lower =  talib.BBANDS(data, n, 2, 2)
        return (upper, middle, lower)

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

    @override_attributes
    def plot(self, widget, fillcolor='b'):
        self._mplot(widget, fillcolor)


    def _mplot(self, ax, fillcolor):
        textsize = 9
        ax.plot(self.value, color=fillcolor, lw=2)
        ax.axhline(70, color=fillcolor, linestyle='-')
        ax.axhline(30, color=fillcolor, linestyle='-')
        ax.fill_between(self.value, 70, where=(self.value>=70), facecolor=fillcolor, edgecolor=fillcolor)
        ax.fill_between(self.value, 30, where=(self.value<=30), facecolor=fillcolor, edgecolor=fillcolor)
        ax.text(0.6, 0.9, '>70 = overbought', va='top', transform=ax.transAxes, fontsize=textsize, color = 'k')
        ax.text(0.6, 0.1, '<30 = oversold', transform=ax.transAxes, fontsize=textsize, color = 'k')
        ax.set_ylim(0, 100)
        ax.set_yticks([30,70])
        ax.text(0.025, 0.95, 'rsi (14)', va='top', transform=ax.transAxes, fontsize=textsize)


class MACD(IndicatorBase):
    """"""
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
        self._mplot(widget)

    def _mplot(self, ax):
        fillcolor = 'darkslategrey'
        nema = 9
        ema9 = MA(self.macd, nema, type='exponential').value
        ax.plot(self.macd, color='black', lw=2)
        ax.plot(self.ema9, color='blue', lw=1)
        ax.fill_between(self.macd-ema9, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

    #def _qtplot(self, widget, fillcolor):
        #raise  NotImplementedError

import matplotlib.finance as finance
class Volume(IndicatorBase):
    """docstring for Volume"""
    @create_attributes
    def __init__(self, tracker, open, close, volume, name='volume', colorup='r', colordown='b', width=1):
        super(Volume, self).__init__(tracker, name)
        self.value = transform2ndarray(volume)
        #self.name = name
        #self.volume = volume
        #self.open = open
        #self.close = close
        #self.colorup = colorup
        #self.colordown = colordown
        #self.width = width

    @override_attributes
    def plot(self, widget, colorup = 'r', colordown = 'b', width = 1):
        """docstring for plot""" 
        finance.volume_overlay(widget, self.open, self.close, self.volume, colorup, colordown, width)



from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection
class Candles(object):
    def __init__(self, tracker, data, name='candle',  width = 0.6, colorup = 'r', colordown='g', lc='k', alpha=1):
        """ Represent the open, close as a bar line and high low range as a
        vertical line.


        ax          : an Axes instance to plot to
        width       : the bar width in points
        colorup     : the color of the lines where close >= open
        colordown   : the color of the lines where close <  open
        alpha       : bar transparency

        return value is lineCollection, barCollection
        """
        #super(Candles, self).__init__(tracker, name)
        self.set_yrange(data.low.values, data.high.values)
        self.data = data
        self.name = name

    # note this code assumes if any value open, close, low, high is
    # missing they all are missing
    def plot(self, widget, width = 0.6, colorup = 'r', colordown='g', lc='k', alpha=1):
        """docstring for plot""" 
        delta = width/2.
        barVerts = [ ( (i-delta, open), (i-delta, close), (i+delta, close), (i+delta, open) ) for i, open, close in zip(xrange(len(self.data)), self.data.open, self.data.close) if open != -1 and close!=-1 ]
        rangeSegments = [ ((i, low), (i, high)) for i, low, high in zip(xrange(len(self.data)), self.data.low, self.data.high) if low != -1 ]
        r,g,b = colorConverter.to_rgb(colorup)
        colorup = r,g,b,alpha
        r,g,b = colorConverter.to_rgb(colordown)
        colordown = r,g,b,alpha
        colord = { True : colorup,
                   False : colordown,
                   }
        colors = [colord[open<close] for open, close in zip(self.data.open, self.data.close) if open!=-1 and close !=-1]
        assert(len(barVerts)==len(rangeSegments))
        useAA = 0,  # use tuple here
        lw = 0.5,   # and here
        r,g,b = colorConverter.to_rgb(lc)
        linecolor = r,g,b,alpha
        lineCollection = LineCollection(rangeSegments,
                                         colors       = ( linecolor, ),
                                         linewidths   = lw,
                                         antialiaseds = useAA,
                                         zorder = 0,
                                         )

        barCollection = PolyCollection(barVerts,
                                       facecolors   = colors,
                                       edgecolors   = colors,
                                       antialiaseds = useAA,
                                       linewidths   = lw,
                                       zorder = 1,
                                       )
        #minx, maxx = 0, len(rangeSegments)
        #miny = min([low for low in self.data.low if low !=-1])
        #maxy = max([high for high in self.data.high if high != -1])
        #corners = (minx, miny), (maxx, maxy)
        #ax.update_datalim(corners)
        widget.autoscale_view()
        # add these last
        widget.add_collection(barCollection)
        widget.add_collection(lineCollection)

        #ax.plot(self.data.close, color = 'y')
        #lineCollection, barCollection = None, None
        return lineCollection, barCollection

    def set_yrange(self, lower, upper=[]):
        self.upper = upper if len(upper)>0 else lower
        self.lower = lower

    def y_interval(self, w_left, w_right):
        if len(self.upper) == 2:
            return max(self.upper), min(self.lower) 
        ymax = np.max(self.upper[w_left: w_right])
        ymin = np.min(self.lower[w_left: w_right])
        return ymax, ymin


class TradingSignal(object):
    """docstring for signalWindow"""
    def __init__(self, tracker, signal, name="Signal", c=None, lw=2):
        #self.set_yrange(price)
        #self.signal=signal
        #self.c = c
        #self.lw = lw
        self.signal = signal
        self.name = name

    def plot(self, widget, c=None, lw=2):
        useAA = 0,  # use tuple here
        signal = LineCollection(self.signal, colors=c, linewidths=lw,
                                antialiaseds=useAA)
        widget.add_collection(signal)

    def y_interval(self, w_left, w_right):
        return 0, 100000000


class TradingSignalPos(object):
    """docstring for signalWindow"""
    def __init__(self, tracker, price_data, deals, name="Signal", c=None, lw=2):
        self.signal = []
        self.colors = []
        for deal in deals:
            # ((x0, y0), (x1, y1))
            p = ((price_data.row[deal.open_datetime], deal.open_price),
                    (price_data.row[deal.close_datetime], deal.close_price))
            self.signal.append(p)
            self.colors.append((1,0,0,1) if deal.profit() > 0 else (0,1,0,1))
        self.name = name

    def plot(self, widget, lw=2):
        useAA = 0,  # use tuple here
        signal = LineCollection(self.signal, colors=self.colors, linewidths=lw,
                                antialiaseds=useAA)
        widget.add_collection(signal)

    def y_interval(self, w_left, w_right):
        ## @todo signal interval
        return 0, 100000000
