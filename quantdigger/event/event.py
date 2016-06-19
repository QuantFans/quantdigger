# -*- coding: utf-8 -*-
# from flufl.enum import Enum
import json

class Event:
    """ 事件类型。

    :ivar MARKET: 市场数据事件, 目前未用到。
    :ivar SIGNAL: 交易信号事件, 由策略函数产生。
    :ivar ORDER: 委托下单事件, 由下单控制器产生。
    :ivar FILL: 订单成交事件, 由交易模拟器产生。
    """
    MARKET = 'MARKET' 
    SIGNAL = 'SIGNAL' 
    ORDER = 'ORDER' 
    FILL = 'FILL' 
    ONCE = 'ONCE' 
    TIMER = 'TIMER' 
    def __init__(self, route=None, args={ }):
        self.route = route
        self.args = args

    def __str__(self):
        return "route: %s\nargs: %s" % (self.route, self.args)

    @classmethod
    def message_to_event(self, message):
        route, args = message.split(']')
        route = route[1:]
        return Event(route=route, args=json.loads(args))

    @classmethod
    def event_to_message(self, event):
        return '[%s]' % event.route + json.dumps(event.args)


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





#class SignalEvent(object):
    #""" 由策略函数产生的交易信号事件。 """

    #def __init__(self, orders):
        #self.type = Event.SIGNAL
        #self.orders = orders


#class OrderEvent(object):
    #""" 委托下单事件。 """

    #def __init__(self, order):
        #self.type = Event.ORDER
        #self.order = order



#class FillEvent(object):
    #""" 委托成交事件。 """
    #def __init__(self, transaction):
        #self.type = Event.FILL
        #self.transaction = transaction
