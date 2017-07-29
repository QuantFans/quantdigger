# -*- coding: utf-8 -*-
import matplotlib
import pandas as pd

from quantdigger.widgets.mplotwidgets import widgets
from quantdigger.widgets.mplotwidgets.mplots import Candles
from quantdigger.technicals.common import MA, Volume

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

price_data = pd.read_csv('data/IF000.csv', index_col=0, parse_dates=True)
fig = plt.figure()

frame = widgets.TechnicalWidget(fig, price_data)
axes = frame.init_layout(50,         # 窗口显示k线数量。
                         4,
                         1)     # 两个1:1大小的窗口

candle_widget = widgets.FrameWidget(axes[0], "candle_widget", 100, 50)
candles = Candles(price_data, None, 'candles')
ma30 = MA(price_data.close, 30, 'MA30', 'b', 2)
ma20 = MA(price_data.close, 20, 'MA20', 'y', 2)
candle_widget.add_plotter(candles, False)
candle_widget.add_plotter(ma30, False)
candle_widget.add_plotter(ma20, False)

volume_widget = widgets.FrameWidget(axes[1], "volume_widget ", 100, 50)
volume_plotter = Volume(price_data.open, price_data.close, price_data.vol)
volume_widget.add_plotter(volume_plotter, False)

frame.add_widget(0, candle_widget, True)
frame.add_widget(1, volume_widget, True)
frame.draw_widgets()
plt.show()
