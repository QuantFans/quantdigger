#!/usr/bin/env python
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import numpy as np
from widgets import *
from data import csv2frame, load_tradeinfo

fig = plt.figure(facecolor='white')
axk = plt.axes([0.1, 0.2, 0.8, 0.7], axisbg='k')
axk.grid(True)
xslider = plt.axes([0.1, 0.1, 0.8, 0.03])
#yslider = plt.axes([0.1, 0.05, 0.8, 0.03])
#ax.xaxis.set_minor_formatter(dayFormatter)


#price_data = csv2frame(os.getcwd() + "\\data\\stock_data\\_IF000.csv")
price_data = csv2frame(os.getcwd() + "/data/stock_data/_IF000.csv")
print os.getcwd() + "/data/stock_data/_IF000.csv"
print "plotting..." 
observer_slider = Slider(xslider, "slider", '', 0, len(price_data), len(price_data), len(price_data)/100, "%d")
kwindow = CandleWindow(axk, "kwindow", price_data, 100, 50)
kwindow.on_changed(observer_slider)
observer_slider.on_changed(kwindow)

from matplotlib.colors import colorConverter
info = load_tradeinfo("_djtrend2_IF000")
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
        c = 'r' if tr['exit_price']>tr['entry_price'] else 'w'
    else:
        c = 'r' if tr['exit_price']<tr['entry_price'] else 'w'
    r,g,b = colorConverter.to_rgb(c)
    colors.append((r,g,b,1))
slw = 2
signal = SignalWindow(axk, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), colors, slw)

#ax2.callbacks.connect('xlim_changed', rect)
c1 = Cursor(axk, useblit=True, color='white', linewidth=1, vertOn = True, horizOn = True)
plt.show()

