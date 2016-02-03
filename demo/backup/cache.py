# -*- coding: utf-8 -*-

import os
import pickle
import pandas as pd
from datetime import datetime, timedelta

_ONE_DAY = timedelta(days=1)

def _process_dt_start(dt_start):
    return pd.to_datetime(dt_start)

def _process_dt_end(dt_end):
    today = pd.to_datetime(datetime.today().date())
    if dt_end is None:
        return today
    else:
        return min(pd.to_datetime(dt_end), today)


class CachedDatasource(object):
    '''
    带缓存的数据源
    '''

    def __init__(self, datasource, cache):
        self.datasource = datasource
        self.cache = cache

    def load_data(self, pcontract, dt_start=None, dt_end=None):
        dt_start = _process_dt_start(dt_start)
        dt_end = _process_dt_end(dt_end)
        try:
            print 'trying to load from cache'
            return self.cache.load_data(pcontract, dt_start, dt_end)
        except CachedDatasource.LoadCacheException as e:
            print 'updating cache'
            if e.cached_data is None:
                missing_range = [(dt_start, dt_end)]
            else:
                missing_range = e.missing_range
            print 'missing range: %s' % missing_range
            missing_data = []
            for start, end in missing_range:
                data = self.datasource.load_data(pcontract, start, end)
                missing_data.append((data, start, end))
            self.cache.save_data(missing_data, pcontract)
            print 'loading cache'
            return self.cache.load_data(pcontract, dt_start, dt_end)

    class LoadCacheException(Exception):
        def __init__(self, cached_data=None, missing_range=None):
            assert(cached_data is None or missing_range)
            self.cached_data = cached_data
            self.missing_range = missing_range

#======

def _merge_data(arr):
    return pd.concat(arr).reset_index().drop_duplicates('datetime', take_last=True).set_index('datetime').sort()

def _missing_range(dt_start, dt_end, cached_start, cached_end):
    result = []
    if cached_start is not None:
        if dt_start is None or dt_start < cached_start:
            result.append((dt_start, cached_start - _ONE_DAY))
    if dt_end > cached_end:
        result.append((cached_end + _ONE_DAY, dt_end))
    return result

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
        try:
            cached_start, cached_end = self.meta[key]
            missing_range = _missing_range(dt_start, dt_end, cached_start, cached_end)
            data = self.__load_data_from_path(self.__key_to_path(key))
            if missing_range:
                raise CachedDatasource.LoadCacheException(data, missing_range)
            return _filter_by_datetime_range(data, dt_start, dt_end)
        except (KeyError, IOError):
            raise CachedDatasource.LoadCacheException()

    def save_data(self, missing_data, pcontract):
        key = self.__to_key(pcontract)
        path = self.__key_to_path(key)
        data_arr = map(lambda t: t[0], missing_data)
        try:
            old_data = self.__load_data_from_path(path)
            data_arr.insert(0, old_data)
        except IOError:
            pass
        data = _merge_data(data_arr)
        self.__save_data_to_path(data, path)
        self.__update_meta(key, map(lambda t: (t[1], t[2]), missing_data))
        self.__save_meta()

    def __check_base_path(self):
        if not os.path.isdir(self.base_path):
            os.makedirs(self.base_path)

    def __load_data_from_path(self, path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

    def __save_data_to_path(self, data, path):
        self.__check_base_path()
        data.to_csv(path)  # TODO: encoding?

    def __meta_path(self):
        return os.path.join(self.base_path, '_meta')

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

    def __update_meta(self, key, range_lst):
        starts, ends = map(lambda t: list(t), zip(*range_lst))
        try:
            cached_start, cached_end = self.meta[key]
            starts.append(cached_start)
            ends.append(cached_end)
        except KeyError:
            pass
        new_start = None if any(map(lambda d: d is None, starts)) else min(starts)
        new_end = max(ends)
        self.meta[key] = new_start, new_end

    def __to_key(self, pcontract):
        return pcontract.contract.exchange + pcontract.contract.code

    def __key_to_path(self, key):
        path = os.path.join(self.base_path, key + '.csv')
        return path
