# -*- coding: utf-8 -*-
import pandas as pd
import os
import unittest
from logbook import Logger
from quantdigger import ConfigUtil
from quantdigger.datasource.data import DataManager

logger = Logger('test')
_DT_START = '1980-1-1'
_DT_END = '2100-1-1'


class TestSqliteSource(unittest.TestCase):
    def test_local_data2(self):
        old_source = ConfigUtil.get('source')
        if old_source == 'csv':
            return
        logger.info('***** 数据测试开始 *****')
        ConfigUtil.set(source='sqlite')
        data_manager = DataManager()
        target = data_manager.get_bars(
            'BB.TEST-1.Minute', _DT_START, _DT_END).data
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'CC.csv')
        source = pd.read_csv(
            fname, parse_dates='datetime', index_col='datetime')
        self.assertFalse(source.equals(target), '本地数据接口负测试失败！')
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'BB.csv')
        source = pd.read_csv(
            fname, parse_dates='datetime', index_col='datetime')
        self.assertTrue(source.equals(target), '本地数据接口正测试失败！')
        logger.info('-- 本地数据接口测试成功 --')
        logger.info('***** 数据测试结束 *****\n')
        ConfigUtil.set(source=old_source)


if __name__ == '__main__':
    unittest.main()
