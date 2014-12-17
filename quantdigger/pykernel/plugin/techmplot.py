# -*- coding: utf8 -*-
from matplotlib.widgets import Cursor
from matplotlib.widgets import MultiCursor
import matplotlib.pyplot as plt

class TechMPlot(object):
    def __init__(self, *args):
        self.fig = plt.figure()
        self.cross_cursor = None
        self.v_cursor = None
        self.add_subplot(*args)
        self.in_qt = False
        for ax in self.axes:
            ax.format_coord = self.format_coord 
        self.connect()

    def set_cursor(self):
        if len(self.axes) == 1:
            self.cross_cursor = Cursor(self.axes[0], useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        else:
            self.v_cursor = MultiCursor(self.fig.canvas, self.fig.axes, color='r', lw=2, horizOn=False, vertOn=True)



    def connect(self):
        """
        matplotlib信号连接。
        """
        self.cidpress = self.fig.canvas.mpl_connect( "button_press_event", self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect( "button_release_event", self.on_release)
        self.cidmotion = self.fig.canvas.mpl_connect( "motion_notify_event", self.on_motion)

        self.fig.canvas.mpl_connect('axes_enter_event', self.enter_axes)
        self.fig.canvas.mpl_connect('axes_leave_event', self.leave_axes)

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidpress)


    def on_press(self, event):
        print("press---")
        pass

    def on_release(self, event):
        print("release---")
        pass

    def on_motion(self, event):
        pass


    def enter_axes(self, event):
        #event.inaxes.patch.set_facecolor('yellow')
        # 只有当前axes会闪烁。
        if not self.in_qt:
            axes = [ax for ax in self.fig.axes if ax is not event.inaxes]
            self.v_cursor = MultiCursor(event.canvas, axes, color='r', lw=2, horizOn=False, vertOn=True)
            self.cross_cursor = Cursor(event.inaxes, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
            event.canvas.draw()
        print("enter---")

    def leave_axes(self, event):
        if not self.in_qt:
            self.v_cursor = None
            self.cross_cursor = None
        #event.inaxes.patch.set_facecolor('white')
        #event.canvas.draw()
        print("leave---")

    def add_subplot(self, *args):
        num_axes = sum(args)
        for i, ratio in enumerate(args):
            if i > 0:
                plt.subplot2grid((num_axes, 1), (sum(args[:i]), 0),
                                 rowspan = ratio, sharex = self.fig.axes[0])
            else:
                plt.subplot2grid((num_axes, 1), (sum(args[:i]), 0), rowspan = ratio)

        #self.slider = mwidgets.Slider(xslider, "slider", '', 0, len(price_data), len(price_data), len(price_data)/100, "%d")
        ##kwindow.on_changed(observer_slider)
        ##observer_slider.on_changed(kwindow)
        #signal = SignalWindow(axk, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), colors, slw)


    def subplots_adjust(self, left, bottom, right, top, wspace=None, hspace=None):
        plt.subplots_adjust(left, bottom, right, top, wspace, hspace)

    @property
    def axes(self):
        return self.fig.axes

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

