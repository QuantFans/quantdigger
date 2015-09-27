# -*- coding: utf-8 -*-
# 从163获取数据的数据源

import io
import urllib2
import os
import pickle
import datetime
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
    '''163股票数据源'''
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
    '''带缓存的数据源'''
    def __init__(self, datasource, cache):
        self.datasource = datasource
        self.cache = cache

    def load_data(self, pcontract, dt_start=None, dt_end=None):
        try:
            print 'try loading from cache'
            return self.cache.load_data(pcontract, dt_start, dt_end)
        except CachedDataSource.LoadCacheFailed:
            print 'load from source'
            data = self.datasource.load_data(pcontract, dt_start, dt_end)
            # dt_end is None 的情况下可能会出现bug
            self.cache.save_data(data, pcontract, dt_start, dt_end)
            return data

    class LoadCacheFailed(Exception):
        pass


def _filter_by_datetime_range(data, start, end):
    # TODO: 先copy过来用，后面再抽象
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    if start is None:
        if end is None:
            return data
        else:
            return data[data.index <= end]
    else:
        if end is None:
            return data[data.index >= start]
        else:
            return data[(data.index >= start) & (data.index <= end)]


class LocalFsCache(object):
    '''
    本地文件系统缓存
    '''

    def __init__(self, base_path):
        self.base_path = base_path
        self.__load_meta()

    def load_data(self, pcontract, dt_start, dt_end):
        key = self.__to_key(pcontract)
        if self.__has(key, dt_start, dt_end):
            raise CachedDataSource.LoadCacheFailed()
        path = self.__key_to_path(key)
        try:
            data = self.__do_load_data(path)
            return _filter_by_datetime_range(data, dt_start, dt_end)
        except IOError:
            raise CachedDataSource.LoadCacheFailed()

    def save_data(self, data, pcontract, dt_start, dt_end):
        key = self.__to_key(pcontract)
        path = self.__key_to_path(key)
        try:
            old_data = self.__do_load_data(path)
            # 合并新旧数据
            data = pd.concat([old_data, data]).drop_duplicates(take_last=True)
        except IOError:
            pass
        self.__do_save_data(data, path)
        self.__update_meta(key, dt_start, dt_end)
        self.__save_meta()

    def __check_base_path(self):
        if not os.path.isdir(self.base_path):
            os.makedirs(self.base_path)

    def __se_to_datetime(self, dt_start, dt_end):
        dt_start = pd.to_datetime(dt_start)
        if dt_end is None:
            dt_end = pd.to_datetime(datetime.datetime.today().date())
        else:
            dt_end = pd.to_datetime(dt_end)
        return dt_start, dt_end

    def __load_meta(self):
        try:
            with open(self.__meta_path(), 'rb') as f:
                self.meta = pickle.load(f)
        except IOError:
            self.meta = {}

    def __save_meta(self):
        self.__check_base_path()
        with open(self.__meta_path(), 'wb') as f:
            pickle.dump(self.meta, f)

    def __meta_path(self):
        return os.path.join(self.base_path, '_meta')

    # __has和__update_meta或许该抽象一下
    def __do_with_meta_key(self, key, dt_start, dt_end, cb, keyerror_cb):
        try:
            start, end = self.meta[key]
            start = pd.to_datetime(start)
            end = pd.to_datetime(end)
            dt_start, dt_end = self.__se_to_datetime(dt_start, dt_end)
            return cb(self, key, dt_start, dt_end, start, end)
        except KeyError:
            return cb(self, key, dt_start, dt_end)

    def __has(self, key, dt_start, dt_end):
        def cb(s, key, dt_start, dt_end, start, end):
            return (start is None or dt_start is not None and dt_start >= start) and dt_end <= end
        def keyerror_cb(s, key, dt_start, dt_end):
            return False
        self.__do_with_meta_key(key, dt_start, dt_end, cb, keyerror_cb)

    def __update_meta(self, key, dt_start, dt_end):
        def cb(s, key, dt_start, dt_end, start, end):
            if dt_start is None or start is None:
                new_start = None
            else:
                new_start = min(dt_start, start)
            new_end = max(dt_end, end)
            s.meta[key] = new_start, new_end
        def keyerror_cb(s, key, dt_start, dt_end):
            s.meta[key] = dt_start, dt_end
        self.__do_with_meta_key(key, dt_start, dt_end, cb, keyerror_cb)

    def __do_load_data(self, path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

    def __do_save_data(self, data, path):
        self.__check_base_path()
        data.to_csv(path)  # TODO: encoding?

    def __to_key(self, pcontract):
        return pcontract.contract.exch_type + pcontract.contract.code

    def __key_to_path(self, key):
        path = os.path.join(self.base_path, key + '.csv')
        return path


class CachedStock163Source(CachedDataSource):
    def __init__(self, base_path):
        datasource = Stock163Source()
        cache = LocalFsCache(base_path)
        super(CachedStock163Source, self).__init__(datasource, cache)
