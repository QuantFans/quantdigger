# -*- coding: utf8 -*-
from matplotlib.widgets import Cursor
from matplotlib.widgets import MultiCursor
import matplotlib.pyplot as plt
import widgets

import os, sys
sys.path.append(os.path.join('..', '..'))
from datasource.data import get_stock_signal_data
price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()

class TechMPlot(object):
    def __init__(self, fig, *args):
        self.fig = fig
        self.cross_cursor = None
        self.v_cursor = None
        self.in_qt = False
        for ax in self.axes:
            ax.format_coord = self.format_coord 
        self.left, self.width = 0.1, 0.8
        self.add_subplot(*args)
        self.connect()

    def init_qt(self):
        """docstring for set_qt""" 
        self.in_qt = True
        #if len(self.axes) == 1:
            #self.cross_cursor = Cursor(self.axes[0], useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        #else:
            #self.v_cursor = MultiCursor(self.fig.canvas, self.axes, color='r', lw=2, horizOn=False, vertOn=True)

    def connect(self):
        """
        matplotlib信号连接。
        """
        #self.cidpress = self.fig.canvas.mpl_connect( "button_press_event", self.on_press)
        #self.cidrelease = self.fig.canvas.mpl_connect( "button_release_event", self.on_release)
        #self.cidmotion = self.fig.canvas.mpl_connect( "motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect('axes_enter_event', self.enter_axes)
        self.fig.canvas.mpl_connect('axes_leave_event', self.leave_axes)

        self.slider.connect()
        self.kwindow.connect()


    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidpress)


    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        #self.fig.canvas.draw()
        pass

    def enter_axes(self, event):
        #event.inaxes.patch.set_facecolor('yellow')
        # 只有当前axes会闪烁。
        if not self.in_qt:
            axes = [ax for ax in self.axes if ax is not event.inaxes]
            if event.inaxes is not self.slider_ax:
                self.v_cursor = MultiCursor(event.canvas, axes, color='r', lw=2, horizOn=False, vertOn=True)
                self.cross_cursor = Cursor(event.inaxes, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        if event.inaxes is not self.slider_ax:
            event.canvas.draw()
        print("enter---")

    def leave_axes(self, event):
        if not self.in_qt:
            self.v_cursor = None
            self.cross_cursor = None
            event.canvas.draw()  # 在qt中不起作用，还影响流畅。
        print("leave---")

    def add_subplot(self, *args):
        bottom = 0.1
        self.slider_ax = self.fig.add_axes([self.left, 0, self.width, 0.1])
        self.slider = widgets.Slider(self.slider_ax, "slider", '', 0, len(price_data), len(price_data), len(price_data)/100, "%d")

        num_axes = sum(args)
        unit = (1.0 - bottom) / num_axes
        for i, ratio in enumerate(args):
            rect = [self.left, bottom, self.width, unit * ratio]
            if i > 0:
                print len(self.axes)
                print len(self.fig.axes)
                self.fig.add_axes(rect, sharex=self.axes[0])  #axisbg=axescolor)
            else:
                self.fig.add_axes(rect)
            bottom += unit * ratio

        for ax in self.axes:
            ax.grid(True)

        self.kwindow = widgets.CandleWindow(self.axes[1], "kwindow", price_data, 100, 50)
        self.kwindow.add_observer(self.slider)
        self.slider.add_observer(self.kwindow)
        #signal = SignalWindow(axk, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), colors, slw)


    def subplots_adjust(self, left, bottom, right, top, wspace=None, hspace=None):
        plt.subplots_adjust(left, bottom, right, top, wspace, hspace)

    @property
    def axes(self):
        """ 返回滚动条以外的区域 """
        return self.fig.axes[1:]

    def format_coord(self, x, y):
        """ 状态栏信息显示 """
        return "x=%.2f, y=%.2f" % (x, y)

    def draw_axes(self, ith, func):
        """传递绘图函数，画第ith个图。
        
        Args:
            ith (number): 待绘axes的编号。
            func (function): 绘图函数。
        """
        try:
            axes = self.axes[ith]
        except IndexError as e:
            print(e)
        else:
            func(axes)

