# -*- coding: utf8 -*-
from matplotlib.widgets import AxesWidget
import numpy as np



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
        print "8888" 
    


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
        """docstring for con""" 
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



from indicator import Candles
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
        self.main_indicator = None

    def set_parent(self, parent, ith_axes):
        """docstring for init_widget""" 
        self.ax = parent.axes[ith_axes]
        #ax.set_xlim((self.xmin, self.xmax))
        #ax.set_ylim((self.ymin, self.ymax))
        candles = Candles(self.data, self.name, 0.6, 'r', 'g', alpha=1)
        parent.register_indicator(ith_axes, candles)
        self.lines, self.rects = candles.plot(self.ax)
        self.main_indicator = candles
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
             


