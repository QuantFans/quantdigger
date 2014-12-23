# -*- coding: utf8 -*-
import numpy as np
import inspect
from matplotlib.axes import Axes

def plot_interface(method):
    def wrapper(self, widget, *args, **kwargs):
        self.widget = widget
        # 用函数中的参数覆盖属性。
        arg_names = inspect.getargspec(method).args[2:]
        method_args = { }
        obj_attrs = { }
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)
        for attr in arg_names:
            obj_attrs[attr] = getattr(self, attr)
        obj_attrs.update(method_args)
        return method(self, widget, **obj_attrs)
    return wrapper


class Indicator(object):
    """docstring for Indicator"""
    def __init__(self, name, value=None, widget=None):
        """
        
        Args:
            name (str): description
            value (np.dataarray): 值
            widget (widget): Axes or QtGui.Widget。
        
        Returns:
            Indicator. The result
        """
        self.name = name
        # 可能是qt widget, Axes, WebUI
        self.widget = widget
        self.value = value

    def __float__(self):
        return float(self.n)
    
    # api
    def plot_line(self, data, color, lw):
        """ 画线    
        
        Args:
            data (list): 浮点数组。
            color (str): 颜色。
            lw (int): 线宽。
        """
        def mplot_line(data, color, lw):
            """ 使用matplotlib容器绘线 """
            raise NotImplementedError

        def qtplot_line(self, data, color, lw):
            """ 使用pyqtq容器绘线 """
            raise NotImplementedError

        if isinstance(self.widget, Axes):
            mplot_line(data, color, lw) 
        else:
            qtplot_line(data, color, lw)

    # other plot ..


from matplotlib.collections import LineCollection
class TradingSignal(Indicator):
    """docstring for signalWindow"""
    def __init__(self, s, name="Signal"):
        self.signal=s
        super(TradingSignal , self).__init__(name)

    def plot_signal(self, widget, c, lw):
        useAA = 0,  # use tuple here
        signal = LineCollection(self.signal, colors=c, linewidths=lw,
                                antialiaseds=useAA)
        widget.add_collection(signal)


class MA(Indicator):
    def __init__(self, price, n, name='MA', type='simple', color='y', lw=1):
        super(MA, self).__init__(name)
        self.value = self._moving_average(price, n, type)
        self.color = color
        self.lw = lw
        self.n = n

    def _moving_average(self, x, n, type='simple'):
        """
        compute an n period moving average.

        type is 'simple' | 'exponential'

        """
        x = np.asarray(x)
        if type=='simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))
        weights /= weights.sum()
        a =  np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    @plot_interface
    def plot(self, widget, color=None, lw=None):
        ## @todo 使用Indicator类中的绘图接口绘图。
        if isinstance(widget, Axes):
            self._mplot(widget, color, lw)
        else:
            # pyqt
            self._qtplot(widget, color, lw)


    def _mplot(self, ax, color, lw):
        ax.plot(self.value, color=color, lw=lw, label=self.name)


    def _qtplot(self, widget, color, lw):
        """docstring for qtplot""" 
        raise  NotImplementedError



class RSI(Indicator):
    def __init__(self, prices, n=14, name="RSI", fillcolor='b'):
        super(RSI, self).__init__(name)
        self.prices = prices
        self.n = n
        self.value = self._relative_strength(prices, n)
        self.fillcolor = fillcolor
    
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


    @plot_interface
    def plot(self, widget, fillcolor='b'):
        self._mplot(widget, fillcolor)


    def _mplot(self, ax, fillcolor):
        textsize = 9
        ax.plot(self.value, color=fillcolor)
        ax.axhline(70, color=fillcolor)
        ax.axhline(30, color=fillcolor)
        ax.fill_between(self.value, 70, where=(self.value>=70), facecolor=fillcolor, edgecolor=fillcolor)
        ax.fill_between(self.value, 30, where=(self.value<=30), facecolor=fillcolor, edgecolor=fillcolor)
        ax.text(0.6, 0.9, '>70 = overbought', va='top', transform=ax.transAxes, fontsize=textsize, color = 'k')
        ax.text(0.6, 0.1, '<30 = oversold', transform=ax.transAxes, fontsize=textsize, color = 'k')
        ax.set_ylim(0, 100)
        ax.set_yticks([30,70])
        ax.text(0.025, 0.95, 'rsi (14)', va='top', transform=ax.transAxes, fontsize=textsize)


class MACD(Indicator):
    """"""
    def __init__(self, prices, nslow, nfast, name='MACD'):
        super(MACD, self).__init__(name)
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
class Volume(Indicator):
    """docstring for Volume"""
    def __init__(self, open, close, volume, name='volume', colorup='r', colordown='b', width=1):
        self.name = name
        self.volume = volume
        self.open = open
        self.close = close
        self.colorup = colorup
        self.colordown = colordown
        self.width = width

    @plot_interface
    def plot(self, widget, colorup = 'r', colordown = 'b', width = 1):
        """docstring for plot""" 
        finance.volume_overlay(widget, self.open, self.close, self.volume, colorup, colordown, width)




from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection
class Candles(Indicator):
    def __init__(self, data, width = 0.6, colorup = 'r', colordown='g', lc='k', alpha=1):
        """ Represent the open, close as a bar line and high low range as a
        vertical line.


        ax          : an Axes instance to plot to
        width       : the bar width in points
        colorup     : the color of the lines where close >= open
        colordown   : the color of the lines where close <  open
        alpha       : bar transparency

        return value is lineCollection, barCollection
        """
        self.data = data
        self.width = width
        self.colorup = colorup
        self.colordown = colordown
        self.lc = lc
        self.alpha = alpha
        # note this code assumes if any value open, close, low, high is
        # missing they all are missing


    @plot_interface
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
