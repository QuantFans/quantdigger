# -*- coding: utf8 -*-
from matplotlib.widgets import MultiCursor
import os, sys
sys.path.append(os.path.join('..', '..'))
import widgets

from datasource.data import get_stock_signal_data
price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()

import matplotlib.ticker as mticker
class MyLocator(mticker.MaxNLocator):
    def __init__(self, *args, **kwargs):
        mticker.MaxNLocator.__init__(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return mticker.MaxNLocator.__call__(self, *args, **kwargs)

#plt.rc('axes', grid=True)
class TechMPlot(object):
    def __init__(self, fig, length, *args):
        self.name = "TechMPlot" 
        self.fig = fig
        self.indicators = { }
        self.cross_cursor = None
        self.v_cursor = None
        self.in_qt = False
        self.left, self.width = 0.1, 0.8
        self.init_slider()
        self.add_subplot(*args)
        for ax in self.axes:
            ax.format_coord = self.format_coord 
        self.connect()
        self.v_cursor = MultiCursor(self.fig.canvas, self.axes, color='r', lw=2, horizOn=True, vertOn=True)
        self.axes[0].set_xlim((len(price_data)-length, len(price_data)))

    def __iter__(self):
        # or yield
        return self.axes.__iter__()


    def add_indicator(self, ith_axes, indicator, if_twinx=False):
        """ 在ith_axes上画指标indicator。
        
        Args:
            ith_axes (Axes): 第i个窗口。
            indicator  (Indicator): 指标.
            if_twinx  (Bool): 是否是独立坐标。
        Returns:
            Indicator. 传进来的指标变量。
        """
        try:
            indicator.plot(self.axes[ith_axes])
            ax_indicators = self.indicators.get(ith_axes, [])
            if ax_indicators:
                ax_indicators.append(indicator) 
            else:
                self.indicators[ith_axes] = [indicator]
            return indicator
        except Exception as e:
            raise e


    def replace_indicator(self, ith_axes, indicator):
        """ 在ith_axes上画指标indicator, 删除其它指标。
        
        Args:
            ith_axes (Axes): 第i个窗口。
            indicator  (Indicator): 指标.
            if_twinx  (Bool): 是否是独立坐标。
        Returns:
            Indicator. 传进来的指标变量。
        """
        try:
            ## @todo remove paint
            self.indicators[ith_axes] = [indicator]
            indicator.plot(self.axes[ith_axes])
            return indicator
        except Exception as e:
            raise e


    def add_widget(self, ith_axes, widget, connect_slider=False):
        """ 添加一个能接收消息事件的控件。
        
        Args:
            ith_axes (Axes): 第i个窗口。
            widget (AxesWidget)
        
        Returns:
            AxesWidget. widget
        """
        try:
            widget.set_parent(self.axes[ith_axes])
            if connect_slider:
                self.slider.add_observer(widget)
            return widget
        except Exception, e:
            raise e


    def init_qt(self):
        """docstring for set_qt""" 
        self.in_qt = True
        self.v_cursor = MultiCursor(self.fig.canvas, self.axes, color='r', lw=2, horizOn=True, vertOn=True)


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


    def on_slider(self, val, event):
        """docstring for update""" 
        print self.name
        print event.name
        print val


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
        if event.inaxes is self.slider_ax: #or event.inaxes is self.range_ax:
            self.v_cursor = None
            event.canvas.draw()
            return 
        #self.cross_cursor = Cursor(event.inaxes, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        print("enter---")

    def leave_axes(self, event):
        if event.inaxes is self.slider_ax:
            self.v_cursor = MultiCursor(self.fig.canvas, self.axes, color='r', lw=2, horizOn=True, vertOn=True)
            event.canvas.draw()
        print("leave---")

    def init_slider(self):
        """docstring for init_slider""" 
        self.bottom = 0.05
        self.height = 0.1
        self.up = self.bottom + self.height
        self.slider_ax = self.fig.add_axes([self.left, self.bottom, self.width, self.height])
        self.range_ax = self.fig.add_axes([self.left, 0.6, self.width, 0.3],
                zorder = 0, frameon=False, sharex=self.slider_ax, visible=False)
        self.slider = widgets.Slider(self.slider_ax, "slider", '', 0, len(price_data),
                                    len(price_data), len(price_data)/50, "%d")
        self.rangew = widgets.RangeWidget('range', self.range_ax, price_data['close'])
        self.slider.add_observer(self)

    def add_subplot(self, *args):
        args = list(reversed(args))
        num_axes = sum(args)
        unit = (1.0 - self.up) / num_axes
        bottom = self.up
        for i, ratio in enumerate(args):
            rect = [self.left, bottom, self.width, unit * ratio]
            if i > 0:
                self.fig.add_axes(rect, sharex=self._user_axes()[0])  #axisbg=axescolor)
            else:
                self.fig.add_axes(rect)
            bottom += unit * ratio

        temp = self._user_axes()
        temp.reverse()
        self._axes = temp
        for ax in self._axes:
            ax.grid(True)
            ax.set_xticklabels([])


    def _user_axes(self):
        return self.fig.axes[2:]


    @property
    def axes(self):
        return self._axes


    def format_coord(self, x, y):
        """ 状态栏信息显示 """
        index = x
        f = x % 1
        index = x-f if f < 0.5 else x-f+1
        #print len(self.kwindow.rects.get_array())
        return "pos=%d o=%.2f c=%.2f h=%.2f l=%.2f" % (index,
                price_data['open'][index], price_data['close'][index], price_data['high'][index],
                price_data['low'][index])

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

