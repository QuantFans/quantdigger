# -*- coding: utf-8 -*-
import pandas as pd

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
    return  dfout


price_data = pd.read_csv("2010-04-16.csv")
#df = price_data.rename(columns={0: 'datetime'})
#df = DataFrame(price_data, columns)

code_r = price_data[price_data.columns[0]]
datetime = price_data[price_data.columns[2]]
price = price_data[price_data.columns[3]]
volume = price_data[price_data.columns[4]]
total = price_data[price_data.columns[5]]
num_bi = price_data[price_data.columns[6]]
m_1 = price_data[price_data.columns[7]]
m_2 = price_data[price_data.columns[8]]
buy1 = price_data[price_data.columns[9]]
sell1 = price_data[price_data.columns[10]]
volume_buy1 = price_data[price_data.columns[11]]
volume_sell1 = price_data[price_data.columns[12]]

str_date = datetime[0].split(' ')[0]
moring_start = " ".join([str_date, '09:15:00'])
moring_end = " ".join([str_date, '11:30:00'])
afternoon_start = " ".join([str_date, '13:00:00'])
afternoon_end = " ".join([str_date, '15:15:00'])
#afternoon_end = " ".join(str_date, '15:00') # 交割日
datetime.loc[datetime < moring_start] = moring_start
datetime.loc[datetime > afternoon_end] = afternoon_end
newf = pd.DataFrame({'code': code_r, 
                    'price': price, 'volume': volume, 'turnover': total, 'num_deals': num_bi,    
                     'pe1': m_1, 'pe2': m_2, 'buy1': buy1, 'sell1': sell1, 'vbuy1': volume_buy1,
                     'vsell1': volume_sell1})
#  print pd.to_datetime(datetime)  # series
#  print pd.to_datetime(datetime.values)  # DatetimeIndex
newf.index = pd.to_datetime(datetime.values)
# 和set_major_locator一样，必定是等间隔的
#df3=newf['turnover'].resample('30T' ,how='sum',closed='right',label='right').dropna()
#df2=newf['volume'].resample('30T' ,how='sum',closed='right',label='right').dropna()
#df1=newf['price'].resample('30T' ,how='ohlc',closed='right',label='right').dropna()
df3=newf['turnover'].resample('30S' ,how='sum',closed='right',label='right').dropna()
df2=newf['volume'].resample('30S' ,how='sum',closed='right',label='right').dropna()
df1=newf['price'].resample('30S' ,how='ohlc',closed='right',label='right').dropna()
df1['turnover'] = df3
df1['volume'] = df2

#df2= df1.truncate(before=afternoon_start, after=afternoon_end) #remove non-trade time
#df3= df1.truncate(before=moring_start, after=moring_end) #remove non-trade time
#df1=df3.append(df2).fillna(0) #fill with 0 for period without valid deal

df1.to_csv("ok.csv", index=True, index_label='datetime',
             columns = ['open', 'close', 'high', 'low', 'volume', 'turnover'])
