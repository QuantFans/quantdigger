# -*- coding: utf-8 -*-
import six
from six.moves import range
import datetime
import os
import time
import pandas as pd
from quantdigger.errors import ArgumentError


def csv2frame(fname):
    return pd.read_csv(fname, index_col=0, parse_dates=True)


def tick2period(code, period, start, end):
    """ get tick data from tushare and resample to certain period data
    selected by input: period
    """
    import tushare as ts
    import numpy as np
    import pandas as pd
    dfout = None
    # get valid trade date
    valid_dates = ts.get_hist_data(code, start=start, end=end).index
    for date in valid_dates:
        # setup trade time grid by period selected
        # date=date.strftime('%Y-%m-%d')
        rng = pd.date_range(date+' 9:30:00', date+' 15:00',
                            closed='right', freq=period)
        sr = pd.Series(np.nan, index=rng)
        df = ts.get_tick_data(code, date=date)

        # process open call auction
        df.loc[df.time < '09:30:00', 'time'] = '09:30:01'
        # process close call auction
        df.loc[df.time > '15:00:00', 'time'] = '14:59:59'

        df['time'] = date + ' ' + df['time']
        df = df.rename(columns={'time': 'datetime'})
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index('datetime').sort()
        df2 = df['volume'].resample(period, how='sum', closed='right',
                                    label='right')
        # align to standard time
        df2, dummy = df2.align(sr, axis=0)
        df3 = df2.truncate(before=date+' 13:00:01', after=date+' 15:00')
        # remove non-trade time
        df2 = df2.truncate(before=date+' 9:30:01', after=date+' 11:30')
        # fill with 0 for period without valid deal
        df2 = df2.append(df3).fillna(0)
        df1 = df['price'].resample(period, how='ohlc', closed='right',
                                   label='right')
        # align to standard time
        df1, dummy = df1.align(sr, axis=0)
        df3 = df1.truncate(before=date+' 13:00:01', after=date+' 15:00')
        # remove non-trade time
        df1 = df1.truncate(before=date+' 9:30:01', after=date+' 11:30')
        df1 = df1.append(df3)
        if np.isnan(df1.loc[0, 'close']):
            # use last day's close as initial price if
            # there is no deal after open
            from datetime import timedelta
            # get enough days to ensure at least one trading day is involved
            aDay = timedelta(days=-10)
            pre = (pd.to_datetime(date) + aDay).strftime('%Y-%m-%d')
            df1.loc[0, 'close'] = ts.get_hist_data(code, start=pre, end=date)\
                                   .loc[-2, 'close']
        # use price before if there is no deal during current period
        df1['close'].fillna(method='pad', inplace=True)
        # use close as open,high,low if there  is no deal during current period
        df1.fillna(method='bfill', inplace=True, axis=1)
        df1['volume'] = df2.values
        dfout = pd.concat([dfout, df1])
    # six.print_(dfout)
    # assert(False)
    return dfout


def encode2id(period, dt):
    """ 把周期和时间编码成13位的整数id

    Args:
        period (Period): 周期
        dt (datetime): 时间戳

    Returns:
        int. id
    """
    db_period = {
            '5.SECOND': '155',
            '3.SECOND': '153',
            '1.MINUTE': '101',
            '3.MINUTE': '102',
            '5.MINUTE': '103',
            '10.MINUTE': '104',
            '15.MINUTE': '105',
            '30.MINUTE': '106',
            '1.HOUR': '107',
            '1.DAY': '108',
            '1.WEEK': '109',
            '1.MONTH': '110',
            '1.SEASON': '111',
            '1.YEAR': '112'
            }
    # 确保13位
    strperiod = str(period)
    if strperiod not in db_period:
        raise Exception("错误类型")
    utime = int(time.mktime(dt.timetuple())*1000)
    id = str(utime)
    count = 13 - len(id)
    for i in range(0, count):
        id = '0' + id
    try:
        return int(db_period[strperiod] + id), utime
    except KeyError:
        raise ArgumentError()


def import_tdx_stock(path, ld):
    """ 导入通达信的股票数据

    Args:
        path (str): 数据文件夹
        ld (LocalData): 本地数据库对象
    """
    from datetime import datetime, timedelta
    from quantdigger.util import ProgressBar
    for path, dirs, files in os.walk(path):
        progressbar = ProgressBar(total=len(files))
        for file_ in files:
            filepath = path + os.sep + file_
            if filepath.endswith(".txt"):
                with open(filepath) as f:
                    lines = f.readlines()
                    data = {
                        'datetime': [],
                        'open': [],
                        'high': [],
                        'low': [],
                        'close': [],
                        'volume': [],
                        'turnover': []
                    }

                    for ln in lines[2:-1]:
                        ln = ln.rstrip('\r\n').split('\t')
                        ln[0] = datetime.strptime(ln[0], "%Y/%m/%d") + \
                            timedelta(hours=15)
                        for i in range(1, len(ln)):
                            ln[i] = float(ln[i])
                        data['datetime'].append(ln[0])
                        data['open'].append(ln[1])
                        data['high'].append(ln[2])
                        data['low'].append(ln[3])
                        data['close'].append(ln[4])
                        data['volume'].append(ln[5])
                        data['turnover'].append(ln[6])
                    t = file_.split('#')
                    exch = t[0]
                    code = t[1].split('.')[0]
                    strpcon = "".join([code, '.', exch, '-', '1.Day'])
                    ld.import_bars(data, strpcon)
            progressbar.move()
            progressbar.log('')
    return


def import_from_csv(self, paths):
    """ 批量导入特定路径下规定格式的csv文件到系统。 """
    for path in paths:
        if not path.endswith(".csv") and not path.endswith(".CSV"):
            # @TODO
            six.print_(path)
            raise Exception("错误的文件格式")
        six.print_("import: ", path)
        df = pd.read_csv(path, parse_dates='datetime')
        try:
            df['datetime'] = map(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
                df['datetime'])
        except ValueError:
            df['datetime'] = map(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"),
                df['datetime'])
        fname = path.split(os.path.sep)[-1]

        tbname = fname.split('-')[0].split('.')
        strdt = fname.split('-')[1].rstrip('.csv').rstrip('.CSV')
        tbname = "_".join([tbname[1], tbname[0]])
        self.import_bars(df, tbname, strdt)


def import_data(fpaths, ds):
    """ 批量导入特定路径下规定格式的csv文件到系统。
    """
    # TODO: 更通用的导入
    for path in fpaths:
        if not path.lower().endswith('.csv'):
            # @TODO
            six.print_(path)
            raise Exception("错误的文件格式")
        six.print_("import data: ", path)
        df = pd.read_csv(path, parse_dates='datetime')
        try:
            df['datetime'] = map(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
                df['datetime'])
        except ValueError:
            df['datetime'] = map(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"),
                df['datetime'])
        strpcon = path.split(os.path.sep)[-1].rstrip('.csv')
        ds.import_bars(df, strpcon)


__all__ = ['csv2frame', 'encode2id', 'tick2period',
           'import_data', 'import_tdx_stock']
