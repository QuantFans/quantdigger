# -*- coding: utf-8 -*-
##
# @file data_context.py
# @brief
# @author wondereamer
# @version 0.1
# @date 2016-11-27

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
)

class StrategyContext(object):
    """ 策略组合

    :ivar name: 策略名
    :ivar blotter: 订单管理
    :ivar exchange: 价格撮合器
    :ivar marks: 绘图标志集合
    """
    def __init__(self, name, settings={}):
        self.events_pool = EventsPool()
        # @TODO merge blotter and exchange
        self.blotter = SimpleBlotter(name, self.events_pool, settings)
        self.exchange = Exchange(name, self.events_pool, strict=True)
        self.name = name
        # 0: line_marks, 1: text_marks
        self.marks = [{}, {}]
        self._orders = []
        self._datetime = None
        self._cancel_now = False  # 是当根bar还是下一根bar撤单成功。

    def update_environment(self, dt, ticks, bars):
        """ 更新模拟交易所和订单管理器的数据，时间,持仓 """
        self.blotter.update_datetime(dt)
        self.exchange.update_datetime(dt)
        self.blotter.update_data(ticks, bars)
        self._datetime = dt
        return

    def process_trading_events(self, at_baropen):
        """ 提交订单，撮合，更新持仓 """
        if self._orders:
            self.events_pool.put(SignalEvent(self._orders))
        if not self._orders:
            # 没有交易信号，确保至少运行一次
            self.events_pool.put(OnceEvent())
        self._process_trading_events(at_baropen)
        self._orders = []

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

    def plot_line(self, name, ith_window, x, y, styles, lw=1, ms=10, twinx=False):
        """ 绘制曲线

        Args:
            name (str): 标志名称
            ith_window (int): 在第几个窗口显示，从1开始。
            x (datetime): 时间坐标
            y (float): y坐标
            styles (str): 控制颜色，线的风格，点的风格
            lw (int): 线宽
            ms (int): 点的大小
        """
        mark = self.marks[0].setdefault(name, [])
        mark.append((ith_window, twinx, x, y, styles, lw, ms))

    def plot_text(self, name, ith_window, x, y, text, color='black', size=15, rotation=0):
        """ 绘制文本

        Args:
            name (str): 标志名称
            ith_window (int): 在第几个窗口显示，从1开始。
            x (float): x坐标
            y (float): y坐标
            text (str): 文本内容
            color (str): 颜色
            size (int): 字体大小
            rotation (float): 旋转角度
        """
        mark = self.marks[1].setdefault(name, [])
        mark.append((ith_window, x, y, text, color, size, rotation))

    def buy(self, price, quantity, price_type, contract):
        self._orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.KAI,
            Direction.LONG,
            float(price),
            quantity
        ))

    def sell(self, price, quantity, price_type, contract):
        self._orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.PING,
            Direction.LONG,
            float(price),
            quantity
        ))

    def short(self, price, quantity, price_type, contract):
        self._orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.KAI,
            Direction.SHORT,
            float(price),
            quantity
        ))

    def cover(self, price, quantity, price_type, contract):
        self._orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.PING,
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
                # @TODO or self._orders ?
                # 结合实盘考虑, 实盘可能自动撤单。
                self._orders.append(norder)
            return
        ## 立即处理撤单
        #temp = copy.deepcopy(self._orders)
        #self._orders = []
        #for order in orders:
            #order.side = TradeSide.CANCEL
            #self._orders.append(order)
        #self.process_trading_events(False)
        #self._orders = temp

    @property
    def open_orders(self):
        """ 未成交的订单 """
        return self.blotter.open_orders

    def all_positions(self):
        return list(six.itervalues(self.blotter.positions))

    def position(self, contract, direction):
        try:
            poskey = PositionKey(contract, direction)
            return self.blotter.positions[poskey]
        except KeyError:
            return None

    def pos(self, contract, direction):
        try:
            poskey = PositionKey(contract, direction)
            return self.blotter.positions[poskey].closable
        except KeyError:
            return 0

    def cash(self):
        return self.blotter.holding['cash']

    def equity(self):
        return self.blotter.holding['equity']

    def profit(self, contract):
        pass

    def day_profit(self, contract):
        """ 当前持仓的浮动盈亏 """
        pass
