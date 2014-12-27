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
        self.left, self.width = 0.1, 0.85
        self.init_slider()
        self.add_subplot(*args)
        self.w_left = len(price_data)-length
        self.w_right = len(price_data)
        self.w_length = length
        self.w_length_min = 50
        self.data = price_data
        for ax in self.axes:
            ax.format_coord = self.format_coord 
        self.connect()
        self.v_cursor = MultiCursor(self.fig.canvas, self.axes,
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)


    def __iter__(self):
        # or yield
        return self.axes.__iter__()


    def set_margin(self, left, right, bottom, top):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top


    def draw_window(self):
        """""" 
        self.axes[0].set_xlim((self.w_left, self.w_right))
        self._set_cur_ylim(self.w_left, self.w_right)
        self.fig.canvas.draw()


    def add_indicator(self, ith_axes, indicator, twinx=False):
        """ 在ith_axes上画指标indicator。
        
        Args:
            ith_axes (Axes): 第i个窗口。
            indicator  (Indicator): 指标.
            twinx  (Bool): 是否是独立坐标。
            ymain  (Bool): 是否作为y轴计算的唯一参考。
        Returns:
            Indicator. 传进来的指标变量。
        """
        try:
            indicator.plot(self.axes[ith_axes])
            return self.register_indicator(ith_axes, indicator)
        except Exception as e:
            raise e


    def register_indicator(self, ith_axes, indicator):
        """ 注册指标。
        axes到指标的映射。
        """ 
        try:
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


    def add_widget(self, ith_axes, widget, ymain=False, connect_slider=False):
        """ 添加一个能接收消息事件的控件。
        
        Args:
            ith_axes (Axes): 第i个窗口。
            widget (AxesWidget)
        
        Returns:
            AxesWidget. widget
        """
        try:
            widget.set_parent(self, ith_axes)
            if connect_slider:
                self._slider.add_observer(widget)
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
        self.fig.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.fig.canvas.mpl_connect('key_release_event', self.on_keyrelease)


    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidpress)


    def on_slider(self, val, event):
        """ 滑块事件处理。 """
        if event.name == "button_press_event":
            self._bigger_picture.set_zorder(1000)
            self._slider_cursor = MultiCursor(self.fig.canvas, [self._slider_ax, self._bigger_picture], color='r', lw=2, horizOn=False, vertOn=True)
        elif event.name == "button_release_event":
            self._bigger_picture.set_zorder(0)
            del self._slider_cursor
            event.canvas.draw()
        elif event.name == "motion_notify_event":
            pass
        # 遍历axes中的每个indicator，计算显示区间。
        self.w_right = int(val)
        self.w_left = max(0, self.w_right-self.w_length)
        self.axes[0].set_xlim(self.w_left, self.w_right)
        self.draw_window()


    def _set_cur_ylim(self, w_left, w_right):
        """ 设置当前显示窗口的y轴范围。
        
        Args:
            name (str): description
        
        Returns:
            int. The result
        Raises:
        """
        self.voffset = 0
        for i in range(0, len(self.axes)):
            all_ymax = []
            all_ymin = []
            for indicator in self.indicators[i]:
                ymax, ymin = indicator.y_interval(w_left, w_right)
                ## @todo move ymax, ymin 计算到indicator中去。
                all_ymax.append(ymax)
                all_ymin.append(ymin)
            ymax = max(all_ymax)
            ymin = min(all_ymin)
            ymax += self.voffset
            ymin -= self.voffset
            self.axes[i].set_ylim((ymin, ymax))
        #self.axes[i].autoscale_view()


    def on_press(self, event):
        pass


    def on_release(self, event):
        pass


    def on_motion(self, event):
        #self.fig.canvas.draw()
        pass


    def on_keyrelease(self, event):
        '''docstring for keypress''' 
        print event.key
        if event.key == "down":
            self.w_length += self.w_length/2 
            self.w_length = min(len(self.data), self.w_length)
        elif event.key == "up" :
            self.w_length -= self.w_length/2 
            self.w_length= max(self.w_length, self.w_length_min)

        middle = (self.w_left+self.w_right)/2
        self.w_left =  middle - self.w_length/2
        self.w_right = middle + self.w_length/2
        self.w_left = max(0, self.w_left)
        self.w_right = min(len(self.data), self.w_right)
        self.draw_window()


    def on_enter_axes(self, event):
        #event.inaxes.patch.set_facecolor('yellow')
        # 只有当前axes会闪烁。
        if event.inaxes is self._slider_ax: #or event.inaxes is self._bigger_picture:
            del self.v_cursor
            event.canvas.draw()
            return 
        #self.cross_cursor = Cursor(event.inaxes, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)


    def on_leave_axes(self, event):
        if event.inaxes is self._slider_ax:
            self.v_cursor = MultiCursor(self.fig.canvas, self.axes, color='r', lw=2, horizOn=True, vertOn=True)
            event.canvas.draw()


    def init_slider(self):
        self.bottom = 0.05
        self._slider_height = 0.1
        self._bigger_picture_height = 0.3
        self.up = self.bottom + self._slider_height
        #
        self._slider_ax = self.fig.add_axes([self.left, self.bottom, self.width, self._slider_height], axisbg='gray')
        self._bigger_picture = self.fig.add_axes([self.left, self.bottom+self._slider_height, 
                                                    self.width, self._bigger_picture_height],
                                                zorder = 0, frameon=True,
                                                sharex=self._slider_ax,
                                                axisbg='gray', alpha = '0.1' )
        #
        self._slider = widgets.Slider(self._slider_ax, "slider", '', 0, len(price_data),
                                    len(price_data), len(price_data)/50, "%d")
        self._bigger_picture.plot(price_data['close'])
        self._bigger_picture.set_yticks([])
        #self.rangew = widgets.RangeWidget('range', self._bigger_picture, price_data['close'])
        self._slider.add_observer(self)


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
        return "[pos=%d o=%.2f c=%.2f h=%.2f l=%.2f]" % (index,
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

