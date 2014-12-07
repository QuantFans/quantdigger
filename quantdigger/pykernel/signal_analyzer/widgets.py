"""
GUI Neutral widgets
===================

Widgets that are designed to work for any of the GUI backends.
All of these widgets require you to predefine an :class:`matplotlib.axes.Axes`
instance and pass that as the first arg.  matplotlib doesn't try to
be too smart with respect to layout -- you will have to figure out how
wide and tall you want your Axes to be to accommodate your widget.
"""


from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.widgets import AxesWidget
import numpy as np
from stock_plot import candlestick2


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

      *dragging*  : allow for mouse dragging on slider

    Call :meth:`on_changed` to connect to the slider event
    """
    def __init__(self, ax, name, label, valmin, valmax, valinit=0.5, width=1, valfmt='%1.2f', 
                 closedmin=True, closedmax=True, slidermin=None,
                 slidermax=None, dragging=True, **kwargs):
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
        self.poly = ax.axvspan(valmax-self.width,valmax, 0, 1, **kwargs)
        self.name = name
        #axhspan
        #self.vline = ax.axvline(valinit, 0, 1, color='r', lw=1)

        self.valfmt = valfmt
        ax.set_yticks([])
        ax.set_xlim((valmin, valmax))
        ax.set_xticks([])
        ax.set_navigate(False)

        self.connect_event('button_press_event', self._update)
        self.connect_event('button_release_event', self._update)
        if dragging:
            self.connect_event('motion_notify_event', self._update)
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

    def _update(self, event):
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

        elif ((event.name == 'button_release_event') or
              (event.name == 'button_press_event' and
               event.inaxes != self.ax)):
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            return
        self.update(event.xdata)


    def update(self, val, width=None):
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
        self.set_val(val)

    def set_val(self, val):
        xy = self.poly.xy
        xy[2] = val, 1
        xy[3] = val, 0
        self.val = val
        self.poly.remove()
        self.poly = self.ax.axvspan(val-self.width, val, 0, 1)
        #self.poly.xy = xy
        self.valtext.set_text(self.valfmt % val)
        self.val = val
        if not self.eventson:
            return
        self.update_observer("kwindow")

    def update_observer(self, obname):
        '''docstring for update_observer''' 
        for name, obj in self.observers.iteritems():
            if name == obname and obname == "kwindow":
                obj.update(self.val)
                break

    def on_changed(self, obj):
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

    def reset(self):
        """reset the slider to the initial value if needed"""
        if (self.val != self.valinit):
            self.set_val(self.valinit)


class CandleWindow(AxesWidget):
    """
    A slider representing a floating point range

    """
    def __init__(self, ax, name, data, wdlength, min_wdlength):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*

        """
        AxesWidget.__init__(self, ax)
        self.wdlength = wdlength
        self.min_wdlength = min_wdlength
        self.voffset = 0
        self.xmax = len(data)
        self.xmin = max(0, self.xmax-self.wdlength) 
        self.ymax = np.max(data.high[self.xmin : self.xmax].values) + self.voffset
        self.ymin = np.min(data.low[self.xmin : self.xmax].values) - self.voffset
        self.ax = ax
        self.cnt = 0
        self.observers = {}
        self.data = data
        self.name = name

        ax.set_xlim((self.xmin, self.xmax))
        ax.set_ylim((self.ymin, self.ymax))
        self.a1, self.a2 = candlestick2(ax, data.open.tolist()[:self.xmax], data.close.tolist()[:self.xmax], 
                                        data.high.tolist()[:self.xmax], data.low.tolist()[:self.xmax], 
                                        0.6, 'r', 'g', alpha=1)
        self.connect_event('key_release_event', self.keyrelease)
        #self.connect_event('button_release_event', self._update)

    def _update(self, event):
        """update the slider position"""
        self.update(event.xdata)

    def update(self, val):
        '''docstring for update(val)''' 
        val = int(val)
        self.xmax = val
        self.xmin = max(0, self.xmax-self.wdlength)
        self.ymax = np.max(self.data.high[val-self.wdlength : val].values) + self.voffset
        self.ymin = np.min(self.data.low[val-self.wdlength : val].values) - self.voffset
        self.ax.set_xlim((val-self.wdlength, val))
        self.ax.set_ylim((self.ymin, self.ymax))
        self.ax.autoscale_view()
        #self.ax.draw()
        #self.ax.draw_artist(self.a1)
        #self.ax.draw_artist(self.a2)
        self.ax.figure.canvas.draw()


    def on_changed(self, obj):
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

    def update_observer(self, obname):
        '''docstring for update_observer''' 
        for name, obj in self.observers.iteritems():
            if name == obname and obname == "slider":
                obj.update(obj.val, self.wdlength)
                break
             
    def keyrelease(self, event):
        '''docstring for keypress''' 
        #print event.__dict__
        print event.key
        #global observer_slider
        if event.key == "down":
            self.wdlength += self.wdlength/2 
            self.wdlength = len(self.data) if self.wdlength>len(self.data) else self.wdlength
            self.update(self.xmax)
            self.update_observer("slider")
        elif event.key == "up" :
            self.wdlength -= self.wdlength/2 
            self.wdlength = max(self.wdlength, self.min_wdlength)
            self.update(self.xmax)
            self.update_observer("slider")


from matplotlib.collections import LineCollection
class SignalWindow(object):
    """docstring for signalWindow"""
    def __init__(self,ax, s, c, lw=0.5):
        useAA = 0,  # use tuple here
        signal = LineCollection(s,
                                colors       = c, 
                                linewidths   = lw,
                                antialiaseds = useAA,
                                #zorder = 0,
                                 )
        ax.add_collection(signal)
    #ax.add_collection(barCollection)

