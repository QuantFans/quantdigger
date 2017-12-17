# -*- coding: utf-8 -*-
import six
from six.moves import range
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from quantdigger.widgets.mplotwidgets import widgets, mplots
from quantdigger.widgets.mplotwidgets.mplots import Candles
from quantdigger.technicals.common import Line, LineWithX, Volume


def xticks_to_display(data_length):
    # six.print_(r.index[0].weekday())
    interval = data_length / 5
    v = 0
    xticks = []
    for i in range(0, 6):
        xticks.append(v)
        v += interval
    return xticks


def plot_strategy(price_data, technicals={}, deals=[], curve=[], marks=[]):
    """
        显示回测结果。
    """
    six.print_("plotting..")
    fig = plt.figure()
    frame = widgets.TechnicalWidget(fig, price_data)
    axes = frame.init_layout(
        50,         # 窗口显示k线数量。
         4, 1     # 两个1:1大小的窗口
    )

    # 绘制第一个窗口
    # 添加k线
    subwidget1 = widgets.FrameWidget(axes[0], "subwidget1", 100, 50)
    candles = Candles(price_data, None, 'candles')
    subwidget1.add_plotter(candles, False)
    #subwidget1.plot(price_data)
    # 交易信号。
    if deals:
        signal = mplots.TradingSignalPos(price_data, deals, lw=2)
        subwidget1.add_plotter(signal, False)
    if len(curve) > 0:
        curve = Line(curve)
        subwidget1.add_plotter(curve, True)
    # 添加指标
    for name, indic in six.iteritems(technicals):
        subwidget1.add_plotter(indic, False)

    # 绘制第2个窗口
    subwidget2 = widgets.FrameWidget(axes[1], "subwidget2", 100, 50)
    volume_plotter = Volume(price_data.open, price_data.close, price_data.volume)
    subwidget2.add_plotter(volume_plotter, False)

    subwidgets = [subwidget1, subwidget2]

    ### 绘制标志
    if marks:
        if marks[0]:
            # plot lines
            for name, values in six.iteritems(marks[0]):
                v = values[0]
                ith_ax = v[0]
                twinx = v[1]
                line_pieces = [[v[2]], [v[3]], v[4], v[5], v[6]]
                line = []
                for v in values[1: ]:
                    ## @TODO 如果是带“点”的，以点的特征聚类，会减少绘图对象的数目
                    x, y, style, lw, ms = v[2], v[3], v[4], v[5], v[6]
                    if style != line_pieces[2] or lw != line_pieces[3] or ms != line_pieces[4]:
                        line.append(line_pieces)
                        line_pieces = [[x], [y], style, lw, ms]
                    else:
                        line_pieces[0].append(x)
                        line_pieces[1].append(y)
                line.append(line_pieces)
                for v in line:
                    ## @TODO 这里的sytle明确指出有点奇怪，不一致。
                    x, y, style, lw, marksize = v[0], v[1], v[2], v[3], v[4]
                    curve = LineWithX(x, y, style=style, lw=lw, ms=marksize)
                    subwidgets[ith_ax].add_plotter(curve, twinx)
        if marks[1]:
            # plot texts
            for name, values in six.iteritems(marks[1]):
                for v in values:
                    ith_ax, x, y, text = v[0], v[1], v[2], v[3]
                    color, size, rotation = v[4], v[5], v[6]
                    ## @TODO move to text plotter
                    frame.plot_text(name, ith_ax, x, y, text, color, size, rotation)

    frame.add_widget(0, subwidget1, True)
    frame.add_widget(1, subwidget2, True)
    frame.draw_widgets()
    plt.show()


def plot_curves(data, colors=[], lws =[], names=[]):
    """ 画资金曲线

    Args:
        data (list): [pd.Series]

        colors (list): [str]

        lws (list): [int.]
    """
    assert(len(data) > 0)
    if colors:
        assert(len(data) == len(colors))
    else:
        colors = ['b'] * len(data)
    if lws:
        assert(len(data) == len(lws))
    else:
        lws = [1] * len(data)
    if names:
        assert(len(data) == len(names))
    # 画资金曲线
    # six.print_(curve.equity)
    fig2 = plt.figure()
    lns = []
    ax = fig2.add_axes((0.1, 0.1, 0.8, 0.8))
    ax.xaxis.set_major_formatter(TimeFormatter(data[0].index, '%Y-%m-%d'))
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    # ax.get_yaxis().get_major_formatter().set_scientific(False)
    ax.set_xticks(xticks_to_display(len(data[0])))
    lns = ax.plot(data[0], c=colors[0])
    for tl in ax.get_yticklabels():
        tl.set_color(colors[0])
    if len(data) > 1:
        for i in range(1, len(data)):
            new_ax = ax.twinx()
            lns += new_ax.plot(data[i], c=colors[i])
            # new_ax.set_ylabel('sin', color=colors[i])
            for tl in new_ax.get_yticklabels():
                tl.set_color(colors[i])
            # new_ax.set_yticks
    # ax.legend(lns, ['aaa', 'bbbb', 'ccc'])
    if names:
        ax.legend(lns, names, loc='upper left').get_frame().set_alpha(0.5)
    plt.show()


class TimeFormatter(Formatter):
    # def __init__(self, dates, fmt='%Y-%m-%d'):
    # 分类 －－format
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''
        return self.dates[ind].strftime(self.fmt)
