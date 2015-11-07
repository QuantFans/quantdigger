# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.widgets.mplotwidgets import widgets, mplots
from quantdigger.digger import finance
from datetime import datetime
from matplotlib.ticker import Formatter

def xticks_to_display(data_length):
    #print(r.index[0].weekday())
    interval = data_length / 5
    v = 0
    xticks = []
    for i in range(0, 6):
        xticks.append(v)
        v += interval
    return xticks


def plot_result(price_data, indicators, signals,
        blotter):
    """ 
        显示回测结果。
    """
    try:
        dts = map(lambda x : datetime.fromtimestamp(x / 1000), price_data.index)
        price_data.index = dts
        curve = finance.create_equity_curve_dataframe(blotter.all_holdings)
        print finance.output_summary_stats(curve)

        fig = plt.figure()
        frame = widgets.MultiWidgets(fig,
                                    price_data,
                                    50          # 窗口显示k线数量。
                                    )

        # 添加k线
        kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
        frame.add_widget(0, kwindow, True)
        # 交易信号。
        signal = mplots.TradingSignalPos(None, price_data, signals, lw=2)
        frame.add_indicator(0, signal)

        # 添加指标
        k_axes, = frame
        for indic in indicators:
            indic.plot(k_axes)
        frame.draw_widgets()

        fig2 = plt.figure()
        ax = fig2.add_axes((0.1, 0.1, 0.8, 0.8))
        delta = curve.index[1] - curve.index[0]
        ax.xaxis.set_major_formatter(TimeFormatter(curve.index, '%Y-%m-%d' ))
        ax.set_xticks(xticks_to_display(len(curve)))
        ax.plot(curve.equity)
        plt.show()

    except Exception, e:
        print(e)

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
