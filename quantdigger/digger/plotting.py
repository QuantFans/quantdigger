# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from quantdigger.widgets.mplotwidgets import widgets, mplots
from quantdigger.technicals import EquityCurve

def xticks_to_display(data_length):
    #print(r.index[0].weekday())
    interval = data_length / 5
    v = 0
    xticks = []
    for i in range(0, 6):
        xticks.append(v)
        v += interval
    return xticks


def plot_strategy(price_data, indicators={ }, deals=[], curve=[]):
    """ 
        显示回测结果。
    """
    print "plotting.."
    fig = plt.figure()
    frame = widgets.MultiWidgets(fig, price_data,
                                50         # 窗口显示k线数量。
                                #4, 1     # 两个1:1大小的窗口
                                )

    # 添加k线
    kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
    frame.add_widget(0, kwindow, True)
    ## 交易信号。
    if deals:
        signal = mplots.TradingSignalPos(price_data, deals, lw=2)
        frame.add_indicator(0, signal)
    if len(curve) > 0:
        curve = EquityCurve(curve)
        frame.add_indicator(0, curve, True)
    ## @bug indicators导致的双水平线!
    ## @todo 完mplot_demo上套。
    #frame.add_indicator(0, Volume(None, price_data.open, price_data.close, price_data.volume))

    ## 添加指标
    for name, indic in indicators.iteritems():
        frame.add_indicator(0, indic)
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
    #print curve.equity
    fig2 = plt.figure()
    lns = []
    ax = fig2.add_axes((0.1, 0.1, 0.8, 0.8))
    ax.xaxis.set_major_formatter(TimeFormatter(data[0].index, '%Y-%m-%d' ))
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    #ax.get_yaxis().get_major_formatter().set_scientific(False)
    ax.set_xticks(xticks_to_display(len(data[0])))
    lns = ax.plot(data[0], c=colors[0])
    for tl in ax.get_yticklabels():
        tl.set_color(colors[0])
    if len(data) > 1:
        for i in range(1, len(data)):
            new_ax = ax.twinx()
            lns += new_ax.plot(data[i], c=colors[i])
            #new_ax.set_ylabel('sin', color=colors[i])
            for tl in new_ax.get_yticklabels():
                tl.set_color(colors[i])
            #new_ax.set_yticks
    #ax.legend(lns, ['aaa', 'bbbb', 'ccc'])
    if names:
        ax.legend(lns, names, loc='upper left').get_frame().set_alpha(0.5)
    plt.show()


class TimeFormatter(Formatter):
    #def __init__(self, dates, fmt='%Y-%m-%d'):
    # 分类 －－format
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''

        return self.dates[ind].strftime(self.fmt)
