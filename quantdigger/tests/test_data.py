# -*- coding: utf-8 -*-
import pandas as pd
import os
import unittest

class TestDataSource(unittest.TestCase):
    def test_local_data(self):
        from quantdigger.datasource.data import LocalData
        from quantdigger.util import  pcontract
        """ 测试本地数据接口 """ 
        db = LocalData()
        target = db.load_data(pcontract('BB.SHFE', '1.Minute'))

        fname = os.path.join(os.getcwd(), 'data', 'CC.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates='datetime', index_col='datetime')
        self.assertFalse(source.equals(target), '本地数据接口负测试失败！')
        fname = os.path.join(os.getcwd(), 'data', 'BB.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates='datetime', index_col='datetime')
        self.assertTrue(source.equals(target), '本地数据接口正测试失败！')

if __name__ == '__main__':
    unittest.main()
