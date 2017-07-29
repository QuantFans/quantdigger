# -*- coding: utf-8 -*-
# from flufl.enum import Enum
import json
import six

from quantdigger.util import py


# @TODO REMOVE EventsPool
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
    MARKET = 'MARKET'
    SIGNAL = 'SIGNAL'
    ORDER = 'ORDER'
    FILL = 'FILL'
    ONCE = 'ONCE'
    TIMER = 'TIMER'

    def __init__(self, route, args):
        self.data = {
            'route': route,
            'data': args
        }

    def __str__(self):
        return "route: %s\nargs: %s" % (self.data['route'], self.data['data'])

    @property
    def route(self):
        return self.data['route']

    @property
    def args(self):
        """"""
        return self.data['data']

    @classmethod
    def message_to_event(self, message):
        if py == 3:
            message = message.decode('utf8')
        route, args = message.split('&')
        route = route[1:]
        return Event(route=route, args=json.loads(args))

    @classmethod
    def event_to_message(self, event):
        # 消息头 ＋ json字符串
        return '<%s&' % event.route + json.dumps(event.args)

    @classmethod
    def message_header(self, route):
        return b'<%s&' % six.b(route)


class SignalEvent(Event):
    """ 由策略函数产生的交易信号事件。 """

    def __init__(self, orders):
        super(SignalEvent, self).__init__(Event.SIGNAL, orders)

    @property
    def orders(self):
        return self.data['data']


class OrderEvent(Event):
    """ 委托下单事件。 """

    def __init__(self, order):
        super(OrderEvent, self).__init__(Event.ORDER, order)

    @property
    def order(self):
        return self.data['data']


class OnceEvent(Event):

    def __init__(self):
        super(OnceEvent, self).__init__(Event.ONCE, None)


class FillEvent(Event):
    """ 委托下单事件。 """

    def __init__(self, transaction):
        super(FillEvent, self).__init__(Event.FILL, transaction)

    @property
    def transaction(self):
        return self.data['data']
