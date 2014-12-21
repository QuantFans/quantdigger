# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import techmplot
import matplotlib.pyplot as plt
import widgets
from indicator import *
from datasource.data import get_stock_signal_data
price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()

import matplotlib.finance as finance
import matplotlib.font_manager as font_manager
fig = plt.figure()
obj = techmplot.TechMPlot(fig, 4,3,1)
ax_candles, ax_rsi, ax_volume = obj

# 把窗口传给techplot, 连接信号
# 事件处理 ||||  绘图，数据的分离。
# twins窗口。
# rangew
# 事件从techplot传到PYQT

kwindow = widgets.CandleWindow(ax_candles, "kwindow", price_data, 100, 50)
signal = TradingSignal(zip(zip(entry_x,entry_y),zip(exit_x,exit_y)))
signal.plot_signal(ax_candles, colors, 2)

# 指标窗口
ma20 = MA(price_data.close, 20, 'simple', 'MA20')
ma20.plot_ma(ax_candles, 'y', 2)
ma30 = MA(price_data.close, 30, 'simple', 'MA30')
ma30.plot_ma(ax_candles, 'b', 2)
# legend
props = font_manager.FontProperties(size=10)
leg = ax_candles.legend(loc='center left', shadow=True, fancybox=True, prop=props)
leg.get_frame().set_alpha(0.5)

rsi = RSI(price_data.close, 14, name= 'RSI')
rsi.plot_rsi(ax_rsi, 'b')

#ax2t.set_yticks([])

volume = price_data['vol']
finance.volume_overlay(ax_volume, price_data['open'], price_data['close'],
                       volume, colorup = 'r', colordown = 'b', width = 1)
# at most 5 ticks, pruning the upper and lower so they don't overlap
# with other ticks
ax_volume.yaxis.set_major_locator(techmplot.MyLocator(5, prune='both'))

# sharex 所有所有的窗口都移动
obj.slider.add_observer(kwindow)
kwindow.connect()
#obj.slider.add_observer(obj.rangew)

plt.show()
