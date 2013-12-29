# -*- coding: gbk -*-
import matplotlib
matplotlib.use("TKAgg")
from matplotlib.widgets import Button, RadioButtons
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from stock_plot import *
from data import *

def summary(data):
    '''docstring for plot_table''' 
    data_win = data[data.exit_profit>0]
    data_lose = data[data.exit_profit<0]
    zero_df = data[data.exit_profit==0]
    total_num = len(data)
    av_period = data['period'].mean()
    #plt.figure()
    #rows = [
            #u"Overall Profits: ", 
            #u"Overall Loss: ", 
            #u"Net Profits: ", 
            #u"Number of Transaction: ", 
            #u"Number of Winning Trades: ",
            #u"Number of Losing Trades: ",
            #u"Average Profit:",
            #u"AV Profits / AV Loss: ", 
            #u"Winning Percentage: ",
            #u"Stock Holding Period: " 
           #]

    #cell_text=[
                #[str(data_win.exit_profit.sum() * 300)],
                #[str(data_lose.exit_profit.sum() * 300)],
                #[str((data.exit_profit.sum()) * 300)],
                #[str(total_num)],
                #[str(len(data_win))],
                #[str(len(data_lose))], 
                #[str(data_win.exit_profit.sum()/ total_num*300)],
                #[str(abs(data_win.exit_profit.sum()/len(data_win) / (data_lose.exit_profit.sum()/len(data_lose))))],
                #[str(len(data_win)/float(total_num)*100) + "%" ], 
                #[str(av_period)]
              #]
    #columns=(['Summary'])
    #assert len(cell_text) == len(rows)
    ## Add a table at the bottom of the axes

    #the_table = plt.table(cellText=cell_text,
                      #colWidths = [0.4],
                      #rowLabels=rows,
                      #colLabels=columns,
                      #loc='center right', fontsize=14)
    #plt.text(12,3.4,'Table Title',size=8)
    print "******************************************" 
    print u"总盈利: " + str(data_win.exit_profit.sum() * 300)
    print u"总亏损: " + str(data_lose.exit_profit.sum() * 300)
    print u"总利润: " + str((data.exit_profit.sum()) * 300)
    print "******************************************" 
    print u"交易次数: " + str(total_num)
    print u"盈利次数: " + str(len(data_win))
    print u"亏损次数: " + str(len(data_lose))
    print u"平均利润 :%s" % str(data_win.exit_profit.sum()/ total_num*300)
    print u"盈亏比: " + str(abs(data_win.exit_profit.sum()/len(data_win) / (data_lose.exit_profit.sum()/len(data_lose))))
    print u"胜率: " + str(len(data_win)/float(total_num)*100) + "%" 
    print u"平均持仓周期: " + str(av_period)
    print "******************************************" 


def simple_entry_analyze(fig, data, n):
    '''docstring for simple_entry_analyze(dat)''' 
    data2 = data
    entry_nbar_best = data2['entry_nbar_best']
    entry_nbar_worst = data2['entry_nbar_worst']
    return plot_simple_entry(fig, entry_nbar_best, entry_nbar_worst, n)


def entry_analyze(fig, data, n):
    '''入场信息图
    
    参数：
        data: 数据
    ''' 
    # ordered by profits
    data2 = data.sort_index(by='exit_profit')

    data_long = data2[data2['islong'] ] # 如果是单根开平，且开平价一样，那么此法不成立
    data_short = data2[data2['islong'] == False]

    exit_profit = data2['exit_profit']
    entry_best = pd.concat([data_long.high_profit, data_short.low_profit]).reindex(data2.index)
    entry_worst = pd.concat([data_long.low_profit, data_short.high_profit]).reindex(data2.index)
    try:
        entry_nbar_best = data2['entry_nbar_best']
        entry_nbar_worst = data2['entry_nbar_worst']
    except Exception, e:
        entry_nbar_best = []
        entry_nbar_worst = []
        

    return plot_entry(fig, exit_profit, entry_best, entry_worst, entry_nbar_best, entry_nbar_worst, n)


def exit_analyze(fig, data, n):
    '''出场信息图''' 
    # ordered by profits
    data2 = data.sort_index(by='exit_profit')
    exit_profit = data2['exit_profit']
    try:
        exit_nbar_best = data2['exit_nbar_best']
        exit_nbar_worst = data2['exit_nbar_worst']
        profits_more = exit_nbar_best - exit_profit
        risks = exit_nbar_worst - exit_profit
        return  plot_exit(fig, exit_profit, exit_nbar_best, exit_nbar_worst, profits_more, risks, n)
    except Exception, e:
        return [], []


def scatter_analyze(fig, data):
    '''交易分布鸟瞰图''' 
    data_win = data[data.exit_profit>0]
    data_lose = data[data.exit_profit<0]
    return  plot_scatter(fig, data_win.period.tolist(), data_win.exit_profit.tolist(),
                            data_lose.period.tolist(),
                            data_lose.exit_profit.tolist(), 30)


def follow_entry_analyze(fig, data, nbar):
    '''恒敏的入场效率评估''' 
    # 
    #data_long = data[data.high_profit>data.low_profit] # 如果是单根开平，且开平价一样，那么此法不成立
    #data_short = data[data.high_profit<=data.low_profit]
    #ax = fig.add_subplot(111)
    #effi_HM = entry_efficiency_HM(data_long, data_short, nbar)
    #ax.plot(effi_HM.order().tolist(), color='b')
    #ax.bar(range(len(effi_HM)), effi_HM.tolist(), color='r')
    #return [ax], []
    pass


# Entry analyze
def summary_analyze(fig, data, n, type_):
    ''' 策略信息概括 '''
    print "prepare plotting.." 
    cursors = []
    # ordered by profits
    data = data.sort_index(by='exit_profit')
    data_long = data[data['islong']] # 如果是单根开平，且开平价一样，那么此法不成立
    data_short = data[data['islong'] == False]

    exit_profit = data['exit_profit']
    entry_best = pd.concat([data_long.high_profit, data_short.low_profit]).reindex(data.index)
    entry_worst = pd.concat([data_long.low_profit, data_short.high_profit]).reindex(data.index)
    try:
        entry_nbar_best = data['entry_nbar_best']
        entry_nbar_worst = data['entry_nbar_worst']
        exit_nbar_best = data['exit_nbar_best']
        exit_nbar_worst = data['exit_nbar_worst']
        profits_more = exit_nbar_best - exit_profit
        risks = exit_nbar_worst - exit_profit
    except Exception, e:
        entry_nbar_best = pd.Series()
        entry_nbar_worst = pd.Series()
        exit_nbar_best = pd.Series()
        exit_nbar_worst = pd.Series()
        profits_more = pd.Series()
        risks = pd.Series()
        print "No nbar!" 
    rtns = data['return']
    data_win = data[data.exit_profit>0]
    data_lose = data[data.exit_profit<=0]
    print "begin plotting.." 
    # summary
    #cursors.append(cursor)

    #fig, cursor = plot_summary2(rtns, entry_best, data_win, data_lose, exit_profit,exit_nbar_best, exit_nbar_worst, n)
    #cursors.append(cursor)
    print "***8888888*********" 
    print n
    if type_ == 1:
        return plot_summary(fig, exit_profit, entry_best, entry_worst, entry_nbar_best, entry_nbar_worst,
                                        exit_nbar_best, exit_nbar_worst, profits_more, risks, n)
    elif type_ == 2:
        return plot_summary2(fig, rtns, entry_best, data_win, data_lose, exit_profit,exit_nbar_best, exit_nbar_worst, n)


def compare_analyze(datas, colors=['r'], names=[]):
    '''策略比较''' 
    NBAR = len(datas[0].ix[0, 'entry_0':'entry_N'])-2
    print "prepare plotting.." 
    figs = []
    axes = []

    exit_profits = []
    entry_bests = []
    entry_worsts = []
    entry_nbar_bests = []
    entry_nbar_worsts = []
    exit_nbar_bests = []
    exit_nbar_worsts = []
    profits_mores = []
    risks = []

    # ordered by profits
    for data in datas:
        data = data.sort_index(by='exit_profit')
        data_long = data[data.high_profit>data.low_profit] # 如果是单根开平，且开平价一样，那么此法不成立
        data_short = data[data.high_profit<=data.low_profit]
        exit_profit = data['exit_profit']
        entry_best = pd.concat([data_long.high_profit, data_short.low_profit]).reindex(data.index)
        entry_worst = pd.concat([data_long.low_profit, data_short.high_profit]).reindex(data.index)
        entry_nbar_best = data['entry_nbar_best']
        entry_nbar_worst = data['entry_nbar_worst']
        exit_nbar_best = data['exit_nbar_best']
        exit_nbar_worst = data['exit_nbar_worst']
        profits_more = exit_nbar_best - exit_profit
        risk = exit_nbar_worst - exit_profit

        exit_profits.append(exit_profit)
        entry_bests.append(entry_best)
        entry_worsts.append(entry_worst)
        entry_nbar_bests.append(entry_nbar_best)
        entry_nbar_worsts.append(entry_nbar_worst)
        exit_nbar_bests.append(exit_nbar_best)
        exit_nbar_worsts.append(exit_nbar_worst)
        profits_mores.append(profits_more)
        risks.append(risk)

    # compare
    fig, ax = plot_compare(exit_profits, entry_bests, entry_worsts, entry_nbar_bests, entry_nbar_worsts,
                            exit_nbar_bests, exit_nbar_worsts, profits_mores, risks, colors, names, NBAR)
    figs.append(fig)
    axes.append(ax)
    plt.show()
    return figs, axes


class AnalyzeFrame(object):
    """
    A slider representing a floating point range

    """
    def __init__(self, fname, n=10, intraday=False):
        """ """
        self.fig = plt.figure(facecolor='white')
        self.fig.canvas.set_window_title(u'期货数据分析')
        self.nbar = n
        self.cursors = []
        self.data, = load_datas(n, intraday, fname)
        self.axes = []
        self.rax = plt.axes([0, 0.5, 0.08, 0.15])
        self.radio = RadioButtons(self.rax, ('scatter', 'summary', 'summary2', 'entry', 'exit', 'simple'), active=0)
        self.axes, self.cursors = scatter_analyze(self.fig, self.data)
        self.radio.on_clicked(self.update)

    def update(self, op):
        for ax in self.axes:
            self.fig.delaxes(ax)
        for c in self.cursors:
            del c
        if op == "scatter":
            print "scatter_analyze" 
            self.axes, self.cursors = scatter_analyze(self.fig, self.data)
        elif op == "summary":
            print "summary_analyze" 
            self.axes, self.cursors = summary_analyze(self.fig, self.data, self.nbar, 1)
        elif op == "summary2":
            print "summary2_analyze" 
            self.axes, self.cursors = summary_analyze(self.fig, self.data, self.nbar, 2)
        elif op == "entry":
            print "entry_analyze" 
            self.axes, self.cursors = entry_analyze(self.fig, self.data, self.nbar)
        elif op == "exit":
            print "exit_analyze" 
            self.axes, self.cursors = exit_analyze(self.fig, self.data, self.nbar)
        elif op == "simple":
            self.axes, self.cursors = simple_entry_analyze(self.fig, self.data, self.nbar)
        #elif op == "hm":
            #axes, cursors = follow_entry_analyze(fig, data)
            #print "hm" 
        self.fig.canvas.draw()
