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
from quantdigger.datasource.source import CsvSource, SqlLiteSource
from quantdigger.datasource.datautil import tick2period
from quantdigger.datastruct import PContract

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
        self._csv = CsvSource(os.path.join(os.getcwd(), 'data'))
        self._sql = SqlLiteSource(os.path.join(os.getcwd(), 'data', 'digger.db'))
        self._src = self._csv # 设置数据源

    def load_bars(self, strpcon, dt_start, dt_end, window_size):
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
        if pcontract.contract.exch_type == 'stock':
            return []
        else:
            return self._src.load_bars(pcontract, dt_start, dt_end, window_size);

    def load_data(self, pcontract, dt_start=datetime(1980,1,1),
                  dt_end=datetime(2100,1,1), window_size=0):
        """ 返回DataFrame数据 """
        return self.load_bars(pcontract, dt_start, dt_end, window_size).data

    def loadTickData(self):
        raise NotImplementedError

    def loadContractsInfo(self):
        """ 合约信息 """
        raise NotImplementedError


class ServerData(object):
    """
    服务器数据代理。
    """
    def __init__(self):
        pass

    def load_bars(self, strpcon, dt_start, dt_end):
        pcontract = PContract.from_string(strpcon)
        if pcontract.contract.exch_type == 'stock':
            return self.load_tushare_bars(pcontract, dt_start, dt_end)
        else:
            return []

    def load_tushare_bars(self, pcontract, dt_start, dt_end):
        import tushare as ts
        print "load stock data with tushare... (start=%s,end=%s)" % (dt_start, dt_end)
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
    

class DataManager(object):
    """
    数据代理
    """
    def __init__(self):
        self._loc_data = LocalData()
        self._srv_data = ServerData()

    def load_bars(self, strpcon , dt_start=datetime(1980,1,1),
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
        data = self._loc_data.load_bars(strpcon, dt_start, dt_end, window_size)
        if len(data) == 0:
            return self._srv_data.load_bars(strpcon, dt_start, dt_end) 
        else:
            return data

