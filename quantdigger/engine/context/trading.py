#!/usr/bin/env python
# encoding: utf-8


import copy
import six
from six.moves import queue
from quantdigger.engine.blotter import SimpleBlotter
from quantdigger.engine.exchange import Exchange
from quantdigger.event import Event, EventsPool, SignalEvent, OnceEvent
from quantdigger.datastruct import (
    Order,
    TradeSide,
    Direction,
    PositionKey,
    PriceType,
    Contract
)


class TradingDelegator(object):
    """"""
    def __init__(self, name, settings={}):
        self.events_pool = EventsPool()
        # @TODO merge blotter and exchange
        self.blotter = SimpleBlotter(name, self.events_pool, settings)
        self.exchange = Exchange(name, self.events_pool, strict=True)
        self._new_orders = []
        self._datetime = None
        self._cancel_now = False  # 是当根bar还是下一根bar撤单成功。

    def update_environment(self, dt, ticks, bars):
        """ 更新模拟交易所和订单管理器的数据，时间,持仓 """
        self._datetime = dt
        self.blotter.update_datetime(dt)
        self.blotter.update_data(ticks, bars)
        self.exchange.update_datetime(dt)

    def process_trading_events(self, at_baropen):
        """ 提交订单，撮合，更新持仓 """
        if self._new_orders:
            self.events_pool.put(SignalEvent(self._new_orders))
        if not self._new_orders:
            # 没有交易信号，确保至少运行一次
            self.events_pool.put(OnceEvent())
        self._process_trading_events(at_baropen)
        self._new_orders = []

    def _process_trading_events(self, at_baropen):
        """"""
        while True:
            # 事件处理。
            try:
                event = self.events_pool.get()
            except queue.Empty:
                assert(False)
            except IndexError:
                break
            else:
                # if event.type == 'MARKET':
                    # strategy.calculate_signals(event)
                    # port.update_timeindex(event)
                if event.route == Event.SIGNAL:
                    assert(not at_baropen)
                    self.blotter.update_signal(event)
                elif event.route == Event.ORDER:
                    assert(not at_baropen)
                    self.exchange.insert_order(event)
                elif event.route == Event.FILL:
                    # 模拟交易接口收到报单成交
                    self.blotter.api.on_transaction(event)
            # 价格撮合。note: bar价格撮合要求撮合置于运算后面。
            # @TODO tick 回测不一样
            if event.route == Event.ONCE or event.route == Event.ORDER:
                self.exchange.make_market(self.blotter._bars, at_baropen)
        self.blotter.update_status(self._datetime, at_baropen)

    def buy(self, price, quantity, symbol=None):
        """ 开多仓

        Args:
            price (float): 价格, 0表市价。
            quantity (int): 数量。
            symbol (str): 合约
        """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能下单！')
        if symbol:
            contract = Contract(symbol) if isinstance(symbol, str) else symbol
        else:
            contract = self.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._new_orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.OPEN,
            Direction.LONG,
            float(price),
            quantity
        ))

    def sell(self, price, quantity, symbol=None):
        """ 平多仓。

        Args:
           price (float): 价格, 0表市价。
           quantity (int): 数量。
           symbol (str): 合约
        """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能下单！')
        if symbol:
            contract = Contract(symbol) if isinstance(symbol, str) else symbol
        else:
            contract = self.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._new_orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.CLOSE,
            Direction.LONG,
            float(price),
            quantity
        ))

    def short(self, price, quantity, symbol=None):
        """ 开空仓

        Args:
            price (float): 价格, 0表市价。
            quantity (int): 数量。
            symbol (str): 合约
        """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能下单！')
        if symbol:
            contract = Contract(symbol) if isinstance(symbol, str) else symbol
        else:
            contract = self.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._new_orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.OPEN,
            Direction.SHORT,
            float(price),
            quantity
        ))

    def cover(self, price, quantity, symbol=None):
        """ 平空仓。

        Args:
           price (float): 价格, 0表市价。
           quantity (int): 数量。
           symbol (str): 合约
        """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能下单！')
        if symbol:
            contract = Contract(symbol) if isinstance(symbol, str) else symbol
        else:
            contract = self.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._new_orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.CLOSE,
            Direction.SHORT,
            float(price),
            quantity
        ))


    def cancel(self, orders):
        """ 撤单

        Args:
            orders (list/Order): 撤单，参数为list表示撤多个单。
        """
        orders = orders if isinstance(orders, list) else [orders]
        if not self._cancel_now:
            # 当前bar收盘处处理撤单
            for order in orders:
                norder = copy.deepcopy(order)
                norder.side = TradeSide.CANCEL
                # @TODO or self._new_orders ?
                # 结合实盘考虑, 实盘可能自动撤单。
                self._new_orders.append(norder)
            return
        ## 立即处理撤单
        #temp = copy.deepcopy(self._new_orders)
        #self._new_orders = []
        #for order in orders:
            #order.side = TradeSide.CANCEL
            #self._new_orders.append(order)
        #self.process_trading_events(False)
        #self._new_orders = temp

    @property
    def open_orders(self):
        """ 未成交的订单 """
        return list(self.blotter.open_orders)

    def all_positions(self):
        """ 返回所有持仓列表 [Position] """
        return list(six.itervalues(self.blotter.positions))

    def position(self, direction='long', symbol=None):
        """ 合约当前持仓仓位。

        Args:
            direction (str/int): 持仓方向。多头 - 'long' / 1 ；空头 - 'short'  / 2
            , 默认为多头。

            symbol (str): 字符串合约，默认为None表示主合约。

        Returns:
            Position. 该合约的持仓
        """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能查询当前持仓！')
        direction = Direction.arg_to_type(direction)
        contract = Contract(symbol) if symbol else \
            self.contract
        # @TODO assert direction
        try:
            poskey = PositionKey(contract, direction)
            return self.blotter.positions[poskey]
        except KeyError:
            return None

    def pos(self, direction='long', symbol=None):
        """  合约的当前可平仓位。

        Args:
            direction (str/int): 持仓方向。多头 - 'long' / 1 ；空头 - 'short'  / 2
            , 默认为多头。

            symbol (str): 字符串合约，默认为None表示主合约。

        Returns:
            int. 该合约的持仓数目。
        """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能查询当前持仓！')
        direction = Direction.arg_to_type(direction)
        # @TODO symbol xxxxx
        contract = Contract(symbol) if symbol else \
            self.contract
        # @TODO assert direction
        try:
            poskey = PositionKey(contract, direction)
            return self.blotter.positions[poskey].closable
        except KeyError:
            return 0

    def cash(self):
        """ 现金。 """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能查询可用资金！')
        return self.blotter.holding['cash']

    def equity(self):
        """ 当前权益 """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能查询当前权益！')
        return self.blotter.holding['equity']

    def profit(self, contract=None):
        """ 当前持仓的历史盈亏 """
        # if not self.on_bar:
            # log.warn('只有on_bar函数内能查询总盈亏！')
            # return
        pass

    def day_profit(self, contract=None):
        """ 当前持仓的浮动盈亏 """
        #if not self.on_bar:
            #log.warn('只有on_bar函数内能查询浮动盈亏！')
            #return
        pass

    def test_cash(self):
        """  当根bar时间终点撮合后的可用资金，用于测试。 """
        self.process_trading_events(at_baropen=False)
        return self.cash()

    def test_equity(self):
        """  当根bar时间终点撮合后的权益，用于测试。 """
        self.process_trading_events(at_baropen=False)
        return self.equity()
