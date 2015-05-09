# -*- coding: utf8 -*-
from logbook import Logger
import time

engine_logger = Logger('engine')
data_logger = Logger('data')

def time2int(t):
     """ datetime to int  """
     epoch =  int(time.mktime(t.timetuple())*1000)
     return epoch

def pcontract(contract, period):
    """ 构建周期合约结构的便捷方式。
    
    Args:
        contract (str): 合约如：'IF000.SHEF'
        period(str): 周期如：'10.Minute' 
    Returns:
        PContract. 周期合约
    """
    from quantdigger.kernel.datastruct import PContract, Contract, Period
    return PContract(Contract(contract),
                     Period(period))

def stock(code):
    """ 构建周期合约结构的便捷方式。
    
    Args:
        code (str): 股票代码
    
    Returns:
        PContract. 周期合约
    """
    from quantdigger.kernel.datastruct import PContract, Contract, Period
    return PContract(Contract('%s.stock' %  code),
                     Period('1.Day'))
