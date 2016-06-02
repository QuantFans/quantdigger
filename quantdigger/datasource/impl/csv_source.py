# -*- coding: utf-8 -*-

import os
import pandas as pd

from quantdigger.datasource.dsutil import *
from quantdigger.datasource.source import SourceWrapper, DataSourceAbstract


@register_datasource('csv', 'data_path')
class CsvSource(DataSourceAbstract):
    '''CSV数据源'''

    def __init__(self, root):
        self._root = root

    def get_bars(self, pcontract, dt_start, dt_end):
        data = self._load_bars(pcontract)
        dt_start = pd.to_datetime(dt_start)
        dt_end = pd.to_datetime(dt_end)
        data = data[(dt_start <= data.index) & (data.index <= dt_end)]
        assert data.index.is_unique
        return SourceWrapper(pcontract, data, len(data))

    def get_last_bars(self, pcontract, n):
        data = self._load_bars(pcontract)
        data = data[-n:]
        assert data.index.is_unique
        return SourceWrapper(pcontract, data, len(data))

    def get_contracts(self):
        """ 获取所有合约的基本信息

        Returns:
            pd.DataFrame
        """
        fname = os.path.join(self._root, "CONTRACTS.csv")
        df = pd.read_csv(fname)
        df.index = df['code'] + '.' + df['exchange']
        df.index = map(lambda x: x.upper(), df.index)
        return df

    def _load_bars(self, pcontract):
        # TODO:  不要字符串转来转去的
        strpcon = str(pcontract).upper()
        contract, period = tuple(strpcon.split('-'))
        code, exch = tuple(contract.split('.'))
        period = period.replace('.', '')
        fname = os.path.join(self._root, period, exch, code + ".csv")
        try:
            data = pd.read_csv(fname, index_col=0, parse_dates=True)
        except IOError:
            raise FileDoesNotExist(file=fname)
        else:
            return data
