# -*- coding: utf-8 -*-
##
# @file stock_plot.py
# @brief 一些绘制统计信息的函数。
# @author wondreamer
# @version 2.0
# @date 2015-10-19

import six
from six.moves import range
import matplotlib
matplotlib.use("TKAgg")
from matplotlib.widgets import Cursor
from matplotlib.widgets import MultiCursor
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np
import operator
import pandas as pd
#from pylab import *
#mpl.rcParams['font.sans-serif'] =  ['Microsoft YaHei'] #指定默认字体


def accumulate(iterable, func=operator.add):
    'Return running totals'
    # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
    # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
    it = iter(iterable)
    total = next(it)
    # rst = []
    yield total
    for element in it:
        total = func(total, element)
        yield total

font = FontProperties(size=8)
font_big = FontProperties(size=14)


class EventHandler(object):
    """docstring for EventHandler"""
    def __init__(self, data=None, fig=None):
        self.fig = fig
        self.data = data
        self.pre_x = None

    def on_pick(self, event):
        '''docstring for on_motion'''
        six.print_("888888")
        six.print_(str(event.mouseevent.xdata))
        #six.print_(event.artist)

    def on_move(self, event):
        '''docstring for on_motion'''
        if isinstance(event.xdata, np.float64):
            i = int(event.xdata)/1
            if self.pre_x != i:
                six.print_(self.data.index[i])
                six.print_(self.data[i])
                c = pd.to_datetime(self.data.index[i])\
                      .strftime("%Y-%m-%d %H:%M:%S") + "\n" + "hh"
                self.fig.axes[2].set_xlabel(c)
                self.pre_x = i


def plot_simple_entry(fig, entry_nbar_best, entry_nbar_worst, nbar):
    '''docstring for plot_simple_entry'''
    fig.canvas.set_window_title('入场信息')
    ax1 = fig.add_subplot(1, 1, 1)
    entry_nbar_best = entry_nbar_best.order()
    entry_nbar_worst = entry_nbar_worst.reindex(entry_nbar_best.index)
    if len(entry_nbar_best) > 0:
        entry_nbar_best.plot(
            ax=ax1, kind='bar', color='red',
            grid=False, use_index=False, label="%s根最优" % nbar)
        #ax1.bar(range(len(entry_nbar_best)), entry_nbar_best, color='r', label="%s根最优"%nbar)
        entry_nbar_worst.plot(
            ax=ax1, kind='bar', color='y',
            grid=False, use_index=False, label="%s根最差" % nbar)
        temp = entry_nbar_worst[entry_nbar_worst < 0]
        ax1.plot(range(len(entry_nbar_best)),
                 [temp.mean()]*len(entry_nbar_best),
                 'y--',
                 label="平均风险: %s" % temp.mean())
        temp = entry_nbar_best[entry_nbar_best > 0]
        ax1.plot(range(len(entry_nbar_best)),
                 [temp.mean()]*len(entry_nbar_best),
                 'r--',
                 label='平均最优: %s' % temp.mean())
        ax1.legend(loc='upper left', prop=font).get_frame().set_alpha(0.5)
        ax1.set_xticklabels([])
        ax1.set_xlabel("")
    return [ax1], []


def plot_entry(fig, exit_profit, entry_best, entry_worst,
               entry_nbar_best, entry_nbar_worst, nbar, binwidth=1):
    fig.canvas.set_window_title('入场信息')
    axescolor = '#f6f6f6'  # the axes background color
    left, width = 0.1, 0.8
    rect1 = [left, 0.7, width, 0.2]  # left, bottom, width, height
    rect2 = [left, 0.3, width, 0.4]
    rect3 = [left, 0.1, width, 0.2]

    ax1 = fig.add_axes(rect1, facecolor=axescolor)
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax1)
    ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax1)
    (entry_best-exit_profit).plot(ax=ax1, kind='bar', grid=False,
                                  use_index=False, label="优实差")
    entry_worst.plot(ax=ax1, kind='bar', grid=False,
                     use_index=False, color='y', label="最大不利偏移")
    if nbar > 0:
        entry_nbar_best.plot(ax=ax3, kind='bar', color='red',
                             grid=False, use_index=False,
                             label="%s根最优" % nbar)
        #ax3.bar(range(len(entry_nbar_best)), entry_nbar_best, color='r', label="%s根最优"%nbar)
        entry_nbar_worst.plot(ax=ax3, kind='bar', color='y',
                              grid=False, use_index=False,
                              label="%s根最差" % nbar)
        temp = entry_nbar_worst[entry_nbar_worst < 0]
        ax3.plot(range(len(entry_nbar_best)),
                 [temp.mean()]*len(entry_nbar_best),
                 'y--',
                 label="平均风险: %s" % temp.mean())
        temp = entry_nbar_best[entry_nbar_best > 0]
        ax3.plot(range(len(entry_nbar_best)),
                 [temp.mean()]*len(entry_nbar_best),
                 'r--',
                 label='平均最优: %s' % temp.mean())
        ax3.legend(loc='upper left', prop=font).get_frame().set_alpha(0.5)

    for i in xrange(len(exit_profit)):
        if entry_best[i] > 0 and exit_profit[i] > 0:
            px21 = ax2.bar(i, exit_profit[i], width=binwidth, color='blue')
            px22 = ax2.bar(i, entry_best[i]-exit_profit[i],
                           width=binwidth,
                           color='red',
                           bottom=exit_profit[i])
        elif entry_best[i] < 0 and exit_profit[i] < 0:
            ax2.bar(i, entry_best[i], width=binwidth, color='red')
            ax2.bar(i, exit_profit[i]-entry_best[i],
                    width=binwidth, color='blue', bottom=entry_best[i])
        else:
            ax2.bar(i, entry_best[i], width=binwidth, color='red')
            ax2.bar(i, exit_profit[i], width=binwidth, color='blue')

    ax2.legend((px21[0], px22[0]), ('实际盈利', '早出最优盈利'),
               loc='upper left',
               prop=font).get_frame().set_alpha(0.5)
    ax1.legend(loc='upper left', prop=font).get_frame().set_alpha(0.5)
    ax1.set_ylabel("交易区间内的差值", fontproperties=font)
    ax2.set_ylabel("交易区间内的盈利", fontproperties=font)
    for ax in ax1, ax2, ax3:
        # if ax!=ax3:
        ax.set_xticklabels([])

    ax3.set_xlabel("")
    ax1.set_title("入场相关信息", fontproperties=font_big)
    c1 = Cursor(ax2, useblit=True, color='red',
                linewidth=1, vertOn=True, horizOn=True)
    multi = MultiCursor(fig.canvas, fig.axes, color='r',
                        lw=1, horizOn=False, vertOn=True)

    #handle = EventHandler(exit_profit, fig)
    #fig.canvas.mpl_connect('motion_notify_event', handle.on_move)
    #fig.canvas.mpl_connect('pick_event', handle.on_pick)

    def format_coord(x, y):
        """ 状态栏信息显示 """
        i = int(x)/1
        c = pd.to_datetime(exit_profit.index[i])\
            .strftime("%Y-%m-%d %H:%M:%S") + \
            " Profit: %s MAE: %s" % (exit_profit[i], entry_worst[i])
        return str(c)
    ax1.format_coord = format_coord
    ax2.format_coord = format_coord
    ax3.format_coord = format_coord
    return [ax1, ax2, ax3], [multi, c1]


def plot_exit(fig, exit_profit, exit_nbar_best, exit_nbar_worst,
              profits_more, risks, nbar, binwidth=1):
    # fig.canvas.set_window_title('出场信息')
    axescolor = '#f6f6f6'  # the axes background color
    left, width = 0.1, 0.8
    rect2 = [left, 0.4, width, 0.4]
    rect3 = [left, 0.1, width, 0.3]

    ax1 = fig.add_axes(rect3, facecolor=axescolor)
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax1)
    if nbar > 0:
        six.print_("**66666")
        # plot ax1
        profits_more.plot(ax=ax1, kind='bar', grid = False, use_index = False, label="%s根最优"%nbar)
        risks.plot(ax=ax1, kind='bar', grid = False, use_index = False, color = 'y', label="%s根最差"%nbar)
        temp = risks[risks<0]
        ax1.plot(range(len(temp)), [temp.mean()]*len(temp), 'y--', label="平均风险: %s"%temp.mean())
        temp = profits_more[profits_more>0]
        ax1.plot(range(len(temp)), [temp.mean()]*len(temp), 'r--', label="平均更优: %s"%temp.mean())
        ax1.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
        #ax1.annotate(str(np.mean(risks)), xy=(len(records)/2, np.mean(risks)),  xycoords='data',
                        #xytext=(-30, -30), textcoords='offset points', color='b',
                        #arrowprops=dict(arrowstyle="->",
                                        #connectionstyle="arc3,rad=.2")
                        #)

        # plot ax2
        for i in xrange(len(exit_profit)):
            if(exit_nbar_best[i]>exit_profit[i] and exit_profit[i]>0):
                px21 = ax2.bar(i, exit_profit[i], width=binwidth, color='blue')
                px22 = ax2.bar(i, exit_nbar_best[i]-exit_profit[i], width=binwidth, color='red', bottom = exit_profit[i])
            elif(exit_nbar_best[i]<exit_profit[i] and exit_profit[i]>0 and exit_nbar_best[i]>0):
                ax2.bar(i, exit_nbar_best[i], width=binwidth, color='red')
                ax2.bar(i, exit_profit[i]-exit_nbar_best[i], width=binwidth, color='blue', bottom = exit_nbar_best[i])
            elif(exit_nbar_best[i]<exit_profit[i] and exit_profit[i]<0):
                ax2.bar(i, exit_profit[i], width=binwidth, color='red')
                ax2.bar(i, exit_nbar_best[i]-exit_profit[i], width=binwidth, color='blue', bottom = exit_profit[i])
            elif(exit_nbar_best[i]>exit_profit[i] and exit_profit[i]<0 and exit_nbar_best[i]<0):
                ax2.bar(i, exit_nbar_best[i], width=binwidth, color='red')
                ax2.bar(i, exit_profit[i]-exit_nbar_best[i], width=binwidth, color='blue', bottom = exit_nbar_best[i])
            else:
                ax2.bar(i, exit_nbar_best[i], width=binwidth, color='red')
                ax2.bar(i, exit_profit[i], width=binwidth, color='blue')
        ax2.legend((px21[0], px22[0]), ('实际盈利', '延出最优盈利'),loc='upper left',  prop=font).get_frame().set_alpha(0.5)
        ax2.set_ylabel("交易区间内的盈利", fontproperties = font)
        for ax in ax1, ax2:
            #if ax!=ax1:
            ax.set_xticklabels([])

        ax1.set_xlabel("")
        ax2.set_title("出场相关信息", fontproperties=font_big)
        multi = MultiCursor(fig.canvas, fig.axes, color='r', lw=1, horizOn=False, vertOn=True)
        return [ax1, ax2], [multi]
    else:
        return [], []


def plot_summary(fig, exit_profit, entry_best, entry_worst, entry_nbar_best, entry_nbar_worst,
                    exit_nbar_best, exit_nbar_worst, profits_more, risks, NBAR):
    fig.canvas.set_window_title('画图汇总')
    ax11 = fig.add_subplot(3, 2, 1)
    ax12 = fig.add_subplot(3, 2, 2)
    ax21 = fig.add_subplot(3, 2, 3)
    ax22 = fig.add_subplot(3, 2, 4)
    ax31 = fig.add_subplot(3, 2, 5)
    ax32 = fig.add_subplot(3, 2, 6)
    #plt.subplots_adjust(left=0, right=1)

    # Profits Distribution
    shift = pd.Series([0]*len(exit_profit[exit_profit<=0]))
    temp = pd.concat([shift, exit_profit[exit_profit>0]])
    temp.index = range(len(temp))
    temp.plot(ax=ax11,  grid=False, use_index=False, style="r", label='盈利')
    ax11.fill_between(range(len(temp)), [0]*len(temp), temp.tolist(), facecolor='r')
    temp = 0 - exit_profit[exit_profit<=0]
    ax11.plot(temp, 'y', label='亏损')
    ax11.fill_between(range(len(temp)), [0]*len(temp), temp.tolist(), facecolor='y')
    ax11.plot(entry_worst, 'b', label='最差偏移')
    ax11.axhline(color='black')
    ax11.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)


    # Profits Distribution Bins
    #exit_profit.hist(ax=ax12, bins=50, normed=True, color='r')
    #n, bins = np.histogram(exit_profit.tolist(), 50, normed=True)
    #ax12.plot([0, 0], [0, max(n)], color='y', linewidth=2)
    #ax12.grid(False)
    exit_profit.plot(ax=ax12, kind='kde', color='b', label="")
    binwidth = abs(exit_profit.min()/9)
    bins = np.arange(exit_profit.min(), exit_profit.max() + binwidth, binwidth)
    ax12.hist(exit_profit[exit_profit>0], bins=bins, color = 'red' , normed=False, label='盈利分布')
    ax12.hist(exit_profit[exit_profit<0], bins=bins, color = 'y' , normed=False, label='亏损分布')
    plot_contribution(ax12, bins, exit_profit, 'bo--')
    ax12.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    #ax12.set_yscale('log')

    # MAE
    MAE = entry_worst.reindex(exit_profit[exit_profit>0].index)
    MAE.order().plot(ax=ax21,style='r', grid=False, use_index=False, label='最大不利偏移')
    exit_profit[exit_profit<0].plot(ax=ax21, style='y', grid=False, use_index=False, label='亏损分布')
    worst = MAE.min()
    six.print_("最大不利偏移: %s" % worst)
    bb = exit_profit[exit_profit<0]
    aa = [worst]*len(bb)
    ax21.fill_between(range(len(exit_profit[exit_profit<0])), aa, bb, where=bb<aa, color='red')
    ax21.set_ylim((min(exit_profit.min(), MAE.min())-10), 0)
    ax21.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)

    # Potential Profits When Lose
    temp = entry_best.reindex(exit_profit[exit_profit<0].index)
    ax22.plot(temp.tolist(), color='r', label="最优盈利" )
    ax22.fill_between(range(len(temp)), temp.tolist(), [0]*len(temp), facecolor='r')
    ax22.plot(temp.order().tolist(), color='b', label="有序最优盈利" )
    ax22.plot(exit_profit[exit_profit<0].tolist(), color='y', label='实际亏损')
    ax22.set_ylim((min(exit_profit.min(), MAE.min())-10, temp.max()+10))
    ax22.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    ax22.axhline(0, c='black')

    if NBAR > 0:
        # Entry N Bar
        enbest = entry_nbar_best.reindex(entry_nbar_best[entry_nbar_best>0].index).order()
        enbest.plot(ax=ax31,style='r', grid=False, use_index=False, label="%s根最优平均: %s"%(NBAR, entry_nbar_best[entry_nbar_best>0].mean()))
        enworst = (0-entry_nbar_worst.reindex(entry_nbar_worst[entry_nbar_worst<0].index).order(ascending=False))
        enworst.plot(ax=ax31, style='y', grid=False, use_index=False,
                label="%s根最差平均: %s"%(NBAR, entry_nbar_worst[entry_nbar_worst<0].mean()))
        ax31.axhline(0, c='black')
        ax31.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
        # Exit N Bar
        profits_more.reindex(profits_more[profits_more>0].index).order().plot(ax=ax32,style='r',
                grid=False, use_index=False, label="%s根最优平均: %s"%(NBAR, profits_more[profits_more>0].mean()))
        (0-risks.reindex(risks[risks<0].index).order(ascending=False)).plot(ax=ax32, style='y',
                grid=False, use_index=False, label="%s根最差平均: %s"%(NBAR,risks[risks<0].mean()))
        ax32.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)

    #
    #ax31.xaxis_date()
    map(lambda x: x.set_xticklabels([]), [ax11, ax21, ax22, ax31, ax32])
    map(lambda x: x.set_xlabel(""), [ax11, ax12, ax21, ax22, ax31, ax32])
    map(lambda x: x.set_ylabel(""), [ax11, ax12, ax21, ax22, ax31, ax32])
    ax11.set_xlabel("盈利分布", fontproperties=font_big)
    ax12.set_ylabel("盈利统计", fontproperties=font_big)
    ax21.set_xlabel("最大不利偏移和亏损", fontproperties=font_big)
    ax22.set_xlabel("亏损交易的潜在盈利空间", fontproperties=font_big)
    ax31.set_xlabel("进场后%s根"%NBAR, fontproperties=font_big)
    ax32.set_xlabel("离场后%s根"%NBAR, fontproperties=font_big)

    cursors = []
    for ax in [ax11, ax12, ax21, ax22, ax31, ax32]:
        cursors.append(Cursor(ax, useblit=True, color='red', linewidth=1,
                            vertOn = True, horizOn = True))
    return [ax11, ax12, ax21, ax22, ax31, ax32], cursors


def plot_scatter(fig, x, y, x2, y2, binnum):
    '''docstring for plot_test'''
    fig.canvas.set_window_title('交易鸟瞰图')
    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    # start with a rectangular Figure

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)
    cursor = Cursor(axScatter, useblit=True, color='red', linewidth=1 )

    axScatter.plot(x, y, 'o', color = 'red')
    axScatter.plot(x2, y2, 'o', color = 'blue')

    # now determine nice limits by hand:
    xmax = np.max(x+x2)
    xmin = np.min(x+x2)
    binwidth = xmax / binnum
    lim = ( int(xmax/binwidth) + 1) * binwidth
    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x+x2, bins=bins)

    ymax = np.max(y+y2)
    ymin = np.min(y+y2)
    binwidth = ymax/binnum
    lim = ( int(ymax/binwidth) + 1) * binwidth
    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHisty.hist(y, bins=bins, orientation='horizontal', color = 'red' )
    axHisty.hist(y2, bins=bins, orientation='horizontal', color = 'blue' )

    xymax = np.max( [np.max(np.fabs(x+x2)), np.max(np.fabs(y+y2))] )
    lim = ( int(xymax/binwidth) + 1) * binwidth
    axScatter.axhline(color='black')

    #axScatter.set_xlim( (-xmin-10, xmax+10))
    #axScatter.set_ylim((-ymin-10, ymax+10))
    axHistx.set_xlim( axScatter.get_xlim() )
    axHisty.set_ylim( axScatter.get_ylim() )
    axHisty.set_xlabel("盈亏分布", fontproperties = font_big)
    axHistx.set_ylabel("周期分布", fontproperties = font_big)
    axScatter.set_xlabel("盈亏和周期分布", fontproperties = font_big)

    axScatter.grid(True)
    axHistx.grid(True)
    axHisty.grid(True)
    c = Cursor(axScatter, useblit=True, color='red', linewidth=1, vertOn = True, horizOn = True)
    return [axScatter, axHistx, axHisty], [c]


def plot_compare(exit_profits, entry_bests, entry_worsts, entry_nbar_bests, entry_nbar_worsts,
                    exit_nbar_bests, exit_nbar_worsts, profits_mores, risks, colors, names, NBAR):
    fig = plt.figure(facecolor='white')
    fig.canvas.set_window_title('画图汇总一')
    ax11 = fig.add_subplot(3, 2, 1)
    ax12 = fig.add_subplot(3, 2, 2)
    ax21 = fig.add_subplot(3, 2, 3)
    ax22 = fig.add_subplot(3, 2, 4)
    ax31 = fig.add_subplot(3, 2, 5)
    ax32 = fig.add_subplot(3, 2, 6)
    #plt.subplots_adjust(left=0, right=1)
    for i in range(len(exit_profits)):
        nm = names[i]
        exit_profit = exit_profits[i]
        entry_best = entry_bests[i]
        entry_worst = entry_worsts[i]
        entry_nbar_best = entry_nbar_bests[i]
        entry_nbar_worst = entry_nbar_worsts[i]
        exit_nbar_best = exit_nbar_bests[i]
        exit_nbar_worst = exit_nbar_worsts[i]
        profits_more = profits_mores[i]
        risk = risks[i]
        c = colors[i]

        # Profits Distribution
        shift = pd.Series([0]*len(exit_profit[exit_profit<=0]))
        temp = pd.concat([shift, exit_profit[exit_profit>0]])
        temp.index = range(len(temp))
        temp.plot(ax=ax11,  grid=False, use_index=False, style=c, label='%s盈利'%nm)
        temp = 0 - exit_profit[exit_profit<=0]
        ax11.plot(temp.tolist(), c, label='%s亏损'%nm)
        ax11.plot(entry_worst.tolist(), c, label='%s最差偏移'%nm)
        #ax11.set_xscale('log')


        # Profits Distribution Bins
        #exit_profit.hist(ax=ax12, bins=50, normed=True, color=c)
        #exit_profit.plot(ax=ax12, kind='kde', color='b', label="")
        #ax12.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
        a = np.histogram(exit_profit.tolist(), 50, normed=True)
        n = pd.Series(a[0])
        bins = pd.Series(a[1][:-1])
        temp = bins[bins>0]
        ax12.plot(temp.tolist(), n.reindex(temp.index).tolist(), c, label='%s盈利分布'%nm)
        temp = bins[bins<0]
        ax12.plot(temp.tolist(), n.reindex(temp.index).tolist(), '%s--'%c, label='%s亏损分布'%nm)
        ax12.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)


        # MAE
        MAE = entry_worst.reindex(exit_profit[exit_profit>0].index)
        MAE.order().plot(ax=ax21,style=c, grid=False, use_index=False, label='%s最大不利偏移'%nm)
        exit_profit[exit_profit<0].plot(ax=ax21, style='%s--'%c, grid=False, use_index=False, label='%s亏损分布'%nm)

        # Potential Profits When Lose
        temp = entry_best.reindex(exit_profit[exit_profit<0].index)
        ax22.plot(temp.tolist(), c, label="%s最优盈利" % nm)
        ax22.plot(temp.order().tolist(), '%s--'%c, label="%s有序最优盈利" % nm)
        ax22.plot(exit_profit[exit_profit<0].tolist(), '%s--'%c, label='%s实际亏损'%nm)

        if len(entry_nbar_best)>0:
            # Entry N Bar
            entry_nbar_best.reindex(entry_nbar_best[entry_nbar_best>0].index).order().plot(ax=ax31,style=c,
                    grid=False, use_index=False, label="%s%s根最优平均: %s"%(nm, NBAR, entry_nbar_best[entry_nbar_best>0].mean()))
            (0-entry_nbar_worst.reindex(entry_nbar_worst[entry_nbar_worst<0].index).order(ascending=False)).plot(ax=ax31, style='%s--'%c,
                    grid=False, use_index=False, label="%s%s根最差平均: %s"%(nm, NBAR, entry_nbar_worst[entry_nbar_worst<0].mean()))

            # Exit N Bar
            profits_more.reindex(profits_more[profits_more>0].index).order().plot(ax=ax32,style=c,
                    grid=False, use_index=False, label="%s%s根最优平均: %s"%(nm,NBAR, profits_more[profits_more>0].mean()))
            (0-risk.reindex(risk[risk<0].index).order(ascending=False)).plot(ax=ax32, style='%s--'%c,
                    grid=False, use_index=False, label="%s%s根最差平均: %s"%(nm,NBAR,risk[risk<0].mean()))

    #
    #ax31.xaxis_date()
    map(lambda x: x.set_xticklabels([]), [ax11, ax21, ax22, ax31, ax32])
    map(lambda x: x.set_xlabel(""), [ax11, ax12, ax21, ax22, ax31, ax32])
    map(lambda x: x.set_ylabel(""), [ax11, ax12, ax21, ax22, ax31, ax32])
    ax11.set_xlabel("盈利分布", fontproperties=font_big)
    ax12.set_ylabel("盈利统计", fontproperties=font_big)
    ax12.axvline(color='black')
    ax21.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    ax21.set_xlabel("最大不利偏移和亏损", fontproperties=font_big)
    ax22.set_xlabel("亏损交易的潜在盈利空间", fontproperties=font_big)
    ax31.set_xlabel("进场后%s根"%NBAR, fontproperties=font_big)
    ax32.set_xlabel("离场后%s根"%NBAR, fontproperties=font_big)
    ax11.axhline(color='black')
    ax11.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    ax22.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    ax22.axhline(0, c='black')
    ax31.axhline(0, c='black')
    ax31.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    ax32.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    ax12.set_xlim((np.min(a[1][:-1])-100, np.max(a[1][:-1])+50))
    ax21.set_ylim((min(exit_profit.min(), MAE.min())-10), 0)
    ax22.set_ylim((min(exit_profit.min(), MAE.min())-10, temp.max()+10))

    cursors = []
    for ax in [ax11, ax12, ax21, ax22, ax31, ax32]:
        cursors.append(Cursor(ax, useblit=True, color='red', linewidth=1,
                            vertOn = True, horizOn = True))
    return fig, cursors


def ax_normed_data(x1list, y1list, ax_ymax):
    '''docstring for normed_data'''
    unit = ax_ymax / max(abs(y1list))
    nxlist = []
    nylist = []
    for i in range(len(y1list)):
        if y1list[i] != 0:
            nxlist.append(x1list[i])
            nylist.append(y1list[i])
    nylist = np.abs(np.array(nylist)*unit)
    return nxlist, nylist


def plot_contribution(ax, bins, v, style):
    '''docstring for plot_contribution'''
    ctri = np.array(range(len(bins)-1))
    ymin, ymax = ax.get_ylim()
    for i in range(len(bins)-1):
        t = v[bins[i]<=v]
        t = t[t<bins[i+1]]
        ctri[i] = t.sum()
    x = [(bins[i]+bins[i+1])/2 for i in range(len(bins)-1)]
    nx, ny = ax_normed_data(x, ctri, ymax)
    ax.plot(nx, ny, style)

    losex = []
    losey = []
    winx = []
    winy = []
    for i in range(len(x)):
        if x[i]<0:
            losex.append(x[i])
            losey.append(ctri[i])
        else:
            winx.append(x[i])
            winy.append(ctri[i])
    losey = [i for i in accumulate(losey[::-1])]
    losey = losey[::-1]
    winy = [i for i in accumulate(winy)]
    nx, ny = ax_normed_data(x, np.array(losey+winy), ymax)
    ax.plot(nx, ny, 'k')


def plot_summary2(fig, rtn, entry_best, data_win, data_lose, exit_profit,
                    exit_nbar_best, exit_nbar_worst, nbar):
    ''' loseed arguments '''
    cursors = []
    winrtn = rtn.reindex(data_win.index)
    losertn = rtn.reindex(data_lose.index)
    fig.canvas.set_window_title('画图汇总二')
    ax11 = fig.add_subplot(2, 2, 1)
    ax11.plot(range(len(losertn)), losertn.tolist(), 'yo--', label='亏损回撤')
    ax11.plot(len(losertn)+np.arange(len(winrtn)), winrtn.tolist(), 'ro--', label='盈利回撤')
    ax11.plot(rtn.order().tolist(), 'b')

    ax11.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    cursors.append(Cursor(ax11, useblit=True, color='red', linewidth=1,
                                vertOn = True, horizOn = True))

    ax11.set_xlabel('回撤', fontproperties=font_big)

    ax12 = fig.add_subplot(2, 2, 2)
    binwidth = (rtn.max() - rtn.min()) / 30
    #rtn.plot(ax=ax12, kind='kde', color='b', label="")
    bins = np.arange(rtn.min(), rtn.max() + binwidth, binwidth)
    rst = ax12.hist(rtn, bins=bins, color = 'y' , normed=False, label='回撤分布')
    n, bins = rst[0], rst[1]
    plot_contribution(ax12, bins, rtn, 'bo--')
    ax12.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    cursors.append(Cursor(ax12, useblit=True, color='red', linewidth=1,
                                vertOn = True, horizOn = True))

    #ax21 = fig.add_subplot(3, 2, 3)
    #ds = entry_best.reindex(data_lose.index)-data_lose['exit_profit']
    #ax21.plot(range(len(ds)), ds, 'yo--', label='亏损回吐')
    #dl = (entry_best.reindex(data_win.index)-data_win['exit_profit']).tolist()
    #ax21.plot(len(ds)+np.arange(len(dl)), dl, 'ro--', label='盈利回吐')
    #ax21.set_xticklabels([])
    #ax21.set_xlabel('回吐', fontproperties=font_big)
    #ax21.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    #cursors.append(Cursor(ax21, useblit=True, color='red', linewidth=1,
                                #vertOn = True, horizOn = True))


    #diff = entry_best - exit_profit
    #ax22 = fig.add_subplot(3, 2, 4)
    #binwidth = (diff.max() - diff.min()) / 30
    ##diff.plot(ax=ax22, kind='kde', color='b', label="")
    #bins = np.arange(diff.min(), diff.max() + binwidth, binwidth)
    #rst = ax22.hist(diff, bins=bins, color = 'y' , normed=False, label='回吐分布')
    #n, bins = rst[0], rst[1]
    #plot_contribution(ax22, bins, diff, 'bo--')
    #ax22.legend(prop=font, loc='upper left').get_frame().set_alpha(0.5)
    #cursors.append(Cursor(ax22, useblit=True, color='red', linewidth=1,
                                #vertOn = True, horizOn = True))
    if nbar>0:
        ax31 = fig.add_subplot(2, 2, 3)
        bl = (exit_nbar_best.reindex(data_lose.index)-data_lose['exit_profit']).order(ascending=False)
        wl = (exit_nbar_worst.reindex(data_lose.index)-data_lose['exit_profit']).reindex(bl.index)
        ax31.plot(bl, color='y')
        ax31.plot(wl, color='k')
        ax31.fill_between(range(len(bl)), bl, wl, facecolor='y')
        bw = (exit_nbar_best.reindex(data_win.index)-data_win['exit_profit']).order()
        ww = (exit_nbar_worst.reindex(data_win.index)-data_win['exit_profit']).reindex(bw.index)
        ax31.plot(len(bl)+np.arange(len(bw)), bw.tolist(), 'r')
        ax31.plot(len(bl)+np.arange(len(ww)), ww.tolist(), 'k')
        ax31.fill_between(len(bl)+np.arange(len(ww)), bw, ww, facecolor='r', label='hello')
        ax31.plot(data_lose['exit_profit'].abs().reindex(bl.index), 'b')
        cursors.append(Cursor(ax31, useblit=True, color='red', linewidth=1,
                                    vertOn = True, horizOn = True))
        ax31.axhline(color='k')
    return [ax11, ax12, ax31], cursors
