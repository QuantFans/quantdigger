# -*- coding: utf-8 -*-
##
# @file data.py
# @brief 本地数据，远程数据，数据控制模块
# @author wondereamer
# @version 0.2
# @date 2015-12-09


import os
import pandas as pd
from datetime import datetime, timedelta
from quantdigger.errors import FileDoesNotExist
from quantdigger.datasource.source import CsvSource, SqlLiteSource
from quantdigger.datasource.datautil import tick2period
from quantdigger.datastruct import PContract, Contract

class QuoteCache(object):
    def __init__(self, arg):
        pass

class LocalData(object):
    """ 
    本地数据代理根据配置决定数据源的类型,
        比如sqlite, csv, pytable
    """
    def __init__(self):
        """
        """ 
        self._src = None
        self.source = ''

    def reset_source(self, settings):
        """ 重新设置数据源 """ 
        if settings['source'] == 'sqlite' :
            try:
                import sqlite3
                path = os.path.join(settings['data_path'], 'digger.db') 
                self._src = SqlLiteSource(path)
            except sqlite3.OperationalError:
                raise FileDoesNotExist(file=path)
        elif settings['source'] == 'csv':
            self._src = CsvSource(settings['data_path'])
        try:
            Contract.info = self.get_contracts()
        except Exception, e:
            ## @TODO 
            pass
        self.source = settings['source']

    def get_bars(self, strpcon, dt_start, dt_end, window_size):
        """ 获取本地历史数据    
        
        Args:
            strpcon (str): 周期合约

            dt_start (datetime): 数据的开始时间

            dt_end (datetime): 数据的结束时间

            window_size (int): 窗口大小，0表示大小为数据长度。
        
        Returns:
            SourceWrapper. 数据
        """
        pcontract = PContract.from_string(strpcon)
        if pcontract.contract.exchange == 'stock':
            return []
        else:
            return self._src.get_bars(pcontract, dt_start, dt_end, window_size);

    def get_data(self, pcontract, dt_start=datetime(1980,1,1),
                  dt_end=datetime(2100,1,1), window_size=0):
        """ 返回DataFrame数据 """
        return self.get_bars(pcontract, dt_start, dt_end, window_size).data

    def getTickData(self):
        raise NotImplementedError

    def getContractsInfo(self):
        """ 合约信息 """
        raise NotImplementedError

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
        self._src.import_bars(data_iter, strpcon)

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
        print "get stock data with tushare... (start=%s,end=%s)" % (dt_start, dt_end)
        if(pcontract.period._type == 'Minute' ):
            data = tick2period(pcontract.contract.code,
                               str(pcontract.period)[:-3].replace('.',''),
                               start=dt_start,
                               end=dt_end)
        elif(pcontract.period._type == 'Second' ):
            data = tick2period(pcontract.contract.code,
                               str(pcontract.period)[:-5].replace('.',''),
                               start=dt_start,
                               end=dt_end)
        else:
                
            #日线直接调用
            data = ts.get_hist_data(pcontract.contract.code,
                                    start=dt_start,
                                    end=dt_end)
            data.open = data.open.astype(float)
            data.close = data.close.astype(float)
            data.high = data.high.astype(float)
            data.low = data.low.astype(float)
            ## @todo bug: data.volume 里面有浮点值！
            data.volume = data.volume.astype(float)
            data.index.names = ['datetime']
            data.index = pd.to_datetime(data.index)
            return data
    
locd = LocalData()
#locd.get_contracts
class DataManager(object):
    """
    数据代理
    """
    def __init__(self):
        self._loc_data = locd
        self._srv_data = ServerData()

    def get_bars(self, strpcon , dt_start=datetime(1980,1,1),
                  dt_end=datetime(2100,1,1), window_size=0):
        """  加载时间范围[dt_start, dt_end]的k线数据。
        
        Args:
            strpcon (str): 周期合约

            dt_start(datetime): 开始时间

            dt_end(datetime): 结束时间
        
        Returns:
            SourceWrapper.
        """
        if type(dt_start) == str:
            dt_start = datetime.strptime(dt_start, "%Y-%m-%d")
        if type(dt_end) == str:
            dt_end = datetime.strptime(dt_end, "%Y-%m-%d")
        dt_end += timedelta(days=1)
        data = self._loc_data.get_bars(strpcon, dt_start, dt_end, window_size)
        if len(data) == 0:
            return self._srv_data.get_bars(strpcon, dt_start, dt_end) 
        else:
            return data

__all__ = ['DataManager', 'locd']
