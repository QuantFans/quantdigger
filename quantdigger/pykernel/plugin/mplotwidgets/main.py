# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import techmplot
import matplotlib.pyplot as plt
import widgets
from indicator import *
from datasource.data import get_stock_signal_data
price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()

#import matplotlib.font_manager as font_manager
fig = plt.figure()
frame = techmplot.TechMPlot(fig, 4,3,1)
ax_candles, ax_rsi, ax_volume = frame

# 把窗口传给techplot, 连接信号
# 事件处理 ||||  绘图，数据的分离。
# twins窗口。
# rangew
# 事件从techplot传到PYQT

kwindow = widgets.CandleWindow(ax_candles, "kwindow", price_data, 100, 50)
signal = TradingSignal(zip(zip(entry_x,entry_y),zip(exit_x,exit_y)))
signal.plot_signal(ax_candles, colors, 2)

# 指标窗口
ma = frame.add_indicator(0, MA(price_data.close, 20, 'MA20', 'simple', 'y', 2))
frame.add_indicator(0, MA(price_data.close, 30, 'MA30', 'simple', 'b', 2))
frame.add_indicator(1, RSI(price_data.close, 14, name='RSI', fillcolor='b'))
frame.add_indicator(2, Volume(price_data.open, price_data.close, price_data.vol))
# legend
#props = font_manager.FontProperties(size=10)
#leg = ax_candles.legend(loc='center left', shadow=True, fancybox=True, prop=props)
#leg.get_frame().set_alpha(0.5)


#ax2t.set_yticks([])

# at most 5 ticks, pruning the upper and lower so they don't overlap
# with other ticks
ax_volume.yaxis.set_major_locator(techmplot.MyLocator(5, prune='both'))

# sharex 所有所有的窗口都移动
frame.slider.add_observer(kwindow)
kwindow.connect()
#frame.slider.add_observer(frame.rangew)

plt.show()
