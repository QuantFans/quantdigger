# -*- coding: utf-8 -*-
import sys
import six
from six.moves import range
from matplotlib.widgets import AxesWidget
from matplotlib.widgets import MultiCursor
from matplotlib.ticker import Formatter
import matplotlib.ticker as mticker
import numpy as np

from quantdigger.util.log import gen_log as log


def slider_strtime_format(delta):
    """ 根据时间间隔判断周期及slider上相应的显示形式 """
    if delta.days >= 1:
        return '%Y-%m'
    elif delta.seconds == 60:
        return '%H:%M'
    else:
        # 日内其它分钟
        return '%H:%M'


class Slider(AxesWidget):
    """
    A slider representing a floating point range

    The following attributes are defined
      *ax*        : the slider :class:`matplotlib.axes.Axes` instance

      *val*       : the current slider value

      *vline*     : a :class:`matplotlib.lines.Line2D` instance
                     representing the initial value of the slider

      *poly*      : A :class:`matplotlib.patches.Polygon` instance
                     which is the slider knob

      *valfmt*    : the format string for formatting the slider text

      *label*     : a :class:`matplotlib.text.Text` instance
                     for the slider label

      *closedmin* : whether the slider is closed on the minimum

      *closedmax* : whether the slider is closed on the maximum

      *slidermin* : another slider - if not *None*, this slider must be
                     greater than *slidermin*

      *slidermax* : another slider - if not *None*, this slider must be
                     less than *slidermax*

      *drag_enabled*  : allow for mouse dragging on slider

    Call :meth:`add_observer` to connect to the slider event
    """

    def __init__(self, ax, name, label, valmin, valmax, valinit=0.5, width=1, valfmt='%1.2f',
                 time_index = None, closedmin=True, closedmax=True, slidermin=None,
                 slidermax=None, drag_enabled=True, **kwargs):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*

        *valinit*
            The slider initial position

        *label*
            The slider label

        *valfmt*
            Used to format the slider value

        *closedmin* and *closedmax*
            Indicate whether the slider interval is closed

        *slidermin* and *slidermax*
            Used to constrain the value of this slider to the values
            of other sliders.

        additional kwargs are passed on to ``self.poly`` which is the
        :class:`matplotlib.patches.Rectangle` which draws the slider
        knob.  See the :class:`matplotlib.patches.Rectangle` documentation
        valid property names (e.g., *facecolor*, *edgecolor*, *alpha*, ...)
        """
        AxesWidget.__init__(self, ax)
        self.label = ax.text(-0.02, 0.5, label, transform=ax.transAxes,
                             verticalalignment='center',
                             horizontalalignment='right')
        self.valtext = None
        self.poly = None
        self.reinit(valmin, valmax, valinit, width, valfmt, time_index, **kwargs)

        self.name = name
        self.cnt = 0
        self.closedmin = closedmin
        self.closedmax = closedmax
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.drag_active = False
        self.drag_enabled = drag_enabled
        self.observers = {}
        ax.set_yticks([])

        #ax.set_xticks([]) # disable ticks
        ax.set_navigate(False)
        self._connect()

    def _xticks_to_display(self, valmax):
        interval = valmax / 5
        v = 0
        xticks = []
        for i in range(0, 6):
            xticks.append(v)
            v += interval
        return xticks


    def _value_format(self, x):
        """docstring for timess"""
        ind = int(round(x))
        if ind>=len(self._index) or ind<0: return ''
        return self._index[ind].strftime(self._fmt)

        self._slider = Slider(0, self._data_length-1,
                                    self._data_length-1, self._data_length/50, "%d",
                                    self._data.index)

    def reinit(self, valmin, valmax, valinit=0.5, width=1, valfmt='%1.2f',
            time_index = None, **kwargs):
        """ [valmin, valmax] """
        self.ax.set_xticks(self._xticks_to_display(valmax))
        self._index = time_index
        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.valinit = valinit
        self.width = width
        self.valfmt = valfmt
        self._fmt = slider_strtime_format(time_index[1] - time_index[0])
        self.ax.set_xlim((valmin, valmax))
        self._data_length = valmax

        if self.valtext:
            self.valtext.remove()
        if self.poly:
            self.poly.remove()
        # 滑动条的形状
        self.poly = self.ax.axvspan(valmax-self.width/2,valmax+self.width/2, 0, 1, **kwargs)
        #axhspan
        #self.vline = ax.axvline(valinit, 0, 1, color='r', lw=1)

        #self.valtext = ax.text(1.02, 0.5, valfmt % valinit,
        self.valtext = self.ax.text(1.005, 0.5,self._value_format(valinit),
                               transform=self.ax.transAxes,
                               verticalalignment='center',
                               horizontalalignment='left')

    def add_observer(self, obj):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        self.observers[obj.name] = obj

    def remove_observer(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def reset(self):
        """reset the slider to the initial value if needed"""
        if (self.val != self.valinit):
            self._set_val(self.valinit)

    def _connect(self):
        # 信号连接。
        self.connect_event('button_press_event', self.on_event)
        self.connect_event('button_release_event', self.on_event)
        if self.drag_enabled:
            self.connect_event('motion_notify_event', self.on_event)

    def on_event(self, event):
        """update the slider position"""
        if self.ignore(event):
            return
        if event.button != 1:
            return
        if event.name == 'button_press_event' and event.inaxes == self.ax:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)
        if not self.drag_active:
            return
        elif event.name == 'button_press_event' and event.inaxes != self.ax:
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            return
        elif event.name == 'button_release_event' and event.inaxes == self.ax:
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            self._update_observer(event)
            return
        self._update(event.xdata)
        self._update_observer(event)
        # 重绘

    def _update(self, val, width=None):
        if val <= self.valmin:
            if not self.closedmin:
                return
            val = self.valmin
        elif val >= self.valmax:
            if not self.closedmax:
                return
            val = self.valmax

        if self.slidermin is not None and val <= self.slidermin.val:
            if not self.closedmin:
                return
            val = self.slidermin.val

        if self.slidermax is not None and val >= self.slidermax.val:
            if not self.closedmax:
                return
            val = self.slidermax.val
        if width:
            self.width = width
        self._set_val(val)


    def _set_val(self, val):
        xy = self.poly.xy
        xy[2] = val, 1
        xy[3] = val, 0
        self.val = val
        self.poly.remove()
        self.poly = self.ax.axvspan(val-self.width/2, val+self.width/2, 0, 1)
        #self.poly.xy = xy
        #self.valtext.set_text(self.valfmt % val)
        self.valtext.set_text(self._value_format(val))
        self.val = val
        if not self.eventson:
            return

    def _update_observer(self, event):
        """ 通知相关窗口更新数据 """
        for name, obj in six.iteritems(self.observers):
            try:
                obj.on_slider(self.val, event)
            except Exception as e:
                six.print_(e)


class FrameWidget(AxesWidget):
    """
    蜡烛线控件。

    """
    def __init__(self, ax, name, wdlength, min_wdlength):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*

        """
        AxesWidget.__init__(self, ax)
        self.name = name
        self.wdlength = wdlength
        self.min_wdlength = min_wdlength
        self.voffset = 0
        self.connect()
        self.plotters = { }

        # 当前显示的范围。
        #self.xmax = len(data)
        #self.xmin = max(0, self.xmax-self.wdlength)
        #self.ymax = np.max(data.high[self.xmin : self.xmax].values) + self.voffset
        #self.ymin = np.min(data.low[self.xmin : self.xmax].values) - self.voffset

        self.cnt = 0
        self.observers = {}

    def add_plotter(self, plotter, twinx):
        """ 添加并绘制, 不允许重名的plotter """
        if plotter.name in self.plotters:
            raise
        if not self.plotters:
            twinx = False
        if twinx:
            twaxes = self.ax.twinx()
            plotter.plot(twaxes)
            plotter.ax = twaxes
            plotter.twinx = True
        else:
            plotter.plot(self.ax)
            plotter.ax = self.ax
            plotter.twinx = False
        self.plotters[plotter.name] = plotter

    def plot_with_plotter(self, plotter_name, *args):
        self.plotters[plotter_name].plot(self.ax, *args)

    def set_ylim(self, w_left, w_right):
        all_ymax = []
        all_ymin = []
        for plotter in six.itervalues(self.plotters):
            if plotter.twinx:
                continue
            ymax, ymin = plotter.y_interval(w_left, w_right)
            ## @todo move ymax, ymin 计算到plot中去。
            all_ymax.append(ymax)
            all_ymin.append(ymin)
        ymax = max(all_ymax)
        ymin = min(all_ymin)
        self._voffset = (ymax-ymin) / 10.0 # 画图显示的y轴留白。
        ymax += self._voffset
        ymin -= self._voffset
        self.ax.set_ylim((ymin, ymax))

    def on_slider(self, val, event):
        #'''docstring for update(val)'''
        ## @TODO _set_ylim 分解到这里
        pass
        #val = int(val)
        #self.xmax = val
        #self.xmin = max(0, self.xmax-self.wdlength)
        #self.ymax = np.max(self.data.high[val-self.wdlength : val].values) + self.voffset
        #self.ymin = np.min(self.data.low[val-self.wdlength : val].values) - self.voffset
        #self.ax.set_xlim((val-self.wdlength, val))
        #self.ax.set_ylim((self.ymin, self.ymax))

    def connect(self):
        #self.ax.figure.canvas.mpl_connect('key_release_event', self.enter_axes)
        pass

    def _update(self, event):
        """update the slider position"""
        self.update(event.xdata)

    def add_observer(self, obj):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        self.observers[obj.name] = obj

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def _update_observer(self, obname):
        #"通知进度条改变宽度"
        #for name, obj in six.iteritems(self.observers):
            #if name == obname and obname == "slider":
                #obj.update(obj.val, self.wdlength)
                #break
        pass


class MyLocator(mticker.MaxNLocator):
    def __init__(self, *args, **kwargs):
        mticker.MaxNLocator.__init__(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return mticker.MaxNLocator.__call__(self, *args, **kwargs)


class TechnicalWidget(object):
    """ 多窗口控件 """
    def __init__(self, fig, data, left=0.1, bottom=0.05, width=0.85, height=0.9,
            parent=None):
        """ 多窗口联动控件。

        Args:
            fig (Figure): matplotlib绘图容器。
            data (DataFrame): [open, close, high, low]数据表。
        """
        self.name = "MultiWidgets"
        self._fig = fig
        self._subwidgets = { }
        self._cursor = None
        self._cursor_axes_index = { }
        self._hoffset = 1

        self._left, self._width = left, width
        self._bottom, self._height  = bottom, height
        self._slider_height = 0.1
        self._bigger_picture_height = 0.3    # 鸟瞰图高度
        self._all_axes = []
        self.load_data(data)
        self._cursor_axes = { }

    def init_layout(self, w_width, *args):
        # 布局参数
        self._w_width_min = 50
        self._w_width = w_width
        self._init_widgets(*args)
        self._connect()
        self._cursor = MultiCursor(self._fig.canvas, self.axes,
                                    color='r', lw=2, horizOn=False,
                                    vertOn=True)
        return self.axes

    def load_data(self, data):
        self._data = data
        self._data_length = len(self._data)

    @property
    def axes(self):
        return self._axes

    def plot_text(self, name, ith_ax, x, y, text, color='black', size=10, rotation=0):
        self.axes[ith_ax].text(x, y, text, color=color, fontsize=size, rotation=rotation)

    def draw_widgets(self):
        """ 显示控件 """
        self._w_left = self._data_length - self._w_width
        self._w_right = self._data_length
        self._reset_auxiliary_widgets()
        self._update_widgets()

    def _reset_auxiliary_widgets(self):
        if self._slider is None:
            self._slider = Slider(self._slider_ax, "slider", '', 0, self._data_length-1,
                                        self._data_length-1, self._data_length/50, "%d",
                                        self._data.index)
            self._slider.add_observer(self)
        else:
            self._slider.reinit( 0, self._data_length-1, self._data_length-1,
                    self._data_length/50, "%d", self._data.index)
        if self._bigger_picture_plot:
            self._bigger_picture_plot.pop(0).remove()
        self._bigger_picture_plot = self._bigger_picture.plot(self._data['close'].values,
                                                               'b')
        self._bigger_picture.set_ylim((min(self._data['low']), max(self._data['high'])))
        self._bigger_picture.set_xlim((0, len(self._data['close'])))
        self._slider_ax.xaxis.set_major_formatter(TimeFormatter(self._data.index,
                                                                fmt='%Y-%m-%d'))

    def add_widget(self, ith_subwidget, widget, ymain=False, connect_slider=False):
        """ 添加一个能接收消息事件的控件。

        Args:
            ith_subwidget (int.): 子窗口序号。
            widget (AxesWidget): 控件。

        Returns:
            AxesWidget. widget
        """
        # 对新创建的Axes做相应的处理
        # 并且调整Cursor
        for plotter in six.itervalues(widget.plotters):
            if plotter.twinx:
                plotter.ax.format_coord = self._format_coord
                self.axes.append(plotter.ax)
                #self._cursor_axes[ith_subwidget] = plotter.ax
                self._cursor = MultiCursor(self._fig.canvas,
                        list(self._cursor_axes.values()),
                                            color='r', lw=2, horizOn=False,
                                            vertOn=True)
        self._subwidgets[ith_subwidget] = widget
        if connect_slider:
            self._slider.add_observer(widget)
        return widget

    def on_slider(self, val, event):
        """ 滑块事件处理。 """
        if event.name == "button_press_event":
            self._bigger_picture.set_zorder(1000)
            self._slider_cursor = MultiCursor(self._fig.canvas,
                                    [self._slider_ax, self._bigger_picture], color='y',
                                    lw=2, horizOn=False, vertOn=True)
            log.debug("on_press_event")
        elif event.name == "button_release_event":
            self._bigger_picture.set_zorder(0)
            del self._slider_cursor
            log.debug("on_release_event")
        elif event.name == "motion_notify_event":
            pass
        # 遍历axes中的每个indicator，计算显示区间。
        self._w_left = int(val)
        self._w_right = self._w_left+self._w_width
        if self._w_right >= self._data_length:
            self._w_right = self._data_length - 1 + self._hoffset
            self._w_left = self._w_right - self._w_width
        self._update_widgets()

    def on_press(self, event):
        log.debug("button_press_event")
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        #self._fig.canvas.draw()
        pass

    def _clear(self):
        """"""
        return

    def on_keyrelease(self, event):
        if event.key == u"down":
            self._w_width += self._w_width/2
            self._w_width = min(self._data_length, self._w_width)
        elif event.key == u"up" :
            self._w_width -= self._w_width/2
            self._w_width= max(self._w_width, self._w_width_min)
        elif event.key == u"super+up":
            six.print_(event.key, "**", type(event.key) )
        elif event.key == u"super+down":
            six.print_(event.key, "**", type(event.key) )
            # @TODO page upper down

        middle = (self._w_left+self._w_right)/2
        self._w_left =  middle - self._w_width/2
        self._w_right = middle + self._w_width/2
        self._w_left = max(0, self._w_left)
        self._w_right = min(self._data_length, self._w_right)
        self._update_widgets()

    def on_enter_axes(self, event):
        #event.inaxes.patch.set_facecolor('yellow')
        # 只有当前axes会闪烁。
        if event.inaxes is self._slider_ax: #or event.inaxes is self._bigger_picture:
            self._cursor = None
            event.canvas.draw()
            log.debug("on_enter_axes")
            return

    def on_leave_axes(self, event):
        if event.inaxes is self._slider_ax:
            # 进入后会创建_slider_cursor,离开后复原
            axes = [self.axes[i] for i in six.itervalues(self._cursor_axes_index)]
            #axes = list(reversed(axes)) # 很奇怪，如果没有按顺序给出，显示会有问题。
            self._cursor = MultiCursor(self._fig.canvas, axes, color='r', lw=2, horizOn=False, vertOn=True)
            event.canvas.draw()
            log.debug("on_leave_axes")

    def _connect(self):
        """
        matplotlib信号连接。
        """
        self.cidpress = self._fig.canvas.mpl_connect( "button_press_event", self.on_press)
        self.cidrelease = self._fig.canvas.mpl_connect( "button_release_event", self.on_release)
        self.cidmotion = self._fig.canvas.mpl_connect( "motion_notify_event", self.on_motion)
        self._fig.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self._fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self._fig.canvas.mpl_connect('key_release_event', self.on_keyrelease)

    #def _disconnect(self):
        #self._fig.canvas.mpl_disconnect(self.cidmotion)
        #self._fig.canvas.mpl_disconnect(self.cidrelease)
        #self._fig.canvas.mpl_disconnect(self.cidpress)

    def _init_widgets(self, *args):

        self._slidder_lower = self._bottom
        self._slidder_upper = self._bottom + self._slider_height
        self._bigger_picture_lower = self._slidder_upper
        self._slider_ax = self._fig.add_axes([self._left, self._slidder_lower, self._width,
                                             self._slider_height])
        self._bigger_picture = self._fig.add_axes([self._left, self._bigger_picture_lower,
                                                    self._width, self._bigger_picture_height],
                                                zorder = 0, frameon=False,
                                                #sharex=self._slider_ax,
                                                alpha = '0.1' )
        self._bigger_picture.set_xticklabels([]);
        self._bigger_picture.set_xticks([])
        self._bigger_picture.set_yticks([])
        self._all_axes = [self._slider_ax, self._bigger_picture]
        self._slider = None
        self._bigger_picture_plot = None

        args = list(reversed(args))
        # 默认子窗口数量为1
        if len(args) ==  0:
            args = (1,)
        total_units = sum(args)
        unit = (self._bottom + self._height - self._slidder_upper) / total_units
        bottom = self._slidder_upper
        user_axes = []
        first_user_axes = None
        for i, ratio in enumerate(args):
            rect = [self._left, bottom, self._width, unit * ratio]
            if i > 0:
                # 共享x轴
                ax = self._fig.add_axes(rect, sharex=first_user_axes)  #facecolor=axescolor)
                self._all_axes.append(ax)
            else:
                first_user_axes = self._fig.add_axes(rect)
                self._all_axes.append(first_user_axes)
            user_axes = self._all_axes[2:]
            bottom += unit * ratio
        self._axes = list(reversed(user_axes))
        map(lambda x: x.grid(True), self._axes)
        map(lambda x: x.set_xticklabels([]), self._axes[1:])
        for ax in self.axes:
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            # ax.get_yaxis().get_major_formatter().set_scientific(False)
        for i, ax in enumerate(self.axes):
            ax.format_coord = self._format_coord
            self._cursor_axes[i] = ax
        delta = (self._data.index[1] - self._data.index[0])
        self.axes[0].xaxis.set_major_formatter(TimeFormatter(self._data.index, delta))
        self.axes[0].set_xticks(self._xticks_to_display(0, self._data_length, delta));
        for ax in self.axes[0:-1]:
            [label.set_visible(False) for label in ax.get_xticklabels()]
        for i in range(0, len(self.axes)):
            self._cursor_axes_index[i] = i


    def _update_widgets(self):
        """ 改变可视区域， 在坐标移动后被调用。"""
        self.axes[0].set_xlim((int(self._w_left), int(self._w_right)))
        self._set_ylim(int(self._w_left), int(self._w_right))
        self._fig.canvas.draw()

    def _set_ylim(self, w_left, w_right):
        """ 设置当前显示窗口的y轴范围。
        """
        for subwidget in six.itervalues(self._subwidgets):
            subwidget.set_ylim(w_left, w_right)

    def _format_coord(self, x, y):
        """ 状态栏信息显示 """
        index = x
        f = x % 1
        index = x-f if f < 0.5 else min(x-f+1, len(self._data['open']) - 1)
        delta = (self._data.index[1] - self._data.index[0])
        fmt = slider_strtime_format(delta)
        index = int(index)
        ## @note 字符串太长会引起闪烁
        return "[dt=%s o=%.2f c=%.2f h=%.2f l=%.2f]" % (
                self._data.index[index].strftime(fmt),
                self._data['open'][index],
                self._data['close'][index],
                self._data['high'][index],
                self._data['low'][index])

    def _xticks_to_display(self, start, end, delta):
        xticks = []
        for i in range(start, end):
            if i >= 1:
                if delta.days >= 1:
                    if self._data.index[i].month != self._data.index[i-1].month:
                        xticks.append(i)
                elif delta.seconds == 60:
                    # 一分钟的以小时为显示单位
                    if self._data.index[i].hour != self._data.index[i-1].hour and \
                       self._data.index[i].day == self._data.index[i-1].day:
                        xticks.append(i)
                else:
                    if self._data.index[i].day != self._data.index[i-1].day:
                        # 其它日内以天为显示单位
                        xticks.append(i)
            else:
                xticks.append(0)
        return xticks


class TimeFormatter(Formatter):
    # 分类 －－format
    def __init__(self, dates, delta=None, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = self._strtime_format(delta) if delta else fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''
        return self.dates[ind].strftime(self.fmt)

    def _strtime_format(self, delta):
        if delta.days >= 1:
            return '%Y-%m'
        elif delta.seconds == 60:
            return '%m-%d %H:%M'
        else:
            # 日内其它分钟
            return '%m-%d'
