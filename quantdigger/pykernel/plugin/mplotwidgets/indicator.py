# -*- coding: utf8 -*-
import numpy as np

class MA(object):
    """docstring for Ave"""
    def __init__(self, price, n, type='simple', ax=None, color='y', lw=2):
        self.value = self._moving_average(price, n, type)
        self.n = n
        if ax:
            self.plot_ma(ax, color, lw) 

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
    
    def plot_ma(self, ax, color='y', lw=2):
        ax.plot(self.value, color=color, lw=lw, label='MA (%d)' % self.n)


class RSI(object):
    """docstring for RSI"""
    def __init__(self, prices, n=14, ax=None, fillcolor='b'):
        self.prices = prices
        self.n = n
        self.value = self._relative_strength(prices, n)
        if ax:
            self.plot_rsi(ax, fillcolor) 
    
    def _relative_strength(self, prices, n=14):
        """
        compute the n period relative strength indicator
        http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
        http://www.investopedia.com/terms/r/rsi.asp

        """
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

    def plot_rsi(self, ax, fillcolor = 'b'):
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


class MACD(object):
    """"""
    def __init__(self, prices, nslow, nfast):
        self.emaslow, self.emafast, self.macd = self._moving_average_convergence(prices, nslow=nslow, nfast=nfast)
        
    def plot_macd(self, ax):
        """docstring for plot_macd""" 
        fillcolor = 'darkslategrey'
        nema = 9
        ema9 = MA(self.macd, nema, type='exponential').value
        ax.plot(self.macd, color='black', lw=2)
        ax.plot(self.ema9, color='blue', lw=1)
        ax.fill_between(self.macd-ema9, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

    def _moving_average_convergence(x, nslow=26, nfast=12):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = MA(x, nslow, type='exponential').value
        emafast = MA(x, nfast, type='exponential').value
        return emaslow, emafast, emafast - emaslow
