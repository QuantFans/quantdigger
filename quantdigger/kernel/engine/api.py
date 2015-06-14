# -*- coding: utf8 -*-
from abc import ABCMeta, abstractmethod

class Trader(object):
    __metaclass__ = ABCMeta
    """ 交易类，包含了回调注册等高级封装。  """

    def __init__(self, arg):
        pass

    @abstractmethod
    def connect(self):
        """ 连接器 """ 
        pass

    @abstractmethod
    def register_handlers(self, handlers):
        """  注册回调函数 """ 
        pass

    @abstractmethod
    def query_contract(self, contract, sync=False):
        """ 合约查询 """ 
        pass

    @abstractmethod
    def query_tick(self, contract, sync=False):
        """ 深度行情数据 """ 
        pass

    @abstractmethod
    def query_captital(self, sync=False):
        """ 查询资金账户 """ 
        pass

    @abstractmethod
    def query_position(self, sync=False):
        """ 查询投资者持仓""" 
        pass

    @abstractmethod
    def order(self, order, sync=False):
        """ 下单请求    
        
           :param Order order: 委托订单。
        """
        pass

    @abstractmethod
    def cancel_order(self, orderid, sync=False):
        """ 撤单操作请求 """ 
        pass

    
    
class CtpTraderAPI(object):
    """  Ctp交易类 """
    def __init__(self):
        pass

    def connect(self):
        """ 连接""" 
        pass

    def query_contract(self, contract):
        """ 合约查询 """ 
        pass

    def query_tick(self, contract):
        """ 深度行情数据 """ 
        pass

    def query_captital(self):
        """ 查询资金账户 """ 
        pass

    def query_position(self):
        """ 查询投资者持仓""" 
        pass

    def order(self, order):
        """ 下单请求    """
        pass

    def cancel_order(self, orderid):
        """ 撤单操作请求 """ 
        pass


class SimulateTrader(Trader):
    """ 模拟交易下单接口 """
    def __init__(self):
        pass

    def connect(self):
        """ 连接""" 
        pass

    def query_contract(self, contract):
        """ 合约查询 """ 
        pass

    def query_tick(self, contract):
        """ 深度行情数据 """ 
        pass

    def query_captital(self):
        """ 查询资金账户 """ 
        pass

    def query_position(self):
        """ 查询投资者持仓""" 
        pass

    def order(self, order):
        """ 下单请求    """
        pass

    def cancel_order(self, orderid):
        """ 撤单操作请求 """ 
        pass
