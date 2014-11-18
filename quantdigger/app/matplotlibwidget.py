__author__ = 'Wenwei Huang'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.finance import *
from PyQt4 import QtCore
from utils import fromUtf8
import numpy as np
import matplotlib.dates as mdates
from datetime import date, time, datetime, timedelta

from utils import WindowSize
import config

import logging
logger = logging.getLogger(__name__)

class SnaptoCursor(object):
    def __init__(self, ax):
        self.x, self.y = None, None
        self.lx = ax.axhline(color='k', linestyle=':')
        self.ly = ax.axvline(color='k', linestyle=':')
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        self.txt = ax.text(0.005, 0.99, '', transform=ax.transAxes, name='monospace', 
                           size='smaller', va='top', bbox=props, alpha=0.5)
    
    def set_data(self, date, open, high, low, close, vol):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vol = vol
        self.x = date
        self.y = self.close
        
    def mouse_move(self, event):
        if not event.inaxes: return
        if self.x is None or self.y is None: return
        x, y = event.xdata, event.ydata
        idx = np.searchsorted(self.x, x)
        if idx >= len(self.x): return
        x = self.x[idx]
        y = self.y[idx]
        # update the line positions self.ly.set_xdata(x)
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)
        
        text = []
        open = self.open[idx] if self.open is not None and idx < len(self.open) else None
        close = self.close[idx] if self.close is not None and idx < len(self.close) else None
        high = self.high[idx] if self.high is not None and idx < len(self.high) else None
        low = self.low[idx] if self.low is not None and idx < len(self.low) else None
        vol = self.vol[idx] if self.vol is not None and idx < len(self.vol) else None
        day = mdates.num2date(x)
        if day.time() == time(0,0):
            date_str = datetime.strftime(day, '%b %d %Y')
        else:
            date_str = datetime.strftime(day, '%b %d %Y %H:%M:%S')
        text.append("{0:>5s} {1:<12s}".format('Date', date_str))
        if open:
            text.append("{0:>5s} {1:.2f}".format('Open', open))
        if close:
            text.append("{0:>5s} {1:.2f}".format('Close', close))
        if high:
            text.append("{0:>5s} {1:.2f}".format('High', high))
        if low:
            text.append("{0:>5s} {1:.2f}".format('Low', low))
        if vol:
            text.append("{0:>5s} {1:.2f}M".format('Vol', (float(vol)/1000000)))
        self.txt.set_text('\n'.join(text))

    def cleanup(self):
        self.x, self.y = None, None
        self.lx.remove()
        self.ly.remove()
        self.txt.remove()

class PointMarker(object):
    def __init__(self, ax, color='k'):
        self.marker,  = ax.plot(-1, -1, 'o', color=color, alpha=0.5, zorder=10)

    def set_data(self, x, y):
        self.x = x
        self.y = y

    def mouse_move(self, event):
        if not event.inaxes: return
        if self.x is None or self.y is None: return
        x, y = event.xdata, event.ydata
        idx = np.searchsorted(self.x, x)
        if idx >= len(self.x): return
        x = self.x[idx]
        y = self.y[idx]
        self.marker.set_xdata(x)
        self.marker.set_ydata(y)

    def cleanup(self):
        self.marker.remove()

class VolumeBars(object):
    def __init__(self, ax, dates, opens, closes, volumes):
        self.dates = dates
        self.opens = opens
        self.closes = closes
        self.volumes = [float(v)/1e6 for v in volumes]
        self.ax = ax

    def add_bars(self, colorup='g', colordown='r', alpha=0.5, width=1):
        r,g,b = colorConverter.to_rgb(colorup)
        colorup = r,g,b,alpha
        r,g,b = colorConverter.to_rgb(colordown)
        colordown = r,g,b,alpha
        colord = {True: colorup, False: colordown}
        colors = [colord[open<close] for open, close in zip(self.opens, self.closes)]

        delta = width/2.0
        bars = [((x-delta, 0), (x-delta, y), (x+delta, y), (x+delta, 0)) 
            for x, y in zip(self.dates, self.volumes)]

        barCollection = PolyCollection(bars, facecolors = colors)

        self.ax.step(self.dates, self.volumes)
        #self.ax.add_collection(barCollection)
        #self.ax.bar(self.dates, self.volumes)
        #self.ax.plot(self.dates, self.volumes)

        xmin, xmax = self.ax.get_xlim()
        ys = [y for x, y in zip(self.dates, self.volumes) if xmin<=x<=xmax]
        if ys:
            self.ax.set_ylim([0, max(ys)*10])

        for tick in self.ax.get_yticklabels():
            tick.set_visible(False)


class MatplotlibWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.volume_axes = self.fig.add_subplot(111)
        self.axes = self.volume_axes.twinx()
        super(MatplotlibWidget, self).__init__(self.fig)
        self.setParent(parent)
        self.cross_cursor = None
        self.marker = None
        self.volumn_bars = None
        self.data = None
        self.main_x = None
        self.main_y = None
        self.press = None

    def connect(self):
        self.cidpress = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect(
            "button_release_event", self.on_release)
        self.cidmotion = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_motion)

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidpress)

    def set_data(self, data):
        if data is None: return
        self.data = data
        dates = self.data['datetime'].values if 'datetime' in self.data.columns else None
        opens = self.data['open'].values if 'open' in self.data.columns else None
        highs = self.data['high'].values if 'high' in self.data.columns else None
        lows = self.data['low'].values if 'low' in self.data.columns else None
        closes = self.data['close'].values if 'close' in self.data.columns else None
        volumes = self.data['volume'].values if 'volume' in self.data.columns else None
        self.main_x = dates
        self.main_y = closes

        if self.cross_cursor:
            self.cross_cursor.cleanup()
        if self.marker:
            self.marker.cleanup()
        self.cross_cursor = SnaptoCursor(self.axes)
        self.cross_cursor.set_data(dates, opens, highs, lows, closes, volumes)
        self.marker = PointMarker(self.axes)
        self.marker.set_data(dates, closes)

        self.volumn_bars = VolumeBars(self.volume_axes, dates, opens, closes, volumes).add_bars()

        xmin, xmax = min(self.main_x), max(self.main_x)
        self.axes.set_xlim([xmin, xmax])
        self.adjust_ylim(xmin, xmax)

    def setxlim(self, size):
        if self.main_x is None or self.main_y is None: return
        xmax = max(self.main_x)
        date = mdates.num2date(xmax).date()
        if size == WindowSize.ONEDAY:
            return # requires per min quotes
        elif size == WindowSize.FIVEDAY:
            return # requires per min quotes
        elif size == WindowSize.ONEMONTH:
            xmin = mdates.date2num(date-timedelta(days=30))
        elif size == WindowSize.THREEMONTH:
            xmin = mdates.date2num(date-timedelta(days=90))
        elif size == WindowSize.SIXMONTH:
            xmin = mdates.date2num(date-timedelta(days=180))
        elif size == WindowSize.ONEYEAR:
            xmin = mdates.date2num(date-timedelta(days=365))
        elif size == WindowSize.TWOYEAR:
            xmin = mdates.date2num(date-timedelta(days=365*2))
        elif size == WindowSize.FIVEYEAR:
            xmin = mdates.date2num(date-timedelta(days=365*5))
        elif size == WindowSize.MAX:
            xmin = min(self.main_x)

        self.axes.set_xlim([xmin, xmax])
        self.adjust_ylim(xmin, xmax)
        self.fig.canvas.draw()

    def adjust_ylim(self, xmin, xmax):
        if self.main_x is None or self.main_y is None: return
        ys = [y for x, y in zip(self.main_x, self.main_y) if xmin<=x<=xmax]
        ymin = min(ys) - 0.1*(max(ys)-min(ys))
        ymax = max(ys) + 0.1*(max(ys)-min(ys))
        self.axes.set_ylim([ymin, ymax])
        self.fig.canvas.draw()

    def draw_data(self):
        if self.main_x is None or self.main_y is None: return
        self.axes.plot_date(self.main_x, self.main_y, '-', color=config.main_curve_color)
        self.fig.autofmt_xdate()
        self.axes.grid(color='k', linestyle='-', linewidth=1, alpha=0.1)

        self.axes.yaxis.tick_right()
        self.fig.canvas.draw()

    def on_press(self, event):
        if event.inaxes != self.axes: return
        self.press = event.xdata, event.ydata

    def on_release(self, event):
        self.press = None
        self.fig.canvas.draw()

    def on_motion(self, event):
        if event:
            logger.debug(event.__dict__)
            logger.debug("%s %s %s %s %s" % (
                event.name, event.xdata, event.ydata, event.x, event.y))
            if self.cross_cursor:
                self.cross_cursor.mouse_move(event)
                self.marker.mouse_move(event)
                self.fig.canvas.draw()

            # drag
            if self.press is None: return
            if event.xdata is None: return
            xpress, ypress = self.press
            dx =  xpress - event.xdata
            if self.main_x is None or self.main_y is None: return
            xmin, xmax = self.axes.get_xlim()
            xmin = xmin+dx
            xmax = xmax+dx
            if min(self.main_x) > xmin or max(self.main_x) < xmax: return

            self.axes.set_xlim([xmin, xmax])
            self.adjust_ylim(xmin, xmax)

