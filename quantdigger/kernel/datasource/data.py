# -*- coding: utf8 -*-
import pandas as pd
from quantdigger.errors import FileDoesNotExist


def process_tushare_data(data):
    """""" 
    data.open = data.open.astype(float)
    data.close = data.close.astype(float)
    data.high = data.high.astype(float)
    data.low = data.low.astype(float)
    ## @todo bug: data.volume 里面有浮点值！
    data.volume = data.volume.astype(float)
    data.index.names = ['datetime']
    data.index = pd.to_datetime(data.index)

    return data

class QuoteCache(object):
    """docstring for QuoteCache"""
    def __init__(self, arg):
        pass
        #contract2

class LocalData(object):
    """ 本地数据数据接口类。
    
    包括数据，合约信息等。
    """
    def load_data(self, pcontract, dt_start=None, dt_end=None):
        """ 加载本地周期合约数据.
        
        Args:
            pcontract (PContract): 周期合约
        
        Returns:
            DataFrame. 

        Raises:
            FileDoesNotExist
        """
        if pcontract.contract.exch_type == 'stock':
            import tushare as ts
            # 使用tushare接口
            print "load stock data with tushare..." 
            data = ts.get_hist_data(pcontract.contract.code)
            return process_tushare_data(data)
        else:
            # 期货数据
            fname = ''.join([str(pcontract), ".csv"])
            try:
                data = pd.read_csv(fname, index_col=0, parse_dates=True)
                assert data.index.is_unique
            except Exception:
                #print u"**Warning: File \"%s\" doesn't exist!"%fname
                raise FileDoesNotExist(file=fname)
            else:
                return data

    def loadTickData(self):
        raise NotImplementedError

    def loadContractsInfo(self):
        """ 合约信息 """
        raise NotImplementedError

local_data = LocalData()

class DataManager(object):
    """"""
    def __init__(self, arg):
        pass
    
