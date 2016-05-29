# -*- coding: utf-8 -*-
#import os, sys
#sys.path.append(os.path.join('..', '..'))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.widgets.mplotwidgets import widgets, mplots
from quantdigger.technicals.common import MA, Volume
from quantdigger.digger import sugar
import pandas as pd


# prepare data
def get_stock_signal_data():
    from matplotlib.colors import colorConverter

    signal_data = pd.read_csv('./work/signal_IF000.csv', index_col=0, parse_dates=True)
    price_data = pd.read_csv('./work/IF000.csv' , index_col=0, parse_dates=True)
    info = sugar.process_signal(signal_data, price_data)
    entry_x = []
    entry_y = info['entry_price'].tolist()
    exit_x = []
    exit_y = info['exit_price'].tolist()
    colors = []
    for t in info.index:
        entry_x.append(price_data.index.searchsorted(t))
    for t in info['exit_datetime'].values:
        exit_x.append(price_data.index.searchsorted(t))
    for i in range(len(info)):
        tr = info.ix[i]
        if tr['islong']:
            c = 'r' if tr['exit_price']>tr['entry_price'] else 'b'
        else:
            c = 'r' if tr['exit_price']<tr['entry_price'] else 'b'
        r,g,b = colorConverter.to_rgb(c)
        colors.append((r,g,b,1))
    return price_data, entry_x, entry_y, exit_x, exit_y, colors

#price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()


price_data = pd.read_csv('./work/IF111.csv', index_col=0, parse_dates=True)
#import matplotlib.font_manager as font_manager
print len(price_data)
fig = plt.figure()
frame = widgets.TechnicalWidget(fig, price_data)
frame.init_layout(50, 4, 1)
ax_candles,  ax_volume = frame.get_subwidgets()

# 添加k线和交易信号。
kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
candle_widget = frame.add_widget(0, kwindow, True)
#signal = mplots.TradingSignal(None, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), c=colors, lw=2)
#frame.add_technical(0, signal)

# 添加指标
ma = frame.add_technical(0, MA(price_data.close, 20, 'MA20', 'y', 2))
frame.add_technical(0, MA(price_data.close, 30, 'MA30', 'b', 2))
#frame.add_technical(1, RSI(None, price_data.close, 14, name='RSI', fillcolor='b'))
frame.add_technical(1, Volume(price_data.open, price_data.close, price_data.vol))
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
