# -*- coding: utf8 -*-
from quantdigger.datastruct import Transaction, PriceType, TradeSide, Direction
from quantdigger.engine.event import FillEvent
from quantdigger.util import elogger as logger
class Exchange(object):
    """ 模拟交易所。
  
        :ivar _slippage: 滑点模型。
        :ivar _open_orders: 未成交订单。
        :ivar events: 事件池。
    """
    def __init__(self, name, events_pool, slippage = None, strict=True):
        self._slippage = slippage
        self._open_orders = set()
        self.events = events_pool
        # strict 为False表示只关注信号源的可视化，而非实际成交情况。
        self._strict = strict
        self._datetime = None
        self.name = name

    def make_market(self, bars):
        """ 价格撮合""" 
            #for order in self._open_orders:
                #print order.id
        fill_orders = set()
        for order in self._open_orders:
            if order.side == TradeSide.CANCEL:
                transact = Transaction(order)
                self.events.put(FillEvent(transact)) 
                fill_orders.add(order)
                continue
            try:
                bar = bars[order.contract]
            except KeyError:
                logger.error('所交易的合约[%s]数据不存在' % order.contract)
                continue
            transact = Transaction(order)
            if self._strict:
                if order.price_type == PriceType.LMT:
                    # 限价单以最高和最低价格为成交的判断条件．
                    if (order.side == TradeSide.KAI and \
                             (order.direction == Direction.LONG and order.price >= bar.low or \
                             order.direction == Direction.SHORT and order.price <= bar.high)) or \
                       (order.side == TradeSide.PING and \
                             (order.direction == Direction.LONG and order.price <= bar.high or \
                             order.direction == Direction.SHORT and order.price >= bar.low)):
                            transact.price = order.price
                            # Bar的结束时间做为交易成交时间.
                            transact.datetime = bar.datetime
                            fill_orders.add(order)
                            self.events.put(FillEvent(transact)) 
                elif order.price_type == PriceType.MKT:
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
            # end of for 
        if fill_orders:
            self._open_orders -= fill_orders

        #if self.name == 'A3':
            #print "aaaaaaaa" 
            #for order in self._open_orders:
                #print order.id


    def insert_order(self, event):
        """
        模拟交易所收到订单。
        """ 
        # 如果是撤单，会自动覆盖。
        #if self.name == 'A3':
            #for order in self._open_orders:
                #print order
            #print event.order.id, event.order.side, "##" 
            #print "-----------------" 
        ## @TODO 
        if event.order in self._open_orders:
            self._open_orders.remove(event.order) 
        self._open_orders.add(event.order)

        #if self.name == 'A3':
            #for order in self._open_orders:
                #print order


    def cancel_order(self, order):
        ## @TODO 撤单
        pass

    def update_datetime(self, dt):
        if self._datetime:
            if self._datetime.date() != dt.date():
                self._open_orders.clear()
        self._datetime = dt
