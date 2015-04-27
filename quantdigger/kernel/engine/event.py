# -*- coding: utf8 -*-
 # event.py
#from flufl.enum import Enum
class EventsPool(object):
    ## @todo 不能共享队列，因为有多策略，每个策略一个消息队列。
    """ 事件池。"""
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
        print len(self._pool)

    def get(self):
        """docstring for get""" 
        return self._pool.pop(0)


class Event(object):
    MARKET = 1
    SIGNAL = 2
    ORDER = 3
    FILL = 4


class MarketEvent(object):
    """
    Handles the event of receiving a new market update with 
    corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = Event.MARKET


class SignalEvent(object):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    
    def __init__(self, orders):
        """
        Initialises the SignalEvent.

        Parameters:
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT'.
        """
        
        self.type = Event.SIGNAL
        self.orders = orders


class OrderEvent(object):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, order):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        
        # simbol 会比Contract好记。
        # 让计算机处理simbol和contract的映射。
        self.type = Event.ORDER
        self.order = order




class FillEvent(object):
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
