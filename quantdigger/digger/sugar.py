# -*- coding: utf-8 -*-

import six
from six.moves import range
import pandas as pd
import os
import datetime as dt


def max_return(nbarprice, islong):
    '''  ''' 
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


def process_signal(signal, price_data, n=10, intraday=False):
    ## @todo split function
    PRICE = 'close' 
    data = pd.DataFrame(signal)
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
    entry_Nlist = []
    exit_Nlist = []
    for i in range(len(data)):
        startt = signal.index[i]
        startpos = price_data.index.searchsorted(startt)
        endt = signal.loc[i, ['exit_datetime']][0]
        endpos = price_data.index.searchsorted(endt)
        tradingdf = price_data.truncate(before=startt, after = endt) # 当笔交易间的价格数据

        onetrade = signal.loc[i, :]
        # high/low
        if len(tradingdf) > 1:
            hp = tradingdf.loc[:-1, :][PRICE].max()
            lp = tradingdf.loc[:-1, :][PRICE].min()
            t = tradingdf.loc[:-1, :][PRICE].tolist()
            t.append(float(onetrade['exit_price']))
            returns.append(max_return(t, onetrade['islong'])) # 当笔交易区间内的最大回测
        else:
            hp = tradingdf.loc[:, :][PRICE].max()
            lp = tradingdf.loc[:, :][PRICE].min()
            if onetrade['islong']:
                returns.append(max(onetrade['entry_price']-onetrade['exit_price'], 0))  # 同一根bar上买和卖
            else:
                returns.append(max(onetrade['exit_price']-onetrade['entry_price'], 0))
        hp = onetrade['exit_price'] if onetrade['exit_price'] > hp else hp # 算入交易价格
        hp = onetrade['entry_price'] if onetrade['entry_price'] > hp else hp
        lp = onetrade['exit_price'] if onetrade['exit_price'] < lp else lp
        lp = onetrade['entry_price'] if onetrade['entry_price'] < lp else lp
        hp = hp - onetrade['entry_price']
        lp = lp - onetrade['entry_price']
        high_profits.append(hp if onetrade['islong'] else 0-hp)  # 理论最高利润
        low_profits.append(lp if onetrade['islong'] else 0-lp)   # 理论最低利润
        # exit
        ep = onetrade['exit_price'] - onetrade['entry_price']
        exit_profits.append(ep if onetrade['islong'] else 0-ep)  # 实际利润
        # period
        periods.append(endpos - startpos + 1)        # 持仓周期

        # 入场或出场后n根bar的最优和最差收益
        entry_begin = startpos
        exit_begin = endpos + 1
        if intraday:
            day_entry_end = price_data.index.searchsorted((pd.to_datetime(startt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            day_exit_end = price_data.index.searchsorted((pd.to_datetime(endt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            # 不隔夜
            entry_end = min(startpos+n+1, day_entry_end)
            exit_end = min(endpos+1+n, day_exit_end)
        else:
            entry_end = startpos + n + 1
            exit_end = endpos + 1 + n
        entry_Nlist.append(entry_end - entry_begin)
        exit_Nlist.append(exit_end - exit_begin)
        islongs.append(onetrade['islong'])

        position_prices = price_data.loc[entry_begin: entry_end, PRICE]
        exit_prices = price_data.loc[exit_begin: exit_end, PRICE]
        if onetrade['islong']:
            entry_nbar_bests.append(position_prices.max() - onetrade['entry_price'])
            entry_nbar_worsts.append(position_prices.min() - onetrade['entry_price'])
            exit_nbar_bests.append(exit_prices.max() - onetrade['entry_price'])
            exit_nbar_worsts.append(exit_prices.min() - onetrade['entry_price'])
        else:
            entry_nbar_bests.append(onetrade['entry_price'] - position_prices.min())
            entry_nbar_worsts.append(onetrade['entry_price'] - position_prices.max())
            exit_nbar_bests.append(onetrade['entry_price'] - exit_prices.min())
            exit_nbar_worsts.append(onetrade['entry_price'] - exit_prices.max())

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
    data['entry_n'] = entry_Nlist
    data['exit_n'] = exit_Nlist
    six.print_("Data Preprocessing Done!")
    return data


def load_datas(n, intraday, signal_fname, price_fname):
    # 一次可加载多个数据

    signal = pd.read_csv(signal_fname, index_col=0, parse_dates=True).sort_index()
    price_data = pd.read_csv(price_fname, index_col=0, parse_dates=True).sort_index()
    return process_signal(signal, price_data, n, intraday)
    #six.print_(data)
    #assert(False)


def load_wavedata(*fnames):
    '''
        dj1, dj2 = load_wavedata("namea", "nameb")
        djx --- (wave, wave_r_entry)
        return: 
            ((wave_timestamp, DataFrame('pre','after')))
    '''
    def fnameparse(fname):
        '''
        return entry_wave_info and wave
        ''' 
        home = os.getcwd() + "/data/" 
        return "".join([home, "trace/", fname,"_trade_wave.txt"]), "".join([home, "trace/", fname, "_wave.txt"])

    def process_session(data):
        '''''' 
        index = data[0]
        pre_en_wave = []
        after_en_wave = []
        ispre = True
        for line in data[1:]:
            issep = line.startswith("=")
            if ispre and not issep:
                pre_en_wave.append(line)
            if issep:
                ispre = False
            if not ispre and not issep:
                after_en_wave.append(line)
        return [index, pre_en_wave, after_en_wave]

    rst = []
    for fname in fnames:
        # code...
        tw_name, w_name = fnameparse(fname)
        wave_ts = []
        ses = []
        entroinfo = []
        for line in open(w_name):
            wave_ts.append(line.rstrip("\n"))
        for line in open(tw_name):
            line = line.rstrip("\n")
            ses.append(line)
            if line.startswith('-'):
                # session begin
                ses.pop()
                if ses:
                    entroinfo.append(process_session(ses))
                ses = []
        entroinfo.append(process_session(ses))
        d = zip(*entroinfo)
    rst.append((wave_ts, pd.DataFrame({'pre':d[1], 'after':d[2]}, index=d[0])))
    return tuple(rst)
