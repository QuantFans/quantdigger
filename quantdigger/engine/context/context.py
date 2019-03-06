# -*- coding: utf-8 -*-
import six
import datetime

from quantdigger.engine.series import SeriesBase
from quantdigger.util import MAX_DATETIME
from quantdigger.engine.series import DateTimeSeries

from .data_context import DataRef
from .plotter import PlotterDelegator
from .trading import TradingDelegator


class Context(PlotterDelegator, TradingDelegator):
    """ 上下文"""
    def __init__(self, data: "dict((s_pcon, DataFrame))",
                 name, settings, strategy, max_window):
        TradingDelegator.__init__(self, name, settings)
        PlotterDelegator.__init__(self)

        self.dt_series = DateTimeSeries([MAX_DATETIME] * max_window,
                                            'universal_time')
        self.aligned_dt = datetime.datetime(2100, 1, 1)
        self.aligned_bar_index = 0
        self.strategy_name = name
        self.on_bar = False
        self.strategy = strategy
        self.data_ref = DataRef(data)

    def process_trading_events(self, at_baropen):
        super().update_environment(
            self.aligned_dt, self.data_ref.ticks, self.data_ref.bars)
        super().process_trading_events(at_baropen)

    def update_datetime(self, next_dt):
        self.dt_series.curbar = self.aligned_bar_index
        self.aligned_dt = min(self.data_ref.original.next_datetime,
                                self.aligned_dt)
        try:
            self.dt_series.data[self.aligned_bar_index] = self.aligned_dt
        except IndexError:
            self.dt_series.data.append(self.aligned_dt)

    def __getitem__(self, strpcon):
        """ 获取跨品种合约 """
        return self.data_ref._all_pcontract_data[strpcon.upper()].original

    def __getattr__(self, name):
        original = self.data_ref.original
        derived = self.data_ref._pcontract_data.derived
        if hasattr(original, name):
            return getattr(original, name)
        elif hasattr(derived, name):
            return getattr(derived, name)

    def __setattr__(self, name, value):
        if name in [
                'dt_series', 'strategy',
                '_trading', 'on_bar', 'aligned_bar_index', 'aligned_dt',
                'marks', 'blotter', 'exchange', '_new_orders', '_datetime',
                '_cancel_now', 'events_pool', 'data_ref',
                'strategy_name'
        ]:
            super(Context, self).__setattr__(name, value)
        else:
            if isinstance(value, SeriesBase):
                value.reset_data([], self.data_ref.original.size)
            self.data_ref.add_item(name, value)

    @property
    def pcontract(self):
        """ 当前周期合约 """
        return self.data_ref.original.pcontract

    @property
    def contract(self):
        """ 当前合约 """
        return self.data_ref.original.pcontract.contract

    @property
    def symbol(self):
        """ 当前合约 """
        return str(self.contract)

    @property
    def curbar(self):
        """ 当前是第几根k线, 从1开始 """
        if self.on_bar:
            return self.aligned_bar_index + 1
        else:
            return self.data_ref.original.curbar

    @property
    def open(self):
        """ k线开盘价序列 """
        return self.data_ref.original.open

    @property
    def close(self):
        """ k线收盘价序列 """
        return self.data_ref.original.close

    @property
    def high(self):
        """ k线最高价序列 """
        return self.data_ref.original.high

    @property
    def low(self):
        """ k线最低价序列 """
        return self.data_ref.original.low

    @property
    def volume(self):
        """ k线成交量序列 """
        return self.data_ref.original.volume

    @property
    def datetime(self):
        """ k线时间序列 """
        if self.on_bar:
            return self.dt_series
        else:
            return self.data_ref.original.datetime

