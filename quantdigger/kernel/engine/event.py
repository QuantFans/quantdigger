# -*- coding: utf8 -*-
 # event.py
#from flufl.enum import Enum
class EventsPool(object):
    """ 事件池，每个策略有一个。"""
    _pool = []
    def __init__(self, container=None):
        """ container决定是否是线程安全的。
        
        Args:
            container (list or Queue): 事件容器
        """
        if container:
            self._pool = container

    def put(self, item):
        self._pool.append(item)

    def get(self):
        return self._pool.pop(0)


class Event(object):
    """ 事件类型。

    :ivar MARKET: 市场数据事件, 目前未用到。
    :ivar SIGNAL: 交易信号事件, 由策略函数产生。
    :ivar ORDER: 委托下单事件, 由下单控制器产生。
    :ivar FILL: 订单成交事件, 由交易模拟器产生。
    """
    MARKET = 1
    SIGNAL = 2
    ORDER = 3
    FILL = 4


class MarketEvent(object):
    """
    市场数据到达事件。
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = Event.MARKET


class SignalEvent(object):
    """
    由策略函数产生的交易信号事件。
    """
    
    def __init__(self, orders):
        self.type = Event.SIGNAL
        self.orders = orders


class OrderEvent(object):
    """
    委托下单事件。
    """

    def __init__(self, order):
        self.type = Event.ORDER
        self.order = order




class FillEvent(object):
    """ 委托成交事件。 """
    def __init__(self, transaction):
        self.type = Event.FILL
        self.transaction = transaction
    #"""
    #Encapsulates the notion of a Filled Order, as returned
    #from a brokerage. Stores the quantity of an instrument
    #actually filled and at what price. In addition, stores
    #the commission of the trade from the brokerage.
    #"""

    #def __init__(self, timeindex, symbol, exchange, quantity, 
                 #direction, fill_cost, commission=None):
        #"""
        #Initialises the FillEvent object. Sets the symbol, exchange,
        #quantity, direction, cost of fill and an optional 
        #commission.

        #If commission is not provided, the Fill object will
        #calculate it based on the trade size and Interactive
        #Brokers fees.

        #Parameters:
        #timeindex - The bar-resolution when the order was filled.
        #symbol - The instrument which was filled.
        #exchange - The exchange where the order was filled.
        #quantity - The filled quantity.
        #direction - The direction of fill ('BUY' or 'SELL')
        #fill_cost - The holdings value in dollars.
        #commission - An optional commission sent from IB.
        #"""
        
        #self.type = Event.FILL
        #self.timeindex = timeindex
        #self.symbol = symbol
        #self.exchange = exchange
        #self.quantity = quantity
        #self.direction = direction
        #self.fill_cost = fill_cost

        ## Calculate commission
        #if commission is None:
            #self.commission = self.calculate_ib_commission()
        #else:
            #self.commission = commission

    #def calculate_ib_commission(self):
        #"""
        #Calculates the fees of trading based on an Interactive
        #Brokers fee structure for API, in USD.

        #This does not include exchange or ECN fees.

        #Based on "US API Directed Orders":
        #https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        #"""
        #full_cost = 1.3
        #if self.quantity <= 500:
            #full_cost = max(1.3, 0.013 * self.quantity)
        #else: # Greater than 500
            #full_cost = max(1.3, 0.008 * self.quantity)
        #full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        #return full_cost
