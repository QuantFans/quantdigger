# -*- coding: utf-8 -*-
#import os, sys
#sys.path.append(os.path.join('..', '..'))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.widgets.mplotwidgets import widgets
from quantdigger.technicals.common import MA, Volume
import pandas as pd


price_data = pd.read_csv('./data/IF000.csv', index_col=0, parse_dates=True)
print len(price_data)
fig = plt.figure()
frame = widgets.TechnicalWidget(fig, price_data, height=0.85)
frame.init_layout(50, 4, 1)
ax_candles,  ax_volume = frame.get_subwidgets()

# 添加k线和交易信号。
kwindow = widgets.CandleWindow("kwindow", 100, 50)
candle_widget = frame.add_widget(0, kwindow, True)
candle_widget.plot(price_data)

# 添加指标
ma = frame.add_technical(0, MA(price_data.close, 20, 'MA20', 'y', 2))
frame.add_technical(0, MA(price_data.close, 30, 'MA30', 'b', 2))
frame.add_technical(1, Volume(price_data.open, price_data.close, price_data.vol))
frame.draw_widgets()


# at most 5 ticks, pruning the upper and lower so they don't overlap
# with other ticks
ax_volume.yaxis.set_major_locator(widgets.MyLocator(5, prune='both'))

plt.show()
