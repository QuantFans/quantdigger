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




from __future__ import print_function
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter

from quantdigger.kernel.datasource.data import csv2frame

r = csv2frame("IF000.SHFE-10.Minute.csv")


class MyFormatter(Formatter):
    #def __init__(self, dates, fmt='%Y-%m-%d'):
    def __init__(self, dates, fmt='%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''
        print(ind)

        return self.dates[ind].strftime(self.fmt)

formatter = MyFormatter(r.index)

fig, ax = plt.subplots()

ax.xaxis.set_major_formatter(formatter)
ax.set_xlim(10, 100)

ax.plot(numpy.arange(len(r)), r.close )
#fig.autofmt_xdate()
plt.show()
