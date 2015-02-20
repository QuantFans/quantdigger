# -*- coding: utf8 -*-
import numpy as np
import inspect
from matplotlib.axes import Axes
from quantdigger.kernel.engine import series
from quantdigger.errors import SeriesIndexError


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


class Indicator(object):
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


    def _mplot(self, ax, color, lw):
        ax.plot(self.value, color=color, lw=lw, label=self.name)


    def _qtplot(self, widget, color, lw):
        """docstring for qtplot""" 
        raise  NotImplementedError

    def set_yrange(self, upper, lower=[]):
        self.upper = upper
        self.lower = lower if len(lower)>0 else upper

    def y_interval(self, w_left, w_right):
        if len(self.upper) == 2:
            return max(self.upper), min(self.lower) 
        ymax = np.max(self.upper[w_left: w_right])
        ymin = np.min(self.lower[w_left: w_right])
        return ymax, ymin
            
    # other plot ..
def NUMBER_SERIES_SUPPORT(data):
    """ 如果是series变量，返回ndarray """
    if data.__class__.__name__ == 'NumberSeries':
        # 获取ndarray变量 
        data = data.data
    return data
    #elif data.__class__.__name__ == 'Series' or data.__class__.__name__ == 'ndarray':
        #x = np.asarray(data)
    #else:
        #raise Exception

class MA(Indicator):
    @create_attributes
    def __init__(self, tracker, price, n, name='MA', type='simple', color='y', lw=1, style="line"):
        super(MA, self).__init__(tracker, name)
        self.value = self._moving_average(price, n, type) # 任何支持index的数据结构。
        self._algo = self._iter_moving_average
        self._args = (n,)

    def _iter_moving_average(self, price, n):
        """ 逐步运行的均值函数。""" 
        pass

    def _moving_average(self, data, n, type_='simple'):
        """ 向量化运行的均值函数。

        compute an n period moving average.

        type is 'simple' | 'exponential'

        """
        data = NUMBER_SERIES_SUPPORT(data)
        # 减少非必须的拷贝。
        x = np.asarray(data)
        if type_=='simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))
        weights /= weights.sum()
        a =  np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    @override_attributes
    def plot(self, widget, color='y', lw=2, style="line"):
        self.widget = widget
        self.plot_line(self.value, color, lw, style)



class RSI(Indicator):
    @create_attributes
    def __init__(self, tracker, prices, n=14, name="RSI", fillcolor='b'):
        super(RSI, self).__init__(tracker, name)
        self.value = self._relative_strength(prices, n)
        self.set_yrange([0, 100])

    
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


class MACD(Indicator):
    """"""
    def __init__(self, tracker, prices, nslow, nfast, name='MACD'):
        super(MACD, self).__init__(tracker, name)
        self.set_yrange(prices)
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
    @create_attributes
    def __init__(self, tracker, open, close, volume, name='volume', colorup='r', colordown='b', width=1):
        super(Volume, self).__init__(tracker, name)
        self.set_yrange(volume)
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
        self.set_yrange(data.high.values, data.low.values)
        self.data = data
        self.name = name

        # note this code assumes if any value open, close, low, high is
        # missing they all are missing


    #@override_attributes
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

    def set_yrange(self, upper, lower=[]):
        self.upper = upper
        self.lower = lower if len(lower)>0 else upper

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
