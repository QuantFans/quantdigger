# -*- coding: utf8 -*-
import numpy as np
from matplotlib.axes import Axes

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
    def __init__(self, price, n, type='simple', name='MA'):
        super(MA, self).__init__(name)
        self.value = self._moving_average(price, n, type)
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
    
    def plot_ma(self, widget, color='y', lw=2):
        self.widget = widget
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
    def __init__(self, prices, n=14, name="RSI"):
        super(RSI, self).__init__(name)
        self.prices = prices
        self.n = n
        self.value = self._relative_strength(prices, n)
    
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

    def plot_rsi(self, widget, fillcolor = 'b'):
        self.widget = widget
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
        
    def plot_macd(self, widget):
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
