# -*- coding: utf-8 -*-

import pandas as pd
import tushare as ts
import cache as cc

# tsshare的get_h_data接口默认只取一年
# 所以这里使用一个很早的时间强制获取所有历史数据
_VERY_EARLY_START = '1988-12-12'

def _process_dt(dt):
    return str(pd.to_datetime(dt).date()) if dt else None

def _process_tushare_data(data):
    data.open = data.open.astype(float)
    data.close = data.close.astype(float)
    data.high = data.high.astype(float)
    data.low = data.low.astype(float)
    ## @todo bug: data.volume 里面有浮点值！
    data.volume = data.volume.astype(int)
    data.amount = data.amount.astype(float)
    data.index.names = ['datetime']
    data.index = pd.to_datetime(data.index)
    return data


class StockTsSource(object):
    '''tushare股票数据源'''
    def __init__(self):
        pass

    def load_data(self, pcontract, dt_start=None, dt_end=None):
        dt_start = _process_dt(dt_start)
        if not dt_start: dt_start = _VERY_EARLY_START
        dt_end = _process_dt(dt_end)
        data = ts.get_h_data(pcontract.contract.code,
                             start=dt_start, end=dt_end)
        return _process_tushare_data(data.iloc[::-1])


class CachedStockTsSource(cc.CachedDatasource):
    def __init__(self, base_path):
        datasource = StockTsSource()
        cache = cc.LocalFsCache(base_path)
        super(CachedStockTsSource, self).__init__(datasource, cache)
