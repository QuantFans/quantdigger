# -*- coding: utf-8 -*-
#import os, sys
#sys.path.append(os.path.join('..', '..'))
import matplotlib
from matplotlib.widgets import Button
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

from quantdigger.widgets.mplotwidgets import widgets
from quantdigger.technicals.common import MA, Volume
from quantdigger.event.rpc import ZMQRPCClient

price_data = pd.read_csv('./data/IF000.csv', index_col=0, parse_dates=True)
print len(price_data)

fig = plt.figure()


class MainWindow(object):
    """docstring for Mai"""
    def __init__(self, arg):
        self._rpcclient = ZMQRPCClient()

    def next(self, event):

        plt.draw()

    def prev(self, event):
        plt.draw()
    
    

callback = MainWindow()
axprev = fig.add_axes([0.1, 0.92, 0.07, 0.075], axisbg='gray')
axnext = fig.add_axes([0.2, 0.92, 0.07, 0.075], axisbg='gray')
bnext = Button(axnext, '1Day')
bnext.on_clicked(callback.next)
bprev = Button(axprev, '1Min')
bprev.on_clicked(callback.prev)


frame = widgets.TechnicalWidget(fig, price_data, height=0.85)
frame.init_layout(50, 4, 1)
ax_candles,  ax_volume = frame.get_subwidgets()

# 添加k线和交易信号。
kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
candle_widget = frame.add_widget(0, kwindow, True)

# 添加指标
ma = frame.add_technical(0, MA(price_data.close, 20, 'MA20', 'y', 2))
frame.add_technical(0, MA(price_data.close, 30, 'MA30', 'b', 2))
frame.add_technical(1, Volume(price_data.open, price_data.close, price_data.vol))
frame.draw_widgets()


# at most 5 ticks, pruning the upper and lower so they don't overlap
# with other ticks
ax_volume.yaxis.set_major_locator(widgets.MyLocator(5, prune='both'))

plt.show()
