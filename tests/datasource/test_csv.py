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


class TestCsvSource(unittest.TestCase):

    def test_csv_source(self):
        source_bak = ConfigUtil.get('source')
        logger.info('***** 数据测试开始 *****')
        ConfigUtil.set(source='csv')
        data_manager = DataManager()
        target = data_manager.get_bars(
            'BB.TEST-1.Minute', _DT_START, _DT_END).data
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'CC.csv')
        logger.info('-- CSV数据路径: ' + fname + ' --')
        source = pd.read_csv(
            fname, parse_dates=['datetime'], index_col='datetime')
        self.assertFalse(source.equals(target), '本地数据接口负测试失败！')
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'BB.csv')
        source = pd.read_csv(
            fname, parse_dates=['datetime'], index_col='datetime')
        self.assertTrue(source.equals(target), '本地数据接口正测试失败！')
        logger.info('-- 本地数据接口测试成功 --')
        ConfigUtil.set(source=source_bak)
        logger.info('***** 数据测试结束 *****\n')


if __name__ == '__main__':
    unittest.main()
