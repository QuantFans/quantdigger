# -*- coding: gbk -*-
import pandas as pd
import numpy as np
import os
import datetime as dt

home = "D:\\stock\\" 

def set_dir(dname):
    '''docstring for set_dir''' 
    global home
    home = dname

def csv2frame(fname):
    ''' 读取CSV文件到DataFrame '''
    try:
        data = pd.read_csv(fname, index_col=0, parse_dates=True)
        data['islong'] = False if fname.endswith("_.csv") else True
    except Exception, e:
        print u"File \"%s\" doesn't exist!"%fname
        data = None
    assert data.index.is_unique
    return data

class Record(object):
    """Represents a record."""
    def __init__(self):
        self.entry_datetime = "" 
        self.entry_bar= None
        self.exit_bar = None
        self.entry_price = None
        self.exit_profit = None
        self.period = None
        self.low_profit = None
        # high since
        self.high_profit = None
        self.entry_nbar = []
        self.exit_nbar = []

    def is_long(self):
        '''docstring for is_long()''' 
        # 如果是单根开平，且开平价一样，那么此法不成立
        return self.high_profit > self.low_profit

    def __str__(self):
        '''docstring for __s''' 
        return "entry_datetime: %s\nentry_bar: %s\nPeriod: %s\nlow_profit: %s\nhigh_profit: %s\nEntryPrice: %s\nExitPrice: %s\nEntrynbar: %s\nExitnbar: %s\n"%(str(self.entry_datetime),str(self.entry_bar), str(self.period), str(self.low_profit), str(self.high_profit), str(self.entry_price), str(self.exit_profit), str(self.entry_nbar), str(self.exit_nbar))


def make_record(data, i):
    s = data.ix[i,:]
    entry_nbar = s['entry_0':'entry_N'].tolist()
    exit_nbar = s['exit_1':'exit_N'].tolist()
    entry_nbar.pop()
    exit_nbar.pop()
    rec = Record()
    rec.entry_datetime = data.index[i]
    rec.entry_bar= s['entry_bar'] 
    rec.exit_bar = s['entry_bar']+s['period']-1
    rec.entry_price = s['entry_price']
    rec.exit_profit = s['exit_profit']
    rec.period = s['period']
    rec.low_profit = s['low_profit']
    rec.high_profit = s['high_profit']
    rec.entry_nbar = entry_nbar
    rec.exit_nbar = exit_nbar
    return rec


def frame2records(data):
    '''docstring for frame2records(dat)''' 
    records = []
    NBAR = len(data.ix[0, 'entry_0':'entry_N'])-2
    for i in range(len(data)):
        rec = make_record(data, i)
        records.append(rec)
    return records


def load_records(fnames):
    '''docstring for load_records''' 
    data = pd.concat([csv2frame(fname) for fname in fnames])
    data = data.sort_index()
    return frame2records(data), data

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
                #print low
        return max(maxdiffs) if maxdiffs else 0
    else:
        for ith_price in nbarprice:
            if ith_price < low:
                low = ith_price
                high = -1000000
                #print low
            elif ith_price > high:
                high = ith_price
                maxdiffs.append(high-low)
        return max(maxdiffs) if maxdiffs else 0

def simple_deal_tradeinfo(tradeinfo, pricefname, n=10, intraday=False):
    print "Loaded File: %s" % pricefname
    PRICE = 'close' 
    data = pd.DataFrame(tradeinfo.ix[:,0:2])
    price_data = csv2frame(pricefname)
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
    for i in range(len(data)):
        startt = tradeinfo.index[i]
        startpos = price_data.index.searchsorted(startt)
        onetrade = tradeinfo.ix[i, :]
        # nbar 
        entry_begin = startpos
        if intraday:
            day_entry_end = price_data.index.searchsorted((pd.to_datetime(startt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            entry_end = min(startpos+n+1, day_entry_end)
        else:
            entry_end = startpos + n + 1
        entry_Nlist.append(entry_end - entry_begin)
        islongs.append(onetrade['islong'])
        if onetrade['islong']:
            entry_nbar_bests.append(price_data.ix[entry_begin: entry_end, PRICE].max() - onetrade['entry_price'])
            entry_nbar_worsts.append(price_data.ix[entry_begin: entry_end, PRICE].min() - onetrade['entry_price'])
        else:
            entry_nbar_bests.append(onetrade['entry_price'] - price_data.ix[entry_begin: entry_end, PRICE].min())
            entry_nbar_worsts.append(onetrade['entry_price'] - price_data.ix[entry_begin: entry_end, PRICE].max())

    data['entry_nbar_best'] = entry_nbar_bests
    data['entry_nbar_worst'] = entry_nbar_worsts
    data['islong'] = islongs
    data['entry_n'] = entry_Nlist
    print "Data Preprocessing Done!"
    data.to_csv("d:\\rst.csv")
    return data

def deal_tradeinfo(tradeinfo, pricefname, n=10, intraday=False):
    print "Loaded File: %s" % pricefname
    PRICE = 'close' 
    data = pd.DataFrame(tradeinfo.ix[:,0:2])
    price_data = csv2frame(pricefname)
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
        startt = tradeinfo.index[i]
        startpos = price_data.index.searchsorted(startt)
        endt = tradeinfo.ix[i, ['exit_datetime']][0]
        endpos = price_data.index.searchsorted(endt)
        tradingdf = price_data.truncate(before=tradeinfo.index[i], after = endt)

        onetrade = tradeinfo.ix[i, :]
        # high/low
        if len(tradingdf) > 1:
            hp = tradingdf.ix[:-1, :][PRICE].max()
            lp = tradingdf.ix[:-1, :][PRICE].min()
            t = tradingdf.ix[:-1, :][PRICE].tolist()
            t.append(float(onetrade['exit_price']))
            returns.append(max_return(t, onetrade['islong']))
        else:
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

        # nbar  todo
        entry_begin = startpos
        exit_begin = endpos + 1
        if intraday:
            day_entry_end = price_data.index.searchsorted((pd.to_datetime(startt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            day_exit_end = price_data.index.searchsorted((pd.to_datetime(endt)+dt.timedelta(days=1)).strftime("%Y-%m-%d"))
            entry_end = min(startpos+n+1, day_entry_end)
            exit_end = min(endpos+1+n, day_exit_end)
        else:
            entry_end = startpos + n + 1
            exit_end = endpos + 1 + n
        entry_Nlist.append(entry_end - entry_begin)
        exit_Nlist.append(exit_end - exit_begin)
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
    data['entry_n'] = entry_Nlist
    data['exit_n'] = exit_Nlist
    print "Data Preprocessing Done!"
    #data.to_csv("d:\\rst.csv")
    return data

def load_datas(n, intraday, *fnames):
    '''''' 
    def path_name(fname):
        return "".join([home, "trace\\", fname, ".csv" ])
    datas = []
    stock_dir=home + "stock_data\\"
        
    for fname in fnames:
        names = [path_name(fname)]
        name, ext =  os.path.splitext(os.path.basename(fname))
        name = os.path.dirname(fname) + name + "_" + ext
        names.append(path_name(name))

        tradeinfo = pd.concat([csv2frame(name) for name in names])
        tradeinfo = tradeinfo.sort_index()

        pricefname = pricefname_from_tradefname(name)
        pricefname = stock_dir + pricefname
        print "Loaded Files: ", names
        data = deal_tradeinfo(tradeinfo, pricefname, n, intraday)
        datas.append(data)
    return tuple(datas)

def load_tradeinfo(fname):
    '''''' 
    def path_name(fname):
        return "".join([home, "trace\\", fname, ".csv" ])
    stock_dir=home + "stock_data\\"
    names = [path_name(fname)]
    name, ext =  os.path.splitext(os.path.basename(fname))
    name = os.path.dirname(fname) + name + "_" + ext
    names.append(path_name(name))

    tradeinfo = pd.concat([csv2frame(name) for name in names])
    tradeinfo = tradeinfo.sort_index()

    print "Loaded Files: ", names
    return tradeinfo


def symbolfromtradefname(fname, prefixnum=2):
    '''docstring for symbolfromfname''' 
    return fname.split('_')[prefixnum]

def pricefname_from_tradefname(fname, prefixnum=2):
    '''docstring for pricefname_from_tradefname''' 
    return '_' + symbolfromtradefname(fname, prefixnum) + '.csv'

def simple_load_data(fname, n, intraday):
    entryinfo = pd.read_csv("%strace\\%s.csv"%(home, fname), index_col=0, parse_dates=True)
    assert entryinfo.index.is_unique

    print entryinfo
    #print entryinfo.islong
    print "Loaded File: %s"%home + fname + ".csv"
    pricefname = pricefname_from_tradefname(fname, 1)
    stock_dir= home + "stock_data\\"
    pricefname = stock_dir + pricefname
    return simple_deal_tradeinfo(entryinfo, pricefname, n, intraday)

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
        return "".join([home, "trace\\", fname,"_trade_wave.txt"]), "".join([home, "trace\\", fname, "_wave.txt"])

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
