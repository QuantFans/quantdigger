# -*- coding: utf-8 -*-
# 从163获取数据的数据源

import io
import urllib2
import os
import pickle
import datetime
import pandas as pd

import cache as cc

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
    qs_part2 = ''
    if dt_start is not None:
        qs_part2 += '&start=' + _dt_to_string(dt_start)
    if dt_end is not None:
        qs_part2 += '&end=' + _dt_to_string(dt_end)
    qs_part2 += '&fields=' + ';'.join(map(lambda i: i[0], _FIELDS))
    for i in [0, 1]:
        qs_part1 = 'code=%s%s' % (i, code)
        url = '%s?%s' % (_HOST, qs_part1 + qs_part2)
        content = urllib2.urlopen(url).read()
        parts = content.split('\n', 1)
        if len(parts) < 2 or parts[1].strip() == '':
            continue
        return parts[0], parts[1]
    raise Exception('没有%s(%s ~ %s)的数据' % (code, dt_start, dt_end))

def _post_process(title, rows):
    new_title = ','.join(['datetime', 'code', 'name'] + map(lambda i: i[1], _FIELDS))
    new_content = '\n'.join([new_title, rows])
    data = pd.read_csv(io.BytesIO(new_content), index_col=0, parse_dates=True)
    data = data[data.volume != 0]  # 过滤没有交易的交易日
    return data.iloc[::-1]  # reverse


class Stock163Source(object):
    '''163股票数据源'''
    def __init__(self):
        pass

    def load_data(self, pcontract, dt_start=None, dt_end=None):
        if pcontract.contract.exch_type != 'stock':
            # 只有股票数据
            return None
        title, rows = _query_data(pcontract.contract.code, dt_start, dt_end)
        data = _post_process(title, rows)
        assert data.index.is_unique
        return data


class CachedStock163Source(cc.CachedDatasource):
    def __init__(self, base_path):
        datasource = Stock163Source()
        cache = cc.LocalFsCache(base_path)
        super(CachedStock163Source, self).__init__(datasource, cache)
