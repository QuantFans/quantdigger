# -*- coding: utf8 -*-
#import os, sys
#sys.path.append(os.path.join('..', '..'))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.widgets.mplotwidgets import widgets, mplots
from quantdigger.indicators.common import MA, RSI, Volume


from quantdigger.datasource.data import get_stock_signal_data
price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()


#import matplotlib.font_manager as font_manager
fig = plt.figure()
frame = widgets.MultiWidgets(fig, price_data, 50, 4,3,1)
ax_candles, ax_rsi, ax_volume = frame

# 添加k线和交易信号。
kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
candle_widget = frame.add_widget(0, kwindow, True)
signal = mplots.TradingSignal(None, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), c=colors, lw=2)
frame.add_indicator(0, signal)

# 添加指标
ma = frame.add_indicator(0, MA(None, price_data.close, 20, 'MA20', 'y', 2))
frame.add_indicator(0, MA(None, price_data.close, 30, 'MA30', 'b', 2))
frame.add_indicator(1, RSI(None, price_data.close, 14, name='RSI', fillcolor='b'))
frame.add_indicator(2, Volume(None, price_data.open, price_data.close, price_data.vol))
frame.draw_widgets()

# legend
#props = font_manager.FontProperties(size=10)
#leg = ax_candles.legend(loc='center left', shadow=True, fancybox=True, prop=props)
#leg.get_frame().set_alpha(0.5)


#ax2t.set_yticks([])

# at most 5 ticks, pruning the upper and lower so they don't overlap
# with other ticks
ax_volume.yaxis.set_major_locator(widgets.MyLocator(5, prune='both'))

# sharex 所有所有的窗口都移动
#frame.slider.add_observer(frame.rangew)
#ma('hhh')

plt.show()
