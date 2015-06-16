# -*- coding: utf8 -*-
import numpy as np
import inspect
from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection
from quantdigger.kernel.engine import series

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
            print(e)
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
                if isinstance(self.value, tuple):
                    self._series = [series.NumberSeries(self.tracker, value) for value in self.value]
                else:
                    self._series = series.NumberSeries(self.tracker, self.value)
            # 绘图中的y轴范围未被设置，使用默认值。
            if not self.upper:
                upper = lower = []
                if isinstance(self.value, tuple):
                    # 多值指标
                    upper = [ max([value[i] for value in self.value ]) for i in xrange(0, len(self.value[0]))]
                    lower = [ min([value[i] for value in self.value ]) for i in xrange(0, len(self.value[0]))]
                else:
                    upper = self.value
                    lower = self.value
                self.set_yrange(lower, upper)
            return rst
    return wrapper

class Candles(object):
    """
    画蜡烛线。
    """
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
        self.width = width
        self.colorup = colorup
        self.colordown = colordown
        self.lc = lc
        self.alpha = alpha

    # note this code assumes if any value open, close, low, high is
    # missing they all are missing
    @override_attributes
    def plot(self, widget, width = 0.6, colorup = 'r', colordown='g', lc='k', alpha=1):
        """docstring for plot""" 
        delta = self.width/2.
        barVerts = [ ( (i-delta, open), (i-delta, close), (i+delta, close), (i+delta, open) ) for i, open, close in zip(xrange(len(self.data)), self.data.open, self.data.close) if open != -1 and close!=-1 ]
        rangeSegments = [ ((i, low), (i, high)) for i, low, high in zip(xrange(len(self.data)), self.data.low, self.data.high) if low != -1 ]
        r,g,b = colorConverter.to_rgb(self.colorup)
        colorup = r,g,b,self.alpha
        r,g,b = colorConverter.to_rgb(self.colordown)
        colordown = r,g,b,self.alpha
        colord = { True : colorup,
                   False : colordown,
                   }
        colors = [colord[open<close] for open, close in zip(self.data.open, self.data.close) if open!=-1 and close !=-1]
        assert(len(barVerts)==len(rangeSegments))
        useAA = 0,  # use tuple here
        lw = 0.5,   # and here
        r,g,b = colorConverter.to_rgb(self.lc)
        linecolor = r,g,b,self.alpha
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
    """ 从信号坐标(时间， 价格)中绘制交易信号。 """
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
    """ 从价格和持仓数据中绘制交易信号图。 """
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
