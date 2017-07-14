# -*- coding: utf-8 -*-
import os
import pickle
import pandas as pd
from datetime import datetime, timedelta

from quantdigger.datasource.cache import CacheAbstract, LoadCacheException
from quantdigger.datasource.source import SourceWrapper


def _merge_data(arr):
    return pd.concat(arr)\
             .reset_index()\
             .drop_duplicates('datetime', keep='last')\
             .set_index('datetime').sort_index()


def _missing_range(delta, dt_start, dt_end, cached_start, cached_end):
    result = []
    if cached_start is not None:
        if dt_start is None or dt_start < cached_start:
            result.append((dt_start, cached_start - delta))
    if dt_end > cached_end:
        result.append((cached_end + delta, dt_end))
    return result


def _filter_by_datetime_range(data, start, end):
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


class LocalFsCache(CacheAbstract):
    '''本地文件系统缓存'''

    def __init__(self, base_path):
        self._base_path = base_path
        self._load_meta()

    def get_bars(self, pcontract, dt_start, dt_end):
        key = self._to_key(pcontract)
        dt_start = pd.to_datetime(dt_start)
        dt_end = pd.to_datetime(dt_end)
        try:
            cached_start, cached_end = self._meta[key]
            missing_range = _missing_range(
                pcontract.period.to_timedelta(),
                dt_start, dt_end, cached_start, cached_end)
            data = self._load_data_from_path(self._key_to_path(key))
            if missing_range:
                raise LoadCacheException(missing_range, data)
            data = _filter_by_datetime_range(data, dt_start, dt_end)
            return SourceWrapper(pcontract, data, len(data))
        except (KeyError, IOError):
            raise LoadCacheException([(dt_start, dt_end)])

    def save_data(self, missing_data, pcontract):
        key = self._to_key(pcontract)
        path = self._key_to_path(key)
        data_arr = map(lambda t: t.data, missing_data)
        try:
            old_data = self._load_data_from_path(path)
            data_arr.insert(0, old_data)
        except IOError:
            pass
        data = _merge_data(data_arr)
        self._save_data_to_path(data, path)
        self._update_meta(key, map(lambda t: (t.start, t.end), missing_data))
        self._save_meta()

    def _check_base_path(self):
        if not os.path.isdir(self._base_path):
            os.makedirs(self._base_path)

    def _load_data_from_path(self, path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

    def _save_data_to_path(self, data, path):
        self._check_base_path()
        data.to_csv(path)

    def _meta_path(self):
        return os.path.join(self._base_path, '_meta')

    def _load_meta(self):
        try:
            with open(self._meta_path(), 'rb') as f:
                self._meta = pickle.load(f)
        except IOError:
            self._meta = {}

    def _save_meta(self):
        self._check_base_path()
        with open(self._meta_path(), 'wb') as f:
            pickle.dump(self._meta, f, protocol=2)

    def _update_meta(self, key, range_lst):
        starts, ends = map(lambda t: list(t), zip(*range_lst))
        try:
            cached_start, cached_end = self._meta[key]
            starts.append(cached_start)
            ends.append(cached_end)
        except KeyError:
            pass
        new_start = None if any(map(lambda d: d is None, starts)) \
            else min(starts)
        new_end = max(ends)
        self._meta[key] = new_start, new_end

    def _to_key(self, pcontract):
        return str(pcontract)

    def _key_to_path(self, key):
        path = os.path.join(self._base_path, key + '.csv')
        return path
