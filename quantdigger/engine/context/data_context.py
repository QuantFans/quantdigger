# -*- coding: utf-8 -*-

import datetime
import six
from collections import namedtuple

from quantdigger.engine.series import NumberSeries, DateTimeSeries, SeriesBase
from quantdigger.technicals.base import TechnicalBase
from quantdigger.util import log
from quantdigger.datastruct import Bar, PContract


PContractData = namedtuple("PContractData", "s_pcontract original derived")


class DataRef(object):
    """
    """
    def __init__(self, data: "Dict((strpcon, DataFrame))"):
        self._all_pcontract_data = {}
        self._pcontract_data = None
        self.ticks = {}  # Contract -> float
        self.bars = {}   # Contract -> Bar
        self._tranform_data(data)
        self.default_pcontract: str = None

    @property
    def original(self):
        return self._pcontract_data.original

    @property
    def derived(self):
        return self._pcontract_data.derived

    def get_technicals(self, s_pcontract: str):
        return self.get_data(s_pcontract).derived.technicals

    def get_data(self, s_pcontract: str):
        return self._all_pcontract_data[s_pcontract]

    def switch_to_default_pcontract(self):
        self.switch_to_pcontract(self.default_pcontract)

    def _tranform_data(self, data: "Dict((strpcon, DataFrame))"):
        for s_pcontract, raw_data in six.iteritems(data):
            original = OriginalData(PContract.from_string(s_pcontract),
                                    raw_data)
            derived = DerivedData()
            pcontract_data = PContractData(s_pcontract, original, derived)
            self._all_pcontract_data[s_pcontract] = pcontract_data
            # PContract -- 'IF000.SHEF-10.Minutes'
            # 简化策略用户的合约输入。
            symbol_exchange = s_pcontract.split('-')[0]
            same_contracts = list(filter(
                lambda x: x.startswith(symbol_exchange), data.keys()))
            if len(same_contracts) == 1:
                self._all_pcontract_data[symbol_exchange] = pcontract_data
            symbol = s_pcontract.split('.')[0]
            num_same_contract = list(filter(
                lambda x: x.startswith(symbol), data.keys()))
            if len(same_contracts) == 1:
                self._all_pcontract_data[symbol] = pcontract_data

    def switch_to_pcontract(self, s_pcontract):
        self._pcontract_data = self._all_pcontract_data[s_pcontract]

    def datetime_aligned(self, context_dt):
        return (self.original.datetime[0] <= context_dt and
                self.original.next_datetime <= context_dt)

    def rolling_forward(self, context_dt_update_func):
        if self.original.has_pending_data:
            context_dt_update_func(self.original.next_datetime)
            return True
        hasnext, data = self.original.rolling_forward()
        if not hasnext:
            return False
        context_dt_update_func(self.original.next_datetime)
        return True

    def update_derived_vars(self):
        """ 更新用户在策略中定义的变量, 如指标等。 """
        self.derived.update_vars(self.original._curbar)

    def update_original_vars(self):
        """ 更新用户在策略中定义的变量, 如指标等。 """
        original = self.original
        original.update_vars()
        self.ticks[original.contract] = original.close[0]
        self.bars[original.contract] = original.bar
        oldbar = self.bars.setdefault(original.contract, original.bar)
        if original.bar.datetime > oldbar.datetime:
            # 处理不同周期时间滞后
            self.bars[original.contract] = original.bar

    def add_item(self, name, value):
        self.derived.add_item(name, value)


class RollingHelper(object):
    """ 数据源包装器，使相关数据源支持逐步读取操作 """

    def __init__(self, max_length):
        self.curbar = -1
        self._max_length = max_length

    def __len__(self):
        return self._max_length

    def rolling_forward(self):
        """ 读取下一个数据"""
        self.curbar += 1
        if self.curbar == self._max_length:
            self.curbar -= 1
            return False, self.curbar
        else:
            return True, self.curbar


class OriginalData(object):
    """ A DataContext expose data should be visited by multiple strategie.
    which including bars of specific PContract.
    """
    def __init__(self, pcontract, raw_data):
        self.open = NumberSeries(raw_data.open.values, 'open')
        self.close = NumberSeries(raw_data.close.values, 'close')
        self.high = NumberSeries(raw_data.high.values, 'high')
        self.low = NumberSeries(raw_data.low.values, 'low')
        self.volume = NumberSeries(raw_data.volume.values, 'volume')
        self.datetime = DateTimeSeries(raw_data.index, 'datetime')
        self.bar = Bar(None, None, None, None, None, None)
        self.has_pending_data = False
        self.next_datetime = datetime.datetime(2100, 1, 1)
        self.size = len(raw_data.close)
        self.pcontract = pcontract
        self._curbar = -1
        self._helper = RollingHelper(len(raw_data))
        self._raw_data = raw_data

    @property
    def raw_data(self):
        return self._helper.data

    @property
    def curbar(self):
        return self._curbar + 1

    @property
    def contract(self):
        return self.pcontract.contract

    def update_vars(self):
        self._curbar = self._next_bar
        self.open.update_curbar(self._curbar)
        self.close.update_curbar(self._curbar)
        self.high.update_curbar(self._curbar)
        self.low.update_curbar(self._curbar)
        self.volume.update_curbar(self._curbar)
        self.datetime.update_curbar(self._curbar)
        self.bar = Bar(self.datetime[0], self.open[0], self.close[0],
                       self.high[0], self.low[0], self.volume[0])

    def rolling_forward(self):
        """ Retrieve data of next step """
        self.has_pending_data, self._next_bar = self._helper.rolling_forward()
        if not self.has_pending_data:
            return False, None
        self.next_datetime = self._raw_data.index[self._next_bar]
        if self.datetime[0] >= self.next_datetime and self.curbar != 0:
            log.error('合约[%s] 数据时间逆序或冗余' % self.pcontract)
            raise
        return True, self.has_pending_data

    def __len__(self):
        return len(self._helper)


class DerivedData(object):
    def __init__(self):
        self._series = {}
        self._technicals = {}
        self._all_vars = {}

    @property
    def technicals(self):
        return self._technicals

    def __getattr__(self, name):
        if name in ["_series", "_technicals", "_all_vars"]:
            return self.__getattribute__(name)
        else:
            return self._all_vars[name]

    def add_item(self, name, value):
        if name in self._all_vars:
            log.warning("Atrribute [{0}] exist!".format(name))
        self._all_vars[name] = value
        if isinstance(value, SeriesBase):
            self._series[name] = value
        elif isinstance(value, TechnicalBase):
            self._technicals[name] = value

    def update_vars(self, curbar):
        for s in self._series.values():
            s.update_curbar(curbar)
            s.duplicate_last_element()
        for tec in self._technicals.values():
            if tec.is_multiple:
                for s in tec.series.values():
                    s.update_curbar(curbar)
            else:
                for s in tec.series:
                    s.update_curbar(curbar)
