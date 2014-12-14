#!/usr/bin/env python
import matplotlib
matplotlib.use('TkAgg')
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from mplot_widgets.widgets import *
from datasource.data import get_stock_signal_data


fig = plt.figure(facecolor='white')
axk = plt.axes([0.1, 0.2, 0.8, 0.7], axisbg='k')
axk.grid(True)
xslider = plt.axes([0.1, 0.1, 0.8, 0.03])
#yslider = plt.axes([0.1, 0.05, 0.8, 0.03])
#ax.xaxis.set_minor_formatter(dayFormatter)


price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()

slw = 2
# setup windows
print("plotting.......")
observer_slider = Slider(xslider, "slider", '', 0, len(price_data), len(price_data), len(price_data)/100, "%d")
kwindow = CandleWindow(axk, "kwindow", price_data, 100, 50)

kwindow.on_changed(observer_slider)
observer_slider.on_changed(kwindow)
#signal = SignalWindow(axk, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), colors, slw)
c1 = Cursor(axk, useblit=True, color='white', linewidth=1, vertOn = True, horizOn = True)
plt.show()

