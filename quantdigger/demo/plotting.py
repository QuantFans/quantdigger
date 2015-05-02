# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.plugin.mplotwidgets import techmplot
from quantdigger.plugin.mplotwidgets import widgets
from quantdigger.kernel.indicators.common import *

def plot_result(price_data, indicators, signals, blotter):
    """ 
        显示回测结果。
    """
    blotter.create_equity_curve_dataframe()
    print blotter.output_summary_stats()

    fig = plt.figure()
    frame = techmplot.TechMPlot(fig,
                                price_data,
                                50          # 窗口显示k线数量。
                                )

    # 添加k线
    kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
    frame.add_widget(0, kwindow, True)
    # 交易信号。
    signal = TradingSignalPos(None, price_data, signals, lw=2)
    frame.add_indicator(0, signal)

    # 添加指标
    k_axes, = frame
    for indic in indicators:
        indic.plot(k_axes)
    frame.draw_window()

    fig2 = plt.figure()
    ax = fig2.add_axes((0.1, 0.1, 0.9, 0.9))
    ax.plot(blotter.equity_curve.total)
    plt.show()
