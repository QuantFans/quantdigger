# -*- coding: utf8 -*-
from matplotlib.widgets import AxesWidget
from matplotlib.widgets import MultiCursor
import matplotlib.ticker as mticker
from  mplots import Candles


class RangeWidget(object):
    """"""
    def __init__(self, name, ax, data):
        self.name = name
        self.ax = ax
        self.ax.plot(data)

    def update(self):
        """""" 
        #self.zorder = 1000
        #self.ax.visible = True
        #self.ax.figure.canvas.draw()
        pass


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
                 closedmin=True, closedmax=True, slidermin=None,
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

        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.valinit = valinit
        self.ax = ax
        self.width = width
        # 滑动条
        self.poly = ax.axvspan(valmax-self.width/2,valmax+self.width/2, 0, 1, **kwargs)
        self.name = name
        #axhspan
        #self.vline = ax.axvline(valinit, 0, 1, color='r', lw=1)

        self.valfmt = valfmt
        ax.set_yticks([])
        ax.set_xlim((valmin, valmax))
        #ax.set_xticks([]) # disable ticks
        ax.set_navigate(False)

        self.label = ax.text(-0.02, 0.5, label, transform=ax.transAxes,
                             verticalalignment='center',
                             horizontalalignment='right')

        self.valtext = ax.text(1.02, 0.5, valfmt % valinit,
                               transform=ax.transAxes,
                               verticalalignment='center',
                               horizontalalignment='left')

        self.cnt = 0
        self.observers = {}
        self.closedmin = closedmin
        self.closedmax = closedmax
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.drag_active = False
        self.drag_enabled = drag_enabled
        self._connect()


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
        self.connect_event('button_press_event', self.on_mouse)
        self.connect_event('button_release_event', self.on_mouse)
        if self.drag_enabled:
            self.connect_event('motion_notify_event', self.on_mouse)


    def on_mouse(self, event):
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
        self.valtext.set_text(self.valfmt % val)
        self.val = val
        if not self.eventson:
            return


    def _update_observer(self, event):
        """ 通知相关窗口更新数据 """
        for name, obj in self.observers.iteritems():
            try:
                obj.on_slider(self.val, event)
            except Exception, e:
                print(e)


class CandleWindow(object):
    """
    画蜡烛线。

    """
    def __init__(self, name, data, wdlength, min_wdlength):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*

        """
        #AxesWidget.__init__(self, ax)
        self.name = name
        self.wdlength = wdlength
        self.min_wdlength = min_wdlength
        self.voffset = 0

        # 当前显示的范围。 
        #self.xmax = len(data)
        #self.xmin = max(0, self.xmax-self.wdlength) 
        #self.ymax = np.max(data.high[self.xmin : self.xmax].values) + self.voffset
        #self.ymin = np.min(data.low[self.xmin : self.xmax].values) - self.voffset

        self.cnt = 0
        self.observers = {}
        self.data = data
        self.main_plot = None

    def set_parent(self, parent, ith_axes):
        """docstring for init_widget""" 
        self.ax = parent.axes[ith_axes]
        #ax.set_xlim((self.xmin, self.xmax))
        #ax.set_ylim((self.ymin, self.ymax))
        candles = Candles(None, self.data, self.name)
        parent.register_plot(ith_axes, candles)
        self.lines, self.rects = candles.plot(self.ax)
        self.main_plot = candles
        self.connect()


    def on_slider(self, val, event):
        #'''docstring for update(val)''' 
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
        #for name, obj in self.observers.iteritems():
            #if name == obname and obname == "slider":
                #obj.update(obj.val, self.wdlength)
                #break
        pass


class MyLocator(mticker.MaxNLocator):
    def __init__(self, *args, **kwargs):
        mticker.MaxNLocator.__init__(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return mticker.MaxNLocator.__call__(self, *args, **kwargs)

#plt.rc('axes', grid=True)
class MultiWidgets(object):
    def __init__(self, fig, data, w_width, *args):
        """ 一个多窗口联动控件。

        Args:

            fig (Figure): matplotlib绘图容器。

            data (DataFrame): [open, close, high, low]数据表。

            w_width (int): 窗口的初始宽度。

            *args (tuple): 窗口布局。
        
        """
        self.name = "MultiWidgets" 
        self._fig = fig
        self._subwidget2plots = { } # 窗口坐标到指标的映射。
        self._cursor = None
        self.in_qt = False
        self._data = data

        self._left, self._width = 0.1, 0.85
        self._data_length = len(self._data)
        self._w_left = self._data_length - w_width
        self._w_right = self._data_length
        self._w_width = w_width
        self._w_width_min = 50
        self._bottom = 0.05
        self._slider_height = 0.1
        self._bigger_picture_height = 0.3
        self._top = self._bottom + self._slider_height

        self._init_slider()
        self._init_widgets(*args)
        for ax in self.axes:
            ax.format_coord = self._format_coord 
        self._connect()
        self._cursor = MultiCursor(self._fig.canvas, self.axes,
                                    color='r', lw=2, horizOn=True,
                                    vertOn=True)
    @property
    def axes(self):
        return self._axes

    def set_margin(self, left, right, bottom, top):
        """ 设置边框。 """
        self._left = left
        self.right = right
        self._bottom = bottom
        self.top = top

    def draw_widgets(self):
        """ 显示控件 """ 
        self._update_widgets()

    def add_indicator(self, ith_axes, indicator, twinx=False):
        """ 在第ith_axes个子窗口上画指标。
        
        Args:

            ith_axes (Axes): 第ith_axes个窗口。

            indicator  (Indicator): 指标.

            twinx  (Bool): 是否是独立坐标。

            ymain  (Bool): 是否作为y轴计算的唯一参考。

        Returns:

            Indicator. 传进来的指标变量。
        """
        self.add_plot(ith_axes, indicator, twinx)

    def add_plot(self, ith_axes, plot, twinx=False):
        try:
            plot.plot(self.axes[ith_axes])
            return self.register_plot(ith_axes,plot)
        except Exception as e:
            raise e

    def register_plot(self, ith_axes, plot):
        """ 注册指标。
            axes到指标的映射。
        """ 
        try:
            ax_plots = self._subwidget2plots.get(ith_axes, [])
            if ax_plots:
                ax_plots.append(plot) 
            else:
                self._subwidget2plots[ith_axes] = [plot]
            return plot
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
            self._subwidget2plots[ith_axes] = [indicator]
            indicator.plot(self.axes[ith_axes])
            return indicator
        except Exception as e:
            raise e

    def add_widget(self, ith_axes, widget, ymain=False, connect_slider=False):
        """ 添加一个能接收消息事件的控件。
        
        Args:

            ith_axes (Axes): 第i个窗口。

            widget (AxesWidget): 控件。
        
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

    def on_slider(self, val, event):
        """ 滑块事件处理。 """
        if event.name == "button_press_event":
            self._bigger_picture.set_zorder(1000)
            self._slider_cursor = MultiCursor(self._fig.canvas, [self._slider_ax, self._bigger_picture], color='r', lw=2, horizOn=False, vertOn=True)
        elif event.name == "button_release_event":
            self._bigger_picture.set_zorder(0)
            del self._slider_cursor
            event.canvas.draw()
        elif event.name == "motion_notify_event":
            pass
        # 遍历axes中的每个indicator，计算显示区间。
        self._w_right = int(val)
        self._w_left = max(0, self._w_right-self._w_width)
        self.axes[0].set_xlim(self._w_left, self._w_right)
        self._update_widgets()

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        #self._fig.canvas.draw()
        pass

    def on_keyrelease(self, event):
        if event.key == "down":
            self._w_width += self._w_width/2 
            self._w_width = min(self._data_length, self._w_width)
        elif event.key == "up" :
            self._w_width -= self._w_width/2 
            self._w_width= max(self._w_width, self._w_width_min)

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
            return 
        #self.cross_cursor = Cursor(event.inaxes, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)

    def on_leave_axes(self, event):
        if event.inaxes is self._slider_ax:
            self._cursor = MultiCursor(self._fig.canvas, self.axes, color='r', lw=2, horizOn=True, vertOn=True)
            event.canvas.draw()

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

    def _disconnect(self):
        self._fig.canvas.mpl_disconnect(self.cidmotion)
        self._fig.canvas.mpl_disconnect(self.cidrelease)
        self._fig.canvas.mpl_disconnect(self.cidpress)

    def _init_slider(self):
        #
        self._slider_ax = self._fig.add_axes([self._left, self._bottom, self._width, self._slider_height], axisbg='gray')
        self._bigger_picture = self._fig.add_axes([self._left, self._bottom+self._slider_height, 
                                                    self._width, self._bigger_picture_height],
                                                zorder = 0, frameon=False,
                                                sharex=self._slider_ax,
                                                axisbg='gray', alpha = '0.1' )
        #
        self._slider = Slider(self._slider_ax, "slider", '', 0, self._data_length,
                                    self._data_length, self._data_length/50, "%d")
        self._bigger_picture.plot(self._data['close'])
        self._bigger_picture.set_yticks([])
        #self.rangew = RangeWidget('range', self._bigger_picture, self._data['close'])
        self._slider.add_observer(self)

    def _init_widgets(self, *args):
        args = list(reversed(args))
        # 默认子窗口数量为1
        if len(args) ==  0:
            args = (1,) 
        total_units = sum(args)
        unit = (1.0 - self._top) / total_units
        bottom = self._top
        for i, ratio in enumerate(args):
            rect = [self._left, bottom, self._width, unit * ratio]
            if i > 0:
                self._fig.add_axes(rect, sharex=self._user_axes()[0])  #axisbg=axescolor)
            else:
                self._fig.add_axes(rect)
            bottom += unit * ratio

        temp = self._user_axes()
        temp.reverse()
        self._axes = temp
        for ax in self._axes:
            ax.grid(True)
            ax.set_xticklabels([])

    def _user_axes(self):
        return self._fig.axes[2:]

    def _format_coord(self, x, y):
        """ 状态栏信息显示 """
        index = x
        f = x % 1
        index = x-f if f < 0.5 else min(x-f+1, len(self._data['open']) - 1)
        #print len(self.kwindow.rects.get_array())
        return "[pos=%d o=%.2f c=%.2f h=%.2f l=%.2f]" % (index,
                self._data['open'][index], self._data['close'][index], self._data['high'][index],
                self._data['low'][index])

    def __iter__(self):
        """ 返回子窗口。 """
        return self.axes.__iter__()

    def _update_widgets(self):
        """ 改变可视区域， 在坐标移动后被调用。""" 
        self.axes[0].set_xlim((self._w_left, self._w_right))
        self._set_cur_ylim(self._w_left, self._w_right)
        self._fig.canvas.draw()

    def _set_cur_ylim(self, w_left, w_right):
        """ 设置当前显示窗口的y轴范围。
        
        Args:

            name (str): description
        
        Returns:

            int. The result
        """
        self.voffset = 0
        for i in range(0, len(self.axes)):
            all_ymax = []
            all_ymin = []
            for plot in self._subwidget2plots[i]:
                ymax, ymin = plot.y_interval(w_left, w_right)
                ## @todo move ymax, ymin 计算到plot中去。
                all_ymax.append(ymax)
                all_ymin.append(ymin)
            ymax = max(all_ymax)
            ymin = min(all_ymin)
            ymax += self.voffset
            ymin -= self.voffset
            self.axes[i].set_ylim((ymin, ymax))
        #self.axes[i].autoscale_view()
