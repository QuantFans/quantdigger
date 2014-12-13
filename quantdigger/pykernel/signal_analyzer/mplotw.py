# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.widgets import Cursor
from matplotlib.widgets import MultiCursor
import matplotlib.pyplot as plt

class MPlotW(object):
    """
    """
    def __init__(self, *args):
        self.fig = plt.figure()
        self.cross_cursor = None
        self.v_cursor = None

        self.add_subplot(*args)
        self.connect()
        for ax in self.axes:
            ax.format_coord = self.format_coord 

    def enter_axes(self, event):
        #event.inaxes.patch.set_facecolor('yellow')
        # 只有当前axes会闪烁。
        axes = [ax for ax in self.fig.axes if ax is not event.inaxes]
        self.v_cursor = MultiCursor(event.canvas, axes, color='r', lw=2, horizOn=False, vertOn=True)
        self.cross_cursor = Cursor(event.inaxes, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        event.canvas.draw()

    def leave_axes(self, event):
        del self.v_cursor
        del self.cross_cursor
        #event.inaxes.patch.set_facecolor('white')
        #event.canvas.draw()

    def connect(self):
        """
        连接信号事件。
        """ 
        self.fig.canvas.mpl_connect('axes_enter_event', self.enter_axes)
        self.fig.canvas.mpl_connect('axes_leave_event', self.leave_axes)

    def add_subplot(self, *args):
        num_axes = sum(args)
        for i, ratio in enumerate(args):
            if i > 0:
                plt.subplot2grid((num_axes, 1), (sum(args[:i]), 0),
                                 rowspan = ratio, sharex = self.fig.axes[0])
            else:
                plt.subplot2grid((num_axes, 1), (sum(args[:i]), 0), rowspan = ratio)

        #for ax in self.fig.axes:
            #ax.set_xticklabels([])

    def subplots_adjust(self, top, bottom, left, right, hspace, wspace):
        plt.subplots_adjust(top, bottom, left, right, hspace, wspace)

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




     
#fig = plt.figure(facecolor='white')
#fig.canvas.set_window_title(u'期货数据分析')

#def plot_entry(fig):
    #axescolor  = '#f6f6f6'  # the axes background color
    #left, width = 0.1, 0.8
    #rect1 = [left, 0.7, width, 0.2]#left, bottom, width, height
    #rect2 = [left, 0.3, width, 0.4]
    #rect3 = [left, 0.1, width, 0.2]

    #ax1 = fig.add_axes(rect1, axisbg=axescolor)
    #ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex = ax1, visible = False)
    #ax3 = fig.add_axes(rect3, axisbg=axescolor, sharex = ax1)
    #y = range(0, 10)

    #ax1.plot(y, y)
    #ax2.plot(y, y)
    #ax3.plot(y, y)
    #ax1.set_ylabel(u"交易区间内的差值")
    #ax2.set_ylabel(u"交易区间内的盈利")
    #for ax in ax1, ax2, ax3:
        ##if ax!=ax3:
        #ax.set_xticklabels([])

    #ax3.set_xlabel("")
    #ax1.set_title(u"入场相关信息")
    #c1 = Cursor(ax1, useblit=True, color='red', linewidth=1, vertOn = True, horizOn = True)
    #multi = MultiCursor(fig.canvas, [ax2, ax3], color='r', lw=1, horizOn=False, vertOn=True)

    ##handle = EventHandler(exit_profit, fig)
    ##fig.canvas.mpl_connect('motion_notify_event', handle.on_move)
    ##fig.canvas.mpl_connect('pick_event', handle.on_pick)

    #def format_coord(x, y):
        #""" 状态栏信息显示 """
        #i = int(x)/1
        ##c = pd.to_datetime(exit_profit.index[i]).strftime("%Y-%m-%d %H:%M:%S") + " Profit: %s MAE: %s"%(exit_profit[i], entry_worst[i])
        #return str(i)
    #ax1.format_coord = format_coord
    #ax2.format_coord = format_coord
    #ax3.format_coord = format_coord
    #return [ax1, ax2, ax3], [multi, c1]

#a = MPLotW(1, 2, 3)

#plt.show()
