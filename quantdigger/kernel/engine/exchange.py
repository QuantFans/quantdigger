# -*- coding: utf8 -*-
from quantdigger.kernel.datastruct import Transaction
from quantdigger.kernel.engine.event import FillEvent
class Exchange(object):
    """ 模拟交易所。
  
        :ivar _slippage: 滑点模型。
        :ivar _open_orders: 未成交订单。
        :ivar events: 事件池。
    """
    def __init__(self, events_pool, slippage = None, strict=True):
        self._slippage = slippage
        self._open_orders = set()
        self.events = events_pool
        self._strict = strict

    def make_market(self, bar):
        """ 价格撮合""" 
        if self._open_orders:
            fill_orders = set()
            for order in self._open_orders:
                transact = Transaction(order)
                if self._strict:
                    if order.type == 'limit':
                        # 限价单以最高和最低价格为成交的判断条件．
                        if (order.kpp == 'k' and \
                                 (order.direction == 'd' and order.price >= bar.low or \
                                 order.direction == 'k' and order.price <= bar.high)) or \
                           (order.kpp == 'p' and \
                                 (order.direction == 'd' and order.price <= bar.high or \
                                 order.direction == 'k' and order.price >= bar.low)):
                                transact.price = order.price
                                # Bar的结束时间做为交易成交时间.
                                transact.datetime = bar.datetime
                                fill_orders.add(order)
                                self.events.put(FillEvent(transact)) 
                    elif order.type == 'market':
                        # 市价单以最高或最低价格为成交价格．
                        if order.direction == 'd':
                            transact.price = bar.high
                        else:
                            transact.price = bar.low
                        transact.datetime = bar.datetime
                        fill_orders.add(order)
                        self.events.put(FillEvent(transact)) 
                else:
                    transact.datetime = bar.datetime
                    fill_orders.add(order)
                    self.events.put(FillEvent(transact)) 
            if fill_orders:
                self._open_orders -= fill_orders


    def insert_order(self, order_event):
        pass

    def cancel_order(self, order):
        pass

    def update_order(self, event):
        """
        模拟交易所收到订单。
        """ 
        self._open_orders.add(event.order)

    def update_datetime(self, dt):
        self._datetime = dt


