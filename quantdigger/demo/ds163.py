# -*- coding: utf-8 -*-
# 从163获取数据的数据源

import io, urllib2
import pandas as pd

_FIELDS = [
    ('TCLOSE',       'close'),
    ('HIGH',         'high'),
    ('LOW',          'low'),
    ('TOPEN',        'open'),
    ('LCLOSE',       'lclose'),
    ('CHG',          'chg'),
    ('PCHG',         'pchg'),
    ('TURNOVER',     'turnover'),
    ('VOTURNOVER',   'volume'),
    ('VATURNOVER',   'vaturnover'),
    ('TCAP',         'tcap'),
    ('MCAP',         'mcap')]

_HOST = 'http://quotes.money.163.com/service/chddata.html'

def _dt_to_string(dt):
    return pd.to_datetime(dt).strftime('%Y%m%d')

def _query_data(code, dt_start, dt_end):
    qs = 'code=0' + code
    if dt_start is not None:
        qs += '&start=' + _dt_to_string(dt_start)
    if dt_end is not None:
        qs += '&end=' + _dt_to_string(dt_end)
    qs += '&fields=' + ';'.join(map(lambda i: i[0], _FIELDS))
    url = '%s?%s' % (_HOST, qs)
    return urllib2.urlopen(url).read()

def _post_process(content):
    buf = content.split('\n', 1)
    buf[0] = ','.join(['datetime', 'code', 'name'] + map(lambda i: i[1], _FIELDS))
    new_content = '\n'.join(buf)
    data = pd.read_csv(io.BytesIO(new_content), index_col=0, parse_dates=True)
    data = data[data.volume != 0]  # 过滤没有交易的交易日
    return data.iloc[::-1]  # reverse

class Stock163Source(object):
    def __init__(self):
        pass
    def load_data(self, pcontract, dt_start=None, dt_end=None):
        if pcontract.contract.exch_type != 'stock':
            # 只有股票数据
            return None
        content = _query_data(pcontract.contract.code, dt_start, dt_end)
        data = _post_process(content)
        assert data.index.is_unique
        return data

class CachedDataSource(object):
    def __init__(self, datasource, cache):
        self.datasource = datasource
        self.cache = cache
    def load_data(self, pcontract, dt_start=None, dt_end=None):
        if self.cache.has(pcontract, dt_start, dt_end):
            return self.cache.load_data(pcontract, dt_start, dt_end)
        else:
            data = self.datasource.load_data(pcontract, dt_start, dt_end)
            self.cache.save_data(data, pcontract, dt_start, dt_end)
            return data
# todo
