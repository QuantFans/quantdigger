# -*- coding: utf-8 -*-

import six
from six.moves import range
import matplotlib
matplotlib.use("TKAgg")
from matplotlib.widgets import RadioButtons
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

from . import stock_plot

def max_return(nbarprice, islong):
    '''docstring for maxreturn''' 
    high = -1000000
    low = 1000000
    maxdiffs = []
    if islong:
        for ith_price in nbarprice:
            if ith_price > high:
                high = ith_price
                low = 1000000
            elif ith_price < low:
                low = ith_price
                maxdiffs.append(high-low)
                #six.print_(low)
        return max(maxdiffs) if maxdiffs else 0
    else:
        for ith_price in nbarprice:
            if ith_price < low:
                low = ith_price
                high = -1000000
                #six.print_(low)
            elif ith_price > high:
                high = ith_price
                maxdiffs.append(high-low)
        return max(maxdiffs) if maxdiffs else 0


def process_data(n, intraday, tradeinfo, price_data):
    """
    tradeinfo:  entry_datetime, entry_price, exit_datetime, exit_price, is_long
    price_data: open, close, high, low, volume
    """
    '''''' 
    PRICE = 'close'  # related to visible price of trading
    data = pd.DataFrame(tradeinfo.ix[:,0:2])  # subframe
    high_profits = []
    low_profits = []
    exit_profits = []

    periods = []
    entry_nbar_bests = []
    entry_nbar_worsts = []
    exit_nbar_bests = []
    exit_nbar_worsts = []
    islongs = []
    returns = []
    for i in range(len(tradeinfo)):
        startt = tradeinfo.index[i]   # entry_datetime
        startpos = price_data.index.searchsorted(startt)
        onetrade = tradeinfo.ix[i, :]  # trade i info
        endt = onetrade['exit_datetime']   # specific line i, columns 'exit_datetime'
        endpos = price_data.index.searchsorted(endt)
        tradingdf = price_data.truncate(before=startt, after = endt) # price[startt, endt]
        # high/low
        # @NOTE need more work
        if len(tradingdf) > 1:
            hp = tradingdf.ix[:-1, :][PRICE].max()  # last 'close' is invisible
            lp = tradingdf.ix[:-1, :][PRICE].min() 
            t = tradingdf.ix[:-1, :][PRICE].tolist()
            t.append(float(onetrade['exit_price']))   #
            returns.append(max_return(t, onetrade['islong']))
        else:
            # buy and sell in the same bar
            hp = tradingdf.ix[:, :][PRICE].max()
            lp = tradingdf.ix[:, :][PRICE].min()
            if onetrade['islong']:
                returns.append(max(onetrade['entry_price']-onetrade['exit_price'], 0))
            else:
                returns.append(max(onetrade['exit_price']-onetrade['entry_price'], 0))

        hp = onetrade['exit_price'] if onetrade['exit_price'] > hp else hp
        hp = onetrade['entry_price'] if onetrade['entry_price'] > hp else hp
        lp = onetrade['exit_price'] if onetrade['exit_price'] < lp else lp
        lp = onetrade['entry_price'] if onetrade['entry_price'] < lp else lp

        hp = hp - onetrade['entry_price']
        lp = lp - onetrade['entry_price']
        high_profits.append(hp if onetrade['islong'] else 0-hp)
        low_profits.append(lp if onetrade['islong'] else 0-lp)
        # exit
        ep = onetrade['exit_price'] - onetrade['entry_price']
        exit_profits.append(ep if onetrade['islong'] else 0-ep)
        # period
        periods.append(endpos - startpos + 1)

        # nbar
        entry_begin = startpos  # first bar after entry
        exit_begin = endpos + 1  # the first bar after exit
        if intraday:
            # the first bar after day of entry
            day_entry_end = price_data.index.searchsorted((pd.to_datetime(startt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            day_exit_end = price_data.index.searchsorted((pd.to_datetime(endt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            entry_end = min(startpos+n+1, day_entry_end) # so called intraday
            exit_end = min(endpos+1+n, day_exit_end)
        else:
            entry_end = startpos + n + 1  # the nth bar after entry
            exit_end = endpos + 1 + n
        islongs.append(onetrade['islong'])
        if onetrade['islong']:
            entry_nbar_bests.append(price_data.ix[entry_begin: entry_end, PRICE].max() - onetrade['entry_price'])
            entry_nbar_worsts.append(price_data.ix[entry_begin: entry_end, PRICE].min() - onetrade['entry_price'])
            exit_nbar_bests.append(price_data.ix[exit_begin: exit_end, PRICE].max() - onetrade['entry_price'])
            exit_nbar_worsts.append(price_data.ix[exit_begin: exit_end, PRICE].min() - onetrade['entry_price'])
        else:
            entry_nbar_bests.append(onetrade['entry_price'] - price_data.ix[entry_begin: entry_end, PRICE].min())
            entry_nbar_worsts.append(onetrade['entry_price'] - price_data.ix[entry_begin: entry_end, PRICE].max())
            exit_nbar_bests.append(onetrade['entry_price'] - price_data.ix[exit_begin: exit_end, PRICE].min())
            exit_nbar_worsts.append(onetrade['entry_price'] - price_data.ix[exit_begin: exit_end, PRICE].max())

    data['high_profit'] = high_profits
    data['low_profit'] = low_profits
    data['exit_profit'] = exit_profits
    data['period'] = periods
    data['return'] = returns
    data['entry_nbar_best'] = entry_nbar_bests
    data['entry_nbar_worst'] = entry_nbar_worsts
    data['exit_nbar_best'] = exit_nbar_bests
    data['exit_nbar_worst'] = exit_nbar_worsts
    data['islong'] = islongs
    six.print_("Data Preprocessing Done!")
    #data.to_csv("d:\\rst.csv")
    return data



def summary(data):
    data_win = data[data.exit_profit>0]
    data_lose = data[data.exit_profit<0]
    zero_df = data[data.exit_profit==0]
    total_num = len(data)
    av_period = data['period'].mean()
    plt.figure()
    rows = [
            "Overall Profits: ", 
            "Overall Loss: ", 
            "Net Profits: ", 
            "Number of Transaction: ", 
            "Number of Winning Trades: ",
            "Number of Losing Trades: ",
            "Average Profit:",
            "AV Profits / AV Loss: ", 
            "Winning Percentage: ",
            "Stock Holding Period: " 
           ]

    cell_text=[
                [str(data_win.exit_profit.sum() * 300)],
                [str(data_lose.exit_profit.sum() * 300)],
                [str((data.exit_profit.sum()) * 300)],
                [str(total_num)],
                [str(len(data_win))],
                [str(len(data_lose))], 
                [str(data_win.exit_profit.sum()/ total_num*300)],
                [str(abs(data_win.exit_profit.sum()/len(data_win) / (data_lose.exit_profit.sum()/len(data_lose))))],
                [str(len(data_win)/float(total_num)*100) + "%" ], 
                [str(av_period)]
              ]
    columns=(['Summary'])
    assert len(cell_text) == len(rows)
    # Add a table at the bottom of the axes

    the_table = plt.table(cellText=cell_text,
                      colWidths = [0.4],
                      rowLabels=rows,
                      colLabels=columns,
                      loc='center right', fontsize=14)
    plt.text(12,3.4,'Table Title',size=8)
    six.print_("******************************************")
    six.print_("总盈利: " + str(data_win.exit_profit.sum() * 300))
    six.print_("总亏损: " + str(data_lose.exit_profit.sum() * 300))
    six.print_("总利润: " + str((data.exit_profit.sum()) * 300))
    six.print_("******************************************")
    six.print_("交易次数: " + str(total_num))
    six.print_("盈利次数: " + str(len(data_win)))
    six.print_("亏损次数: " + str(len(data_lose)))
    six.print_("平均利润: " + str(data_win.exit_profit.sum()/ total_num*300))
    six.print_("盈亏比: " + str(abs(data_win.exit_profit.sum()/len(data_win) / (data_lose.exit_profit.sum()/len(data_lose)))))
    six.print_("胜率: " + str(len(data_win)/float(total_num)*100) + "%" )
    six.print_("平均持仓周期: " + str(av_period))
    six.print_("******************************************")


def simple_entry_analyze(fig, data, n):
    '''docstring for simple_entry_analyze(dat)''' 
    data2 = data
    entry_nbar_best = data2['entry_nbar_best']
    entry_nbar_worst = data2['entry_nbar_worst']
    return plot_simple_entry(fig, entry_nbar_best, entry_nbar_worst, n)


def entry_analyze(fig, data, n):
    '''Èë³¡ÐÅÏ¢Í¼
    
    ²ÎÊý£º
        data: Êý¾Ý
    ''' 
    # ordered by profits
    data2 = data.sort_index(by='exit_profit')

    data_long = data2[data2['islong'] ] # Èç¹ûÊÇµ¥¸ù¿ªÆ½£¬ÇÒ¿ªÆ½¼ÛÒ»Ñù£¬ÄÇÃ´´Ë·¨²»³ÉÁ¢
    data_short = data2[data2['islong'] == False]

    exit_profit = data2['exit_profit']
    entry_best = pd.concat([data_long.high_profit, data_short.low_profit]).reindex(data2.index)
    entry_worst = pd.concat([data_long.low_profit, data_short.high_profit]).reindex(data2.index)
    try:
        entry_nbar_best = data2['entry_nbar_best']
        entry_nbar_worst = data2['entry_nbar_worst']
    except Exception as e:
        entry_nbar_best = []
        entry_nbar_worst = []
        

    return plot_entry(fig, exit_profit, entry_best, entry_worst, entry_nbar_best, entry_nbar_worst, n)


def exit_analyze(fig, data, n):
    '''³ö³¡ÐÅÏ¢Í¼''' 
    # ordered by profits
    data2 = data.sort_index(by='exit_profit')
    exit_profit = data2['exit_profit']
    try:
        exit_nbar_best = data2['exit_nbar_best']
        exit_nbar_worst = data2['exit_nbar_worst']
        profits_more = exit_nbar_best - exit_profit
        risks = exit_nbar_worst - exit_profit
        return  plot_exit(fig, exit_profit, exit_nbar_best, exit_nbar_worst, profits_more, risks, n)
    except Exception as e:
        return [], []


def scatter_analyze(fig, data):
    '''½»Ò×·Ö²¼Äñî«Í¼''' 
    data_win = data[data.exit_profit>0]
    data_lose = data[data.exit_profit<0]
    return  stock_plot.plot_scatter(fig, data_win.period.tolist(), data_win.exit_profit.tolist(),
                            data_lose.period.tolist(),
                            data_lose.exit_profit.tolist(), 30)



# Entry analyze
def summary_analyze(fig, data, n, type_):
    six.print_("prepare plotting.." )

    cursors = []
    # ordered by profits
    data = data.sort_index(by='exit_profit')
    data_long = data[data['islong']] # Èç¹ûÊÇµ¥¸ù¿ªÆ½£¬ÇÒ¿ªÆ½¼ÛÒ»Ñù£¬ÄÇÃ´´Ë·¨²»³ÉÁ¢
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
    except Exception as e:
        entry_nbar_best = pd.Series()
        entry_nbar_worst = pd.Series()
        exit_nbar_best = pd.Series()
        exit_nbar_worst = pd.Series()
        profits_more = pd.Series()
        risks = pd.Series()
        six.print_("No nbar!" )
    rtns = data['return']
    data_win = data[data.exit_profit>0]
    data_lose = data[data.exit_profit<=0]
    six.print_("begin plotting.." )
    # summary
    #cursors.append(cursor)

    #fig, cursor = plot_summary2(rtns, entry_best, data_win, data_lose, exit_profit,exit_nbar_best, exit_nbar_worst, n)
    #cursors.append(cursor)
    if type_ == 1:
        return plot_summary(fig, exit_profit, entry_best, entry_worst, entry_nbar_best, entry_nbar_worst,
                                        exit_nbar_best, exit_nbar_worst, profits_more, risks, n)
    elif type_ == 2:
        return plot_summary2(fig, rtns, entry_best, data_win, data_lose, exit_profit,exit_nbar_best, exit_nbar_worst, n)

class AnalyzeFrame(object):
    """
    A slider representing a floating point range

    """
    def __init__(self, profile, n=10, intraday=False):
        """ """
        self.fig = plt.figure(facecolor='white')
        self.fig.canvas.set_window_title('future data analyze')
        self.nbar = n
        self.cursors = []
        self.data = process_data(n, intraday,
                    self.get_tradeinfo(profile), profile.data())
        #six.print_(self.data.columns)
        #six.print_(self.data[0:3])
        #assert False
        self.axes = []
        self.rax = plt.axes([0, 0.5, 0.08, 0.15])
        self.radio = RadioButtons(self.rax, ('scatter', 'summary', 'summary2',
                'entry', 'exit', 'simple'), active=0)
        self.update('scatter')
        self.radio.on_clicked(self.update)
        summary(self.data)


    def get_tradeinfo(self, profile):
        """docstring for fname""" 
        entry_datetime = []
        exit_datetime = []
        entry_price = []
        exit_price = []
        islong = []
        for deal in profile.deals():
            entry_datetime.append(deal.open_datetime)
            exit_datetime.append(deal.close_datetime)
            entry_price.append(deal.open_price)
            exit_price.append(deal.close_price)
            v = True if deal.direction == 1 else False
            islong.append(v)
        tradeinfo = pd.DataFrame({'entry_price': entry_price,
                'exit_datetime': exit_datetime,
                'exit_price': exit_price,
                'islong': islong
                },index=entry_datetime)
        return tradeinfo

    def update(self, op):
        for ax in self.axes:
            self.fig.delaxes(ax)
        for c in self.cursors:
            del c
        if op == "scatter":
            six.print_("scatter_analyze" )
            self.axes, self.cursors = scatter_analyze(self.fig, self.data)
        elif op == "summary":
            self.axes, self.cursors = summary_analyze(self.fig, self.data, self.nbar, 1)
        elif op == "summary2":
            self.axes, self.cursors = summary_analyze(self.fig, self.data, self.nbar, 2)
        elif op == "entry":
            six.print_("entry_analyze" )
            self.axes, self.cursors = entry_analyze(self.fig, self.data, self.nbar)
        elif op == "exit":
            six.print_("exit_analyze" )
            self.axes, self.cursors = exit_analyze(self.fig, self.data, self.nbar)
        elif op == "simple":
            self.axes, self.cursors = simple_entry_analyze(self.fig, self.data, self.nbar)
        #elif op == "hm":
            #axes, cursors = follow_entry_analyze(fig, data)
            #six.print_("hm" )
        self.fig.canvas.draw()


if __name__ == '__main__':
    a = AnalyzeFrame('_djtrend2_IF000' , 10, False)
    plt.show()
    six.print_("ok")

