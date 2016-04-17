# -*- coding: utf-8 -*-
##
# @file data.py
# @brief 本地数据，远程数据，数据控制模块
# @author wondereamer
# @version 0.2
# @date 2015-12-09

from datetime import datetime
import os
import pandas as pd
from quantdigger.errors import FileDoesNotExist
from quantdigger.datasource.source import CsvSource, SqlLiteSource, MongoSource
from quantdigger.datasource.datautil import tick2period
from quantdigger.datastruct import PContract, Contract


class QuoteCache(object):
    def __init__(self, arg):
        pass


class LocalData(object):
    """
    本地数据代理根据配置决定数据源的类型, 比如sqlite, csv, pytable

    :ivar source: 数据源名称
    """
    def __init__(self):
        """
        """
        self._src = None
        self.source = ''

    def get_code2strpcon(self):
        return self._src.get_code2strpcon()

    def set_source(self, settings):
        if settings['source'] == 'sqlite':
            try:
                import sqlite3
                path = os.path.join(settings['data_path'], 'digger.db')
                self._src = SqlLiteSource(path)
            except sqlite3.OperationalError:
                raise FileDoesNotExist(file=path)
        elif settings['source'] == 'mongodb':
            self._src = MongoSource() # TODO: address, port
        elif settings['source'] == 'csv':
            self._src = CsvSource(settings['data_path'])
        try:
            Contract.info = self.get_contracts()
        except Exception, e:
            # @TODO
            pass
        self.source = settings['source']

    def get_bars(self, strpcon, dt_start, dt_end):
        """ 获取本地历史数

        Args:
            strpcon (str): 周期合约
            dt_start (datetime): 数据的开始时间
            dt_end (datetime): 数据的结束时间

        Returns:
            SourceWrapper. 数据
        """
        pcontract = PContract.from_string(strpcon)
        return self._src.get_bars(pcontract, dt_start, dt_end)

    def get_last_bars(self, strpcon, n):
        pcontract = PContract.from_string(strpcon)
        return self._src.get_last_bars(pcontract, n)

    def get_data(self, pcontract, dt_start="1980-1-1", dt_end="2100-1-1"):
        """ 获取本地历史数据

        Args:
            strpcon (str): 周期合约
            dt_start (datetime): 数据的开始时间
            dt_end (datetime): 数据的结束时间

        Returns:
            DataFrame.
        """
        if isinstance(dt_start, str):
            dt_start = datetime.strptime(dt_start, "%Y-%m-%d")
        if isinstance(dt_end, str):
            dt_end = datetime.strptime(dt_end, "%Y-%m-%d")
        return self.get_bars(pcontract, dt_start, dt_end).data

    def get_contracts(self):
        """ 获取所有合约的基本信息"""
        return self._src.get_contracts()

    def get_exchanges(self):
        """ 获取所有交易所的编码"""
        return self._src.get_exchanges()

    def get_tables(self):
        """ 返回数据库所有的表格"""
        return self._src.get_tables()

    def import_bars(self, data_iter, strpcon):
        """ 导入交易数据

        Args:
            data_iter (iteratorable object): 数据['datetime', 'open', 'close',
            'high', 'low', 'volume']
            strpcon (str): 周期合约字符串如, 'AA.SHFE-1.Minute'

        """
        pcontract = PContract.from_string(strpcon)
        self._src.import_bars(data_iter, pcontract)

    def import_contracts(self, data):
        """ 导入合约的基本信息。

        Args:
            data (iteratorable object): 数据['key', 'code', 'exchange', 'name',
            'spell', 'long_margin_ratio', 'short_margin_ratio', 'price_tick',
            'volume_multiple']

        """
        self._src.import_contracts(data)

    def export_bars(self, index=True, index_label='index'):
        """ 导出sqlite中的所有表格数据。

        Args:
            index (bool): 是否显示index

            index_label: 索引标签

        Returns:
            int. The result
        """
        self._src.export_bars(index, index_label)


class ServerData(object):
    """
    服务器数据代理。
    """
    def __init__(self):
        pass

    def get_bars(self, strpcon, dt_start, dt_end):
        pcontract = PContract.from_string(strpcon)
        if pcontract.contract.exchange == 'stock':
            return self.get_tushare_bars(pcontract, dt_start, dt_end)
        else:
            return []

    def get_tushare_bars(self, pcontract, dt_start, dt_end):
        import tushare as ts
        print "get stock data with tushare... (start=%s,end=%s)" % \
            (dt_start, dt_end)
        if pcontract.period._type == 'Minute':
            data = tick2period(pcontract.contract.code,
                               str(pcontract.period)[:-3].replace('.', ''),
                               start=dt_start,
                               end=dt_end)
        elif pcontract.period._type == 'Second':
            data = tick2period(pcontract.contract.code,
                               str(pcontract.period)[:-5].replace('.', ''),
                               start=dt_start,
                               end=dt_end)
        else:

            # 日线直接调用
            data = ts.get_hist_data(pcontract.contract.code,
                                    start=dt_start,
                                    end=dt_end)
            data.open = data.open.astype(float)
            data.close = data.close.astype(float)
            data.high = data.high.astype(float)
            data.low = data.low.astype(float)
            # @todo bug: data.volume 里面有浮点值！
            data.volume = data.volume.astype(float)
            data.index.names = ['datetime']
            data.index = pd.to_datetime(data.index)
            return data


class DataManager(object):
    """
    数据代理
    """
    def __init__(self):
        self._loc_data = locd
        self._srv_data = ServerData()

    def get_bars(self, strpcon, dt_start="1980-1-1", dt_end="2100-1-1"):
        """  加载时间范围[dt_start, dt_end]的k线数据。

        Args:
            strpcon (str): 周期合约
            dt_start(datetime/str): 开始时间
            dt_end(datetime/str): 结束时间

        Returns:
            SourceWrapper.
        """
        # @TODO 不存在数据时可能返回一个空的list, 虽然不影响程序执行。
        if isinstance(dt_start, str):
            dt_start = datetime.strptime(dt_start, "%Y-%m-%d")
        if isinstance(dt_end, str):
            dt_end = datetime.strptime(dt_end, "%Y-%m-%d")
        # dt_end += timedelta(days=1) # dt_end]
        data = self._loc_data.get_bars(strpcon, dt_start, dt_end)
        if len(data) == 0:
            return self._srv_data.get_bars(strpcon, dt_start, dt_end)
        else:
            return data

    def get_last_bars(self, strpcon, n):
        data = self._loc_data.get_last_bars(strpcon, n)
        if len(data) == 0:
            return self._srv_data.get_last_bars(strpcon, n)
        else:
            return data

    def get_code2strpcon(self):
        return self._loc_data.get_code2strpcon()

locd = LocalData()
__all__ = ['DataManager', 'locd']
