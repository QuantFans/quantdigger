
# -*- coding: utf8 -*-
from logbook import Logger
import time
from progressbar import ProgressBar

elogger = Logger('engine')
dlogger = Logger('data')

def time2int(t):
     """ datetime转化为整数。
     
        :param datetime t: 时间。
        :return: 整数。
        :rtype: int
     """
     epoch =  int(time.mktime(t.timetuple())*1000)
     return epoch

def pcontract(contract, period):
    """ 构建周期合约结构的便捷方式。
    
       :param str contract: 合约如：'IF000.SHEF'
       :param str Period: 周期如：'10.Minute' 
       :return: 周期合约
       :rtype: PContract
    """
    from quantdigger.datastruct import PContract, Contract, Period
    return PContract(Contract(contract),
                     Period(period))

def stock(code,period='1.Day'):
    """ 构建周期合约结构的便捷方式。
    
       :param str code: 股票代码。
       :param str period: 回测周期。
       :return: 周期合约。
       :rtype: PContract
    """
    from quantdigger.datastruct import PContract, Contract, Period
    return PContract(Contract('%s.stock' %  code),
                     Period(period))

def formatTimeTicks():
    """ 格式化时间显示""" 
    pass

