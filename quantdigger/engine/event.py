# -*- coding: utf-8 -*-
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
    ONCE = 5


class MarketEvent(object):
    """ 市场数据到达事件。 """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = Event.MARKET


class SignalEvent(object):
    """ 由策略函数产生的交易信号事件。 """

    def __init__(self, orders):
        self.type = Event.SIGNAL
        self.orders = orders


class OrderEvent(object):
    """ 委托下单事件。 """

    def __init__(self, order):
        self.type = Event.ORDER
        self.order = order


class OnceEvent(object):

    def __init__(self):
        self.type = Event.ONCE


class FillEvent(object):
    """ 委托成交事件。 """
    def __init__(self, transaction):
        self.type = Event.FILL
        self.transaction = transaction
