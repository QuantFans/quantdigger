# -*- coding: utf-8 -*-
#import matplotlib
#matplotlib.use('TkAgg')
#import datetime
#import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.dates as dates
#import matplotlib.cbook as cbook


#from quantdigger.kernel.datasource.data import csv2frame

#fig, ax = plt.subplots()
#fig, ax2 = plt.subplots()

#days = mdates.HourLocator()  # every month
#mins = mdates.MinuteLocator(interval=15)  # should not be major, if there are many ticks
#yearsFmt = mdates.DateFormatter('%Y')

## load a numpy record array from yahoo csv data with fields date,
## open, close, volume, adj_close from the mpl-data/example directory.
## The record array stores python datetime.date as an object array in
## the date column
##datafile = cbook.get_sample_data('goog.npy')
##r = np.load(datafile).view(np.recarray)
#r = csv2frame("IF000.SHFE-10.Minute.csv")



## format the ticks
##ax.xaxis.set_major_locator(days)
##ax.xaxis.set_minor_locator(mins)
##ax.xaxis.set_major_formatter(yearsFmt)
#max=10
#ax.plot(r.index[0: max], r.close[0:max])
#ax2.plot(r.close[0:max])
##datemin = datetime.date(r.index.min().year, r.index.min().month, r.index.min().day)
##datemax = datetime.date(r.index.min().year, r.index.min().month, r.index.min().day+1)
##print datemin, datemax
##ax.set_xlim(datemin, datemax)
## format the coords message box
##def price(x): return '$%1.2f'%x
##ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
#ax.format_xdata = mdates.DateFormatter('%H:%M')
##ax.format_ydata = price
##ax.grid(True)

## rotates and right aligns the x labels, and moves the bottom of the
## axes up to make room for them
##fig.autofmt_xdate()

#plt.show()




import numpy
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter

from quantdigger.datasource.data import csv2frame

r = csv2frame("IF000.SHFE-10.Minute.csv")


class MyFormatter(Formatter):
    #def __init__(self, dates, fmt='%Y-%m-%d'):
    # 分类 －－format
    def __init__(self, dates, fmt='%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''

        return self.dates[ind].strftime(self.fmt)

formatter = MyFormatter(r.index)

fig, ax = plt.subplots()

ax.xaxis.set_major_formatter(formatter)
ax.set_xlim(10, 100)
# 分类 -- xticks 的时间间隔
# 停止的时候决定tick显示哪个
ax.set_xticks([20,40])


ax.plot(numpy.arange(len(r)), r.close )
#fig.autofmt_xdate()
#plt.show()
print("-----------")
#dates = pd.Series(pd.date_range('2015-01-01', '2016-12-31'))  # Timestamps
dates = pd.Series(r.index)  # Timestamps
today = pd.Timestamp('now')                                   # Timestamp
print(dates.dt.year[0])
print(dates.dt.year[1])
print(dates.dt.hour[0])
print(dates.dt.hour[1])
print(dates.dt.minute[0])
print(dates.dt.minute[1])
print(dates.dt.minute[2])
print("******")
print(r.index[0].year)
print(r.index[0].weekday())
print(r.index[30].weekday())
print("******")
#print(dates[(dates.dt.year == today.year) & 
    #(dates.dt.month == today.month) &
    #(dates.dt.day == today.day)])
