# -*- coding: utf-8 -*-

import time
import pandas as pd
from quantdigger.errors import ArgumentError

def csv2frame(fname):
    return pd.read_csv(fname, index_col=0, parse_dates=True)

def tick2period(code,period,start,end):
    """ get tick data from tushare and resample to certain period data
    selected by input: period
    """
    import tushare as ts
    import numpy as np
    import pandas as pd
    dfout=None
    #get valid trade date
    valid_dates=ts.get_hist_data(code,start=start,end=end).index
    for date in valid_dates:
        #date=date.strftime('%Y-%m-%d')
        rng=pd.date_range(date+' 9:30:00',date+' 15:00',closed='right',freq=period) #setup trade time grid by period selected
        sr = pd.Series(np.nan, index=rng)
        df = ts.get_tick_data(code,date=date)

        df.loc[df.time<'09:30:00','time']='09:30:01' #process open call auction
        df.loc[df.time>'15:00:00','time']='14:59:59' #process close call auction

        df['time'] = date + ' ' + df['time']
        df = df.rename(columns={'time': 'datetime'})
        df['datetime']=pd.to_datetime(df['datetime'])
        df = df.set_index('datetime').sort()
        df2=df['volume'].resample(period,how='sum',closed='right',label='right')
        df2,dummy=df2.align(sr,axis=0) #align to standard time
        df3=df2.truncate(before=date+' 13:00:01', after=date+' 15:00')
        df2= df2.truncate(before=date+' 9:30:01', after=date+' 11:30') #remove non-trade time
        df2=df2.append(df3).fillna(0) #fill with 0 for period without valid deal
        df1=df['price'].resample(period,how='ohlc',closed='right',label='right')
        df1,dummy=df1.align(sr,axis=0) #align to standard time
        df3=df1.truncate(before=date+' 13:00:01', after=date+' 15:00')
        df1= df1.truncate(before=date+' 9:30:01', after=date+' 11:30') #remove non-trade time
        df1=df1.append(df3)
        if np.isnan(df1.ix[0,'close']): #use last day's close as initial price if there is no deal after open
            from datetime import timedelta
            aDay = timedelta(days=-10)  #get enough days to ensure at least one trading day is involved
            pre  = (pd.to_datetime(date) + aDay).strftime('%Y-%m-%d')
            df1.ix[0,'close'] = ts.get_hist_data(code,start=pre,end=date).ix[-2,'close']
        df1['close'].fillna(method='pad',inplace=True) #use price before if there is no deal during current period
        df1.fillna(method='bfill',inplace=True,axis=1) #use close as open,high,low if there  is no deal during current period
        df1['volume']=df2.values
        dfout=pd.concat([dfout,df1])
    #print dfout
    #assert(False)
    return  dfout


def encode2id(period, dt):
    """ 把周期和时间编码成13位的整数id
    
    Args:
        period (Period): 周期

        dt (datetime): 时间戳 
    
    Returns:
        int. id
    """
    # 确保13位
    st = str(int(time.mktime(dt.timetuple())*1000))
    count = 13 - len(st)
    for i in range(0, count):
        st = '0' + st
    prefix = {
            '1.Minute': '101',
            '3.Minute': '102',
            '5.Minute': '103',
            '10.Minute': '104',
            '15.Minute': '105',
            '30.Minute': '106',
            '1.Hour': '107',
            '1.Day': '108',
            '1.Week': '109',
            '1.Month': '110',
            '1.Season': '111',
            '1.Year': '112'
            }
    try:
        return int(prefix[str(period)] + st)
    except KeyError:
        raise ArgumentError()
