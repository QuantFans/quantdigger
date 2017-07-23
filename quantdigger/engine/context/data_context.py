# -*- coding: utf-8 -*-

import datetime
import six

from quantdigger.engine.series import SeriesBase, NumberSeries, DateTimeSeries
from quantdigger.technicals.base import TechnicalBase
from quantdigger.util import elogger as logger
from quantdigger.datastruct import Bar


class DataContext(object):
    """ A DataContext expose data should be visited by multiple strategie.
    which including bars of specific PContract, technicals and series of
    strategie.
    """
    def __init__(self, Helper):
        data = Helper.data
        self.open = NumberSeries(data.open.values, 'open')
        self.close = NumberSeries(data.close.values, 'close')
        self.high = NumberSeries(data.high.values, 'high')
        self.low = NumberSeries(data.low.values, 'low')
        self.volume = NumberSeries(data.volume.values, 'volume')
        self.datetime = DateTimeSeries(data.index, 'datetime')
        self.ith_comb = -1   # 第i个组合
        self.ith_strategy = -1   # 第j个策略
        self.bar = Bar(None, None, None, None, None, None)
        self.new_row = False
        self.next_datetime = datetime.datetime(2100, 1, 1)
        self.technicals = [[{}]]

        self._curbar = -1
        self._Helper = Helper
        self._series = [[{}]]
        self._variables = [[{}]]
        self._all_variables = [[{}]]
        self._size = len(data.close)

    @property
    def raw_data(self):
        return self._Helper.data

    @property
    def curbar(self):
        return self._curbar + 1

    @property
    def pcontract(self):
        return self._Helper.pcontract

    @property
    def contract(self):
        return self._Helper.pcontract.contract

    def __getattr__(self, name):
        return self.get_item(name)

    def update_system_vars(self):
        # self.data = np.append(data, tracker.container_day)
        self._curbar = self.last_curbar
        self.open.update_curbar(self._curbar)
        self.close.update_curbar(self._curbar)
        self.high.update_curbar(self._curbar)
        self.low.update_curbar(self._curbar)
        self.volume.update_curbar(self._curbar)
        self.datetime.update_curbar(self._curbar)
        self.bar = Bar(self.datetime[0], self.open[0], self.close[0],
                       self.high[0], self.low[0], self.volume[0])
        self.new_row = False

    def update_user_vars(self):
        # Update series defined by user if exist.
        try:
            series = self._series[self.ith_comb][self.ith_strategy].values()
        except IndexError:
            pass
        else:
            for s in series:
                s.update_curbar(self._curbar)
                s.duplicate_last_element()
        # Update technicals if exist.
        try:
            technicals = self.technicals[self.ith_comb][self.ith_strategy].values()
        except IndexError:
            pass
        else:
            for tec in technicals:
                if tec.is_multiple:
                    for s in six.itervalues(tec.series):
                        s.update_curbar(self._curbar)
                else:
                    for s in tec.series:
                        s.update_curbar(self._curbar)

    def rolling_forward(self):
        """ 滚动读取下一步的数据。 """
        self.new_row, self.last_curbar = self._Helper.rolling_forward()
        if not self.new_row:
            self.last_curbar -= 1
            return False, None
        self.next_datetime = self._Helper.data.index[self.last_curbar]
        if self.datetime[0] >= self.next_datetime and self.curbar != 0:
            logger.error('合约[%s] 数据时间逆序或冗余' % self.pcontract)
            raise
        return True, self.new_row

    def __len__(self):
        return len(self._Helper)

    def get_item(self, name):
        """ 获取用户在策略on_init函数中初始化的变量 """
        return self._all_variables[self.ith_comb][self.ith_strategy][name]

    def add_item(self, name, value):
        """ 添加用户初始化的变量。 """
        # @TODO ...
        if self.ith_comb < len(self._all_variables):
            if self.ith_strategy < len(self._all_variables[self.ith_comb]):
                self._all_variables[self.ith_comb][self.ith_strategy][name] = value
            else:
                self._all_variables[self.ith_comb].append({name: value})
        else:
            self._all_variables.append([{name: value}])
        if isinstance(value, SeriesBase):
            self.add_series(name, value)
        elif isinstance(value, TechnicalBase):
            self.add_indicator(name, value)
        else:
            self.add_variable(name, value)

    def add_series(self, attr, s):
        """ 添加on_init中初始化的序列变量

        Args:
            attr (str): 属性名
            s (Series): 序列变量
        """
        s.reset_data([], self._size)
        if self.ith_comb < len(self._series):
            if self.ith_strategy < len(self._series[self.ith_comb]):
                self._series[self.ith_comb][self.ith_strategy][attr] = s
            else:
                self._series[self.ith_comb].append({attr: s})
        else:
            self._series.append([{attr: s}])

    def add_indicator(self, attr, indic):
        if self.ith_comb < len(self.technicals):
            if self.ith_strategy < len(self.technicals[self.ith_comb]):
                self.technicals[self.ith_comb][self.ith_strategy][attr] = indic
            else:
                self.technicals[self.ith_comb].append({attr: indic})
        else:
            self.technicals.append([{attr: indic}])

    def add_variable(self, attr, var):
        if self.ith_comb < len(self._variables):
            if self.ith_strategy < len(self._variables[self.ith_comb]):
                self._variables[self.ith_comb][self.ith_strategy][attr] = var
            else:
                self._variables[self.ith_comb].append({attr: var})
        else:
            self._variables.append([{attr: var}])


class DataContextAttributeHelper(object):
    """"""
    def __init__(self, data):
        self.data = data

    def __setattr__(self, name, value):
        if name == 'data':
            super(DataContextAttributeHelper, self).__setattr__(name, value)
            return

        data = self.data
        if name in data._all_variables[data.ith_comb][data.ith_strategy]:
            data.add_item(name, value)

    def __getattr__(self, name):
        return getattr(self.data, name)
