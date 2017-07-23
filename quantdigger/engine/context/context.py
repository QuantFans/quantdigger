# -*- coding: utf-8 -*-
##
# @file data.py
# @brief 数据上下文，交易上下文。
# @author wondereamer
# @version 0.2
# @date 2015-12-09

import six
import datetime

from quantdigger.datastruct import (
    Direction,
    PriceType,
    Contract,
)
from quantdigger.engine.series import DateTimeSeries
from quantdigger.engine.context.data_context import DataContextAttributeHelper


class Context(object):
    """ 上下文"""
    def __init__(self, data, max_window):
        self.ctx_dt_series = DateTimeSeries(
            [datetime.datetime(2100, 1, 1)] * max_window,
            'universal_time')
        self.ctx_datetime = datetime.datetime(2100, 1, 1)
        self.ctx_curbar = 0  # update by ExecuteUnit

        self.on_bar = False  # pass to on_bar function or on_symbol function
        self._strategy_contexts = []
        self._cur_strategy_context = None
        self._cur_data_context = None
        self._data_contexts = {}       # str(PContract): DataContext
        for key, value in six.iteritems(data):
            self._data_contexts[key] = value
            self._data_contexts[key.split('-')[0]] = value
            self._data_contexts[key.split('.')[0]] = value
        # latest price data
        # Contract -> float
        # Contract -> Bar
        self._ticks = {}
        self._bars = {}

    def add_strategy_context(self, ctxs):
        self._strategy_contexts.append(ctxs)

    def switch_to_pcontract(self, pcon):
        self._cur_data_context = self._data_contexts[pcon]

    def switch_to_strategy(self, ith_comb, ith_strategy):
        self._cur_strategy_context = self._strategy_contexts[ith_comb][ith_strategy]
        if self.on_bar:
            for data_context in six.itervalues(self._data_contexts):
                data_context.ith_comb, data_context.ith_strategy = ith_comb, ith_strategy
        else:
            self._cur_data_context.ith_comb, self._cur_data_context.ith_strategy = ith_comb, ith_strategy

    def time_aligned(self):
        return (self._cur_data_context.datetime[0] <= self.ctx_datetime and
                self._cur_data_context.next_datetime <= self.ctx_datetime)
        # 第一根是必须运行
        # return  (self._cur_data_context.datetime[0] <= self.ctx_dt_series and
                # self._cur_data_context.ctx_dt_series <= self.ctx_dt_series) or \
                # self._cur_data_context.curbar == 0

    def rolling_forward(self):
        """ 更新最新tick价格，最新bar价格, 环境时间。 """
        if self._cur_data_context.new_row:
            self.ctx_dt_series.curbar = self.ctx_curbar
            self.ctx_datetime = min(self._cur_data_context.next_datetime,
                                    self.ctx_datetime)
            try:
                self.ctx_dt_series.data[self.ctx_curbar] = min(
                    self._cur_data_context.next_datetime, self.ctx_datetime)
            except IndexError:
                self.ctx_dt_series.data.append(
                    min(self._cur_data_context.next_datetime, self.ctx_datetime))
            return True
        hasnext, data = self._cur_data_context.rolling_forward()
        if not hasnext:
            return False
        self.ctx_dt_series.curbar = self.ctx_curbar
        try:
            self.ctx_dt_series.data[self.ctx_curbar] = min(
                self._cur_data_context.next_datetime, self.ctx_datetime)
        except IndexError:
            self.ctx_dt_series.data.append(min(
                self._cur_data_context.next_datetime, self.ctx_datetime))
        self.ctx_datetime = min(
            self._cur_data_context.next_datetime, self.ctx_datetime)
        return True

    def update_user_vars(self):
        """ 更新用户在策略中定义的变量, 如指标等。 """
        self._cur_data_context.update_user_vars()

    def update_system_vars(self):
        """ 更新用户在策略中定义的变量, 如指标等。 """
        self._cur_data_context.update_system_vars()
        self._ticks[self._cur_data_context.contract] = \
            self._cur_data_context.close[0]
        self._bars[self._cur_data_context.contract] = \
            self._cur_data_context.bar
        oldbar = self._bars.setdefault(
            self._cur_data_context.contract, self._cur_data_context.bar)
        if self._cur_data_context.bar.datetime > oldbar.datetime:
            # 处理不同周期时间滞后
            self._bars[self._cur_data_context.contract] = \
                self._cur_data_context.bar

    def process_trading_events(self, at_baropen):
        self._cur_strategy_context.update_environment(
            self.ctx_datetime, self._ticks, self._bars)
        self._cur_strategy_context.process_trading_events(at_baropen)

    def __getitem__(self, strpcon):
        """ 获取跨品种合约 """
        return DataContextAttributeHelper(
            self._data_contexts[strpcon.upper()])

    def __getattr__(self, name):
        return self._cur_data_context.get_item(name)

    def __setattr__(self, name, value):
        if name in [
                '_data_contexts', '_cur_data_context', '_cur_strategy_context',
                '_strategy_contexts', 'ctx_dt_series', '_ticks', '_bars',
                '_trading', 'on_bar', 'ctx_curbar', 'ctx_datetime'
        ]:
            super(Context, self).__setattr__(name, value)
        else:
            self._cur_data_context.add_item(name, value)

    @property
    def strategy(self):
        """ 当前策略名 """
        return self._cur_strategy_context.name

    @property
    def pcontract(self):
        """ 当前周期合约 """
        return self._cur_data_context.pcontract

    @property
    def symbol(self):
        """ 当前合约 """
        return str(self._cur_data_context.pcontract.contract)

    @property
    def curbar(self):
        """ 当前是第几根k线, 从1开始 """
        if self.on_bar:
            return self.ctx_curbar + 1
        else:
            return self._cur_data_context.curbar

    @property
    def open(self):
        """ k线开盘价序列 """
        return self._cur_data_context.open

    @property
    def close(self):
        """ k线收盘价序列 """
        return self._cur_data_context.close

    @property
    def high(self):
        """ k线最高价序列 """
        return self._cur_data_context.high

    @property
    def low(self):
        """ k线最低价序列 """
        return self._cur_data_context.low

    @property
    def volume(self):
        """ k线成交量序列 """
        return self._cur_data_context.volume

    @property
    def datetime(self):
        """ k线时间序列 """
        if self.on_bar:
            return self.ctx_dt_series
            # return self._cur_data_context.datetime
        else:
            return self._cur_data_context.datetime

    @property
    def open_orders(self):
        """ 未成交的订单 """
        return list(self._cur_strategy_context.open_orders)

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
            contract = self._cur_data_context.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.buy(price,
                                       quantity, price_type,
                                       contract)

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
            contract = self._cur_data_context.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.sell(price,
                                        quantity, price_type,
                                        contract)

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
            contract = self._cur_data_context.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.short(price,
                                         quantity, price_type,
                                         contract)

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
            contract = self._cur_data_context.contract
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.cover(price,
                                         quantity, price_type,
                                         contract)

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
            self._cur_data_context.contract
        # @TODO assert direction
        return self._cur_strategy_context.position(contract, direction)

    def all_positions(self):
        """ 返回所有持仓列表 [Position] """
        return self._cur_strategy_context.all_positions()

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
            self._cur_data_context.contract
        # @TODO assert direction
        return self._cur_strategy_context.pos(contract, direction)

    def cancel(self, orders):
        """ 撤单 """
        self._cur_strategy_context.cancel(orders)

    def cash(self):
        """ 现金。 """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能查询可用资金！')
        return self._cur_strategy_context.cash()

    def equity(self):
        """ 当前权益 """
        if not self.on_bar:
            raise Exception('只有on_bar函数内能查询当前权益！')
        return self._cur_strategy_context.equity()

    def profit(self, contract=None):
        """ 当前持仓的历史盈亏 """
        # if not self.on_bar:
            # logger.warn('只有on_bar函数内能查询总盈亏！')
            # return
        pass

    def plot_line(self, name, ith_window, x, y, styles, lw=1, ms=10, twinx=False):
        self._cur_strategy_context.plot_line(name, ith_window - 1, x - 1, float(y),
                                            styles, lw, ms, twinx)

    def plot_text(self, name, ith_window, x, y, text, color='black', size=15, rotation=0):
        self._cur_strategy_context.plot_text(name, ith_window-1, x-1, float(y),
                                                text, color, size, rotation)

    def day_profit(self, contract=None):
        """ 当前持仓的浮动盈亏 """
        #if not self.on_bar:
            #logger.warn('只有on_bar函数内能查询浮动盈亏！')
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
