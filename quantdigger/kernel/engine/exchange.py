# -*- coding: utf8 -*-
from quantdigger.kernel.datastruct import Transaction, PriceType, TradeSide, Direction
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
        # strict 为False表示只关注信号源的可视化，而非实际成交情况。
        self._strict = strict

    def make_market(self, bar):
        ## @bug 开仓资金是否足够的验证
        ## @todo 
        """ 价格撮合""" 
        if self._open_orders:
            fill_orders = set()
            for order in self._open_orders:
                transact = Transaction(order)
                if self._strict:
                    if order.price_type == PriceType.LMT:
                        # 限价单以最高和最低价格为成交的判断条件．
                        if (order.side == TradeSide.KAI and \
                                 (order.direction == Direction.LONG and order.price >= bar.low or \
                                 order.direction == Direction.SHORT and order.price <= bar.high)) or \
                           (order.kpp == TradeSide.PING and \
                                 (order.direction == Direction.LONG and order.price <= bar.high or \
                                 order.direction == Direction.SHORT and order.price >= bar.low)):
                                transact.price = order.price
                                # Bar的结束时间做为交易成交时间.
                                transact.datetime = bar.datetime
                                fill_orders.add(order)
                                self.events.put(FillEvent(transact)) 
                    elif order.type == PriceType.MKT:
                        # 市价单以最高或最低价格为成交价格．
                        if order.side == TradeSide.KAI:
                            if order.direction == Direction.LONG:
                                transact.price = bar.high
                            else:
                                transact.price = bar.low
                        elif order.side == TradeSide.PING:
                            if order.direction == Direction.LONG:
                                transact.price = bar.low
                            else:
                                transact.price = bar.high

                        transact.datetime = bar.datetime
                        fill_orders.add(order)
                        self.events.put(FillEvent(transact)) 
                else:
                    transact.datetime = bar.datetime
                    fill_orders.add(order)
                    #
                    self.events.put(FillEvent(transact)) 
            if fill_orders:
                self._open_orders -= fill_orders


    def insert_order(self, event):
        """
        模拟交易所收到订单。
        """ 
        self._open_orders.add(event.order)

    def cancel_order(self, order):
        pass


    def update_datetime(self, dt):
        self._datetime = dt


