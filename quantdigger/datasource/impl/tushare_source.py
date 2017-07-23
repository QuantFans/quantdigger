# -*- coding: utf-8 -*-

import pandas as pd
import tushare as ts

from quantdigger.datasource.cache import CachedDatasource
from quantdigger.datasource.dsutil import register_datasource
from quantdigger.datasource.source import SourceWrapper, DatasourceAbstract
from quantdigger.datasource.impl.localfs_cache import LocalFsCache


def _process_ts_dt(dt):
    return str(pd.to_datetime(dt))


@register_datasource('tushare')
class TuShareSource(DatasourceAbstract):
    '''TuShare数据源'''

    def __init__(self):
        pass

    def get_bars(self, pcontract, dt_start, dt_end):
        # TODO: 判断pcontract是不是股票，或者tushare支持期货？
        data = self._load_data(pcontract.contract.code, dt_start, dt_end)
        assert data.index.is_unique
        return SourceWrapper(pcontract, data, len(data))

    def get_last_bars(self, pcontract, n):
        # TODO
        pass

    def _load_data(self, code, dt_start, dt_end):
        dts = _process_ts_dt(dt_start)
        dte = _process_ts_dt(dt_end)
        data = ts.get_k_data(code, start=dts, end=dte)
        data.set_index('date',drop=True,inplace=True)
        data.index.names = ['datetime']
        return data.iloc[::-1]

    def get_contracts(self):
        # TODO
        return pd.DataFrame()


@register_datasource('cached-tushare', 'cache_path')
def CachedTuShareSource(cache_path):
    return CachedDatasource(TuShareSource(), LocalFsCache(cache_path))
