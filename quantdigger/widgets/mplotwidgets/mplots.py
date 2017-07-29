# -*- coding: utf-8 -*-

import six
from six.moves import range
import numpy as np
import inspect
from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection


def override_attributes(method):
    # 如果plot函数不带绘图参数，则使用属性值做为参数。
    # 如果带参数，者指标中的plot函数参数能够覆盖本身的属性。
    def wrapper(self, widget, *args, **kwargs):
        self.widget = widget
        # 用函数中的参数覆盖属性。
        arg_names = inspect.getargspec(method).args[2:]
        method_args = {}
        obj_attrs = {}
        for i, arg in enumerate(args):
            method_args[arg_names[i]] = arg
        method_args.update(kwargs)

        try:
            for attr in arg_names:
                obj_attrs[attr] = getattr(self, attr)
        except Exception as e:
            six.print_(e)
            six.print_("构造函数和绘图函数的绘图属性参数不匹配。")
        obj_attrs.update(method_args)
        return method(self, widget, **obj_attrs)
    return wrapper


class Candles(object):
    """
    画蜡烛线。
    """
    def __init__(self, data, tracker, name='candle',
                 width=0.6, colorup='r', colordown='g',
                 lc='k', alpha=1):
        """ Represent the open, close as a bar line and high low range as a
        vertical line.


        ax          : an Axes instance to plot to

        width       : the bar width in points

        colorup     : the color of the lines where close >= open

        colordown   : the color of the lines where close <  open

        alpha       : bar transparency

        return value is lineCollection, barCollection
        """
        # super(Candles, self).__init__(tracker, name)
        self.data = data
        self.name = name
        self.width = width
        self.colorup = colorup
        self.colordown = colordown
        self.lc = lc
        self.alpha = alpha
        self.lineCollection = []
        self.barCollection = []

    # note this code assumes if any value open, close, low, high is
    # missing they all are missing
    @override_attributes
    def plot(self, widget, data, width=0.6,
             colorup='r', colordown='g', lc='k', alpha=1):

        if self.lineCollection:
            self.lineCollection.remove()
        if self.barCollection:
            self.barCollection.remove()

        self.set_yrange(data.low.values, data.high.values)
        self.data = data
        """docstring for plot"""
        delta = self.width / 2.
        barVerts = [((i - delta, open),
                     (i - delta, close),
                     (i + delta, close),
                     (i + delta, open))
                    for i, open, close in zip(range(len(self.data)),
                                              self.data.open,
                                              self.data.close)
                    if open != -1 and close != -1]
        rangeSegments = [((i, low), (i, high))
                         for i, low, high in zip(range(len(self.data)),
                                                 self.data.low,
                                                 self.data.high)
                         if low != -1]
        r, g, b = colorConverter.to_rgb(self.colorup)
        colorup = r, g, b, self.alpha
        r, g, b = colorConverter.to_rgb(self.colordown)
        colordown = r, g, b, self.alpha
        colord = {
            True: colorup,
            False: colordown,
        }
        colors = [colord[open < close]
                  for open, close in zip(self.data.open, self.data.close)
                  if open != -1 and close != -1]
        assert(len(barVerts) == len(rangeSegments))
        useAA = 0,  # use tuple here
        lw = 0.5,   # and here
        r, g, b = colorConverter.to_rgb(self.lc)
        linecolor = r, g, b, self.alpha
        self.lineCollection = LineCollection(rangeSegments,
                                             colors=(linecolor,),
                                             linewidths=lw,
                                             antialiaseds=useAA,
                                             zorder=0)

        self.barCollection = PolyCollection(barVerts,
                                            facecolors=colors,
                                            edgecolors=colors,
                                            antialiaseds=useAA,
                                            linewidths=lw,
                                            zorder=1)
        widget.autoscale_view()
        # add these last
        widget.add_collection(self.barCollection)
        widget.add_collection(self.lineCollection)
        return self.lineCollection, self.barCollection

    def set_yrange(self, lower, upper=[]):
        self.upper = upper if len(upper) > 0 else lower
        self.lower = lower

    def y_interval(self, w_left, w_right):
        if len(self.upper) == 2:
            return max(self.upper), min(self.lower)
        ymax = np.max(self.upper[w_left: w_right])
        ymin = np.min(self.lower[w_left: w_right])
        return ymax, ymin


class TradingSignal(object):
    """ 从信号坐标(时间， 价格)中绘制交易信号。 """
    def __init__(self, signal, name="Signal", c=None, lw=2):
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
    def __init__(self, price_data, deals, name="Signal", c=None, lw=2):
        self.signal = []
        self.colors = []
        price_data['row'] = [i for i in range(0, len(price_data))]
        for deal in deals:
            # ((x0, y0), (x1, y1))
            p = ((price_data.row[deal.open_datetime], deal.open_price),
                 (price_data.row[deal.close_datetime], deal.close_price))
            self.signal.append(p)
            self.colors.append(
                (1, 0, 0, 1) if deal.profit() > 0 else (0, 1, 0, 1))
        self.name = name

    def plot(self, widget, lw=2):
        useAA = 0,  # use tuple here
        signal = LineCollection(self.signal, colors=self.colors, linewidths=lw,
                                antialiaseds=useAA)
        widget.add_collection(signal)

    def y_interval(self, w_left, w_right):
        # @todo signal interval
        return 0, 100000000
