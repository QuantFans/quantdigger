# -*- coding: utf8 -*-
from logbook import Logger
import time

engine_logger = Logger('engine')
data_logger = Logger('data')

def time2int(t):
     """ datetime to int  """
     epoch =  int(time.mktime(t.timetuple())*1000)
     return epoch

def pcontract(exchange, contract, time_unit, unit_count):
    """ 构建周期合约结构的便捷方式。
    
    Args:
        exchange (str): 交易所
        contract (str): 合约
        time_unit (str): 时间单位
        unit_count (int): 时间数目
    
    Returns:
        PContract. 周期合约
    """
    from quantdigger.kernel.datastruct import PContract, Contract, Period
    return PContract(Contract(exchange, contract),
                     Period(time_unit, unit_count))

def stock(code):
    """ 构建周期合约结构的便捷方式。
    
    Args:
        code (str): 股票代码
    
    Returns:
        PContract. 周期合约
    """
    from quantdigger.kernel.datastruct import PContract, Contract, Period
    return PContract(Contract('stock', code),
                     Period('Days', 1))
