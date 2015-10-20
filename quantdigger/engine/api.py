# -*- coding: utf8 -*-
from quantdigger.engine.event import OrderEvent
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

    #@abstractmethod
    #def register_handlers(self, handlers):
        #"""  注册回调函数 """ 
        #pass

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

    def on_transaction(self, trans):
        """ 委托成交回调 """ 
        pass

    def on_tick(self, tick):
        """ tick数据回调  """ 
        pass

    def on_captial(self, tick):
        """ 资金查询回调  """ 
        pass

    def on_position(self, tick):
        """ 持仓查询回调 """ 
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

    def on_transaction(self, trans):
        """ 委托成交回调 """ 
        pass

    def on_tick(self, tick):
        """ tick数据回调  """ 
        pass

    def on_captial(self, tick):
        """ 资金查询回调  """ 
        pass

    def on_position(self, tick):
        """ 持仓查询回调 """ 
        pass


class SimulateTraderAPI(Trader):
    """ 模拟交易下单接口 """
    def __init__(self, blotter, events_pool):
        self._blotter = blotter
        self._events = events_pool

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
        """ 模拟下单 """
        self._events.put(OrderEvent(order)) 

    def cancel_order(self, orderid):
        """ 撤单操作请求 """ 
        pass

    def on_transaction(self, trans):
        """ 模拟委托成交回调 """ 
        self._blotter.update_fill(trans)

    def on_tick(self, tick):
        """ tick数据回调  """ 
        pass

    def on_captial(self, tick):
        """ 资金查询回调  """ 
        pass

    def on_position(self, tick):
        """ 持仓查询回调 """ 
        pass
