# -*- coding: utf-8 -*-

import os
import pandas as pd

from quantdigger.datasource.dsutil import *
from quantdigger.datasource.source import SourceWrapper, DatasourceAbstract
from quantdigger.errors import FileDoesNotExist


@register_datasource('csv', 'data_path')
class CsvSource(DatasourceAbstract):
    '''CSV数据源'''

    def __init__(self, root):
        self._root = root

    def get_bars(self, pcontract, dt_start, dt_end):
        data = self._load_bars(pcontract)
        dt_start = pd.to_datetime(dt_start)
        dt_end = pd.to_datetime(dt_end)
        data = data[(dt_start <= data.index) & (data.index <= dt_end)]
        assert data.index.is_unique
        return data

    def get_last_bars(self, pcontract, n):
        data = self._load_bars(pcontract)
        data = data[-n:]
        assert data.index.is_unique
        return data

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

    def import_bars(self, tbdata, pcontract):
        """ 导入交易数据

        Args:
            tbdata (dict): {'datetime', 'open', 'close',
                            'high', 'low', 'volume'}
            pcontract (PContract): 周期合约
        """
        strpcon = str(pcontract).upper()
        contract, period = tuple(strpcon.split('-'))
        code, exch = tuple(contract.split('.'))
        period = period.replace('.', '')
        try:
            os.makedirs(os.path.join(self._root, period, exch))
        except OSError:
            pass
        fname = os.path.join(self._root, period, exch, code+'.csv')
        df = pd.DataFrame(tbdata)
        df.to_csv(fname, columns=[
            'datetime', 'open', 'close', 'high', 'low', 'volume'
        ], index=False)

    def import_contracts(self, data):
        """ 导入合约的基本信息。

        Args:
            data (dict): {key, code, exchange, name, spell,
            long_margin_ratio, short_margin_ratio, price_tick, volume_multiple}

        """
        fname = os.path.join(self._root, "CONTRACTS.csv")
        df = pd.DataFrame(data)
        df.to_csv(fname, columns=[
            'code', 'exchange', 'name', 'spell',
            'long_margin_ratio', 'short_margin_ratio', 'price_tick',
            'volume_multiple'
        ], index=False)

    def get_code2strpcon(self):
        symbols = {}  # code -> string pcontracts, 所有周期
        period_exchange2strpcon = {}  # exchange.period -> string pcontracts , 所有合约
        for parent, dirs, files in os.walk(self._root):
            if dirs == []:
                t = parent.split(os.sep)
                period, exch = t[-2], t[-1]
                for i, a in enumerate(period):
                    if not a.isdigit():
                        sepi = i
                        break
                count = period[0:sepi]
                unit = period[sepi:]
                period = '.'.join([count, unit])
                strpcons = period_exchange2strpcon.setdefault(
                    ''.join([exch, '-', period]), [])
                for file_ in files:
                    if file_.endswith('csv'):
                        code = file_.split('.')[0]
                        t = symbols.setdefault(code, [])
                        rst = ''.join([code, '.', exch, '-', period])
                        t.append(rst)
                        strpcons.append(rst)
        return symbols, period_exchange2strpcon
