# -*- coding: utf-8 -*-
import os

import pandas as pd


def process_file(path, fname, period):
    price_data = pd.read_csv(fname)
    #df = price_data.rename(columns={0: 'datetime'})
    #df = DataFrame(price_data, columns)

    code_r = price_data[price_data.columns[0]]
    datetime = price_data[price_data.columns[2]]
    price = price_data[price_data.columns[3]]
    volume = price_data[price_data.columns[4]]
    total = price_data[price_data.columns[5]]
    num_bi = price_data[price_data.columns[6]]
    #m_1 = price_data[price_data.columns[7]]
    #m_2 = price_data[price_data.columns[8]]
    #buy1 = price_data[price_data.columns[9]]
    #sell1 = price_data[price_data.columns[10]]
    #volume_buy1 = price_data[price_data.columns[11]]
    #volume_sell1 = price_data[price_data.columns[12]]

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
                         })
    #  print pd.to_datetime(datetime)  # series
    #  print pd.to_datetime(datetime.values)  # DatetimeIndex
    newf.index = pd.to_datetime(datetime.values)
    # 和set_major_locator一样，必定是等间隔的
    df1 = newf['price'].resample(period, how = 'ohlc', closed = 'right', label = 'right')
    df3 = newf['turnover'].resample(period, how = 'sum', closed = 'right', label = 'right')
    df2 = newf['volume'].resample(period, how = 'sum', closed = 'right', label = 'right')
    df1['turnover'] = df3
    df1['volume'] = df2

   

    filepath = path + os.sep + "new_" + period + "_" + file
    df1.to_csv(filepath, index=True, index_label='datetime',
                 columns = ['open', 'close', 'high', 'low', 'volume', 'turnover'])

for path, dirs, files in os.walk(os.getcwd()):
    for file in files:
        #print os.path.join(path, file)
        filepath = path + os.sep + file
        if filepath.endswith(".csv"):
            process_file(path, file,  '1S')
            process_file(path, file, '5S')
            process_file(path, file, '20S')
