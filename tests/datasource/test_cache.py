# -*- coding: utf-8 -*-

import pandas as pd
import shutil
import unittest

from quantdigger.infras.object import HashObject
from quantdigger.datasource.cache import CachedDatasource
from quantdigger.datasource.impl.localfs_cache import LocalFsCache
from quantdigger.datasource.source import DatasourceAbstract, SourceWrapper
from quantdigger.datastruct import PContract


class _MockSource(DatasourceAbstract):
    def __init__(self):
        self.log = []

    def get_bars(self, pcontract, dt_start, dt_end):
        self.log.append(HashObject.new(start=dt_start, end=dt_end))
        dt_start = pd.to_datetime(dt_start)
        dt_end = pd.to_datetime(dt_end)
        dt_curr = dt_start
        arr = []
        while dt_curr <= dt_end:
            arr.append({'datetime': dt_curr})
            dt_curr += pcontract.period.to_timedelta()
        data = pd.DataFrame([{'datetime': pd.to_datetime('2010-1-1')}])\
                 .set_index('datetime')
        return SourceWrapper(pcontract, data, len(data))


def dt_eq(dt1, dt2):
    return pd.to_datetime(dt1) == pd.to_datetime(dt2)


class TestCache(unittest.TestCase):

    CACHE_PATH = '_local_test_cache'

    def setUp(self):
        cache = LocalFsCache(TestCache.CACHE_PATH)
        self.src = _MockSource()
        self.ds = CachedDatasource(self.src, cache)
        self.pcontract = PContract.from_string('000001.SH-1.DAY')

    def tearDown(self):
        shutil.rmtree(TestCache.CACHE_PATH)

    def test1(self):
        self.ds.get_bars(self.pcontract, '2010-3-1', '2010-6-1')
        self.assertTrue(len(self.src.log) > 0, '没有访问数据源！')
        rec = self.src.log[-1]
        self.assertTrue(dt_eq(rec.start, '2010-3-1') and
                        dt_eq(rec.end, '2010-6-1'),
                        '访问的时间范围不正确！')
        self.src.log = []

        self.ds.get_bars(self.pcontract, '2010-3-1', '2010-6-1')
        self.assertTrue(len(self.src.log) == 0, '访问缓存失败！')

        self.ds.get_bars(self.pcontract, '2010-2-15', '2010-6-1')
        self.assertTrue(len(self.src.log) > 0 and
                        dt_eq(self.src.log[-1].start, '2010-2-15') and
                        dt_eq(self.src.log[-1].end, '2010-2-28'),
                        '访问数据源的时间范围不正确！')
        self.src.log = []

        self.ds.get_bars(self.pcontract, '2010-3-1', '2010-7-1')
        self.assertTrue(len(self.src.log) > 0 and
                        dt_eq(self.src.log[-1].start, '2010-6-2') and
                        dt_eq(self.src.log[-1].end, '2010-7-1'),
                        '访问数据源的时间范围不正确！')
        self.src.log = []

        # TODO: 两边


if __name__ == '__main__':
    unittest.main()
