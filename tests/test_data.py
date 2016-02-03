# -*- coding: utf-8 -*-
import pandas as pd
import os
import unittest
from logbook import Logger
logger = Logger('test')
from quantdigger import locd, set_config

class TestDataSource(unittest.TestCase):

    def test_local_data(self):
        old_source = locd.source
        if old_source == 'sqlite':
            return 
        logger.info('***** 数据测试开始 *****')
        set_config({ 'source': 'csv' })
        target = locd.get_data('BB.TEST-1.Minute')
        fname = os.path.join(os.getcwd(), 'data', 'CC.TEST-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates='datetime', index_col='datetime')
        self.assertFalse(source.equals(target), '本地数据接口负测试失败！')
        fname = os.path.join(os.getcwd(), 'data', 'BB.TEST-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates='datetime', index_col='datetime')
        self.assertTrue(source.equals(target), '本地数据接口正测试失败！')
        logger.info('-- 本地数据接口测试成功 --')
        logger.info('***** 数据测试结束 *****\n')
        set_config({ 'source': old_source })

    def test_local_data2(self):
        old_source = locd.source
        if old_source == 'csv':
            return 
        logger.info('***** 数据测试开始 *****')
        set_config({ 'source': 'sqlite' })
        self.assertTrue(locd.source == 'sqlite')

        target = locd.get_data('BB.TEST-1.Minute')
        fname = os.path.join(os.getcwd(), 'data', 'CC.TEST-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates='datetime', index_col='datetime')
        self.assertFalse(source.equals(target), '本地数据接口负测试失败！')

        fname = os.path.join(os.getcwd(), 'data', 'BB.TEST-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates='datetime', index_col='datetime')
        self.assertTrue(source.equals(target), '本地数据接口正测试失败！')
        logger.info('-- 本地数据接口测试成功 --')
        logger.info('***** 数据测试结束 *****\n')
        # 恢复默认值避免影响其它测试
        set_config({ 'source': old_source })




if __name__ == '__main__':
    unittest.main()
