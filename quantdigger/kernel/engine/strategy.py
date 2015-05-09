# -*- coding: utf8 -*-
import numpy as np

from quantdigger.kernel.datastruct import Order, Bar, TradeSide, Direction, Contract
from quantdigger.kernel.engine.exchange import Exchange
from quantdigger.kernel.engine.event import SignalEvent
from quantdigger.kernel.engine.series import NumberSeries, DateTimeSeries
from quantdigger.util import engine_logger as logger

from blotter import SimpleBlotter
from event import EventsPool

class Simulator(object):
    """docstring for Simulator"""
    def __init__(self):
        self.events_pool = EventsPool()
        self.blotter = SimpleBlotter(None, self.events_pool)
        self.exchange = Exchange(self.events_pool, strict=False)

class CrossTrackerMixin(object):
    """ 跨跟踪器数据引用 """
    def open_(self, index):
        assert(index >= 0)
        if index == 0:
            return self.open 
        else:
            return self._excution.trackers[index-1].open

    def close_(self, index):
        assert(index >= 0)
        if index == 0:
            return self.close 
        else:
            return self._excution.trackers[index-1].close

    def high_(self, index):
        assert(index >= 0)
        if index == 0:
            return self.high 
        else:
            return self._excution.trackers[index-1].high

    def low_(self, index):
        assert(index >= 0)
        if index == 0:
            return self.low 
        else:
            return self._excution.trackers[index-1].low

    def volume_(self, index):
        assert(index >= 0)
        if index == 0:
            return self.volume 
        else:
            return self._excution.trackers[index-1].volume

    def datetime_(self, index):
        assert(index >= 0)
        if index == 0:
            return self.datetime 
        else:
            return self._excution.trackers[index-1].datetime
    

class BarTracker(Simulator):
    """ 跟踪器，可能是策略，策略用到的非主合约数据，独立指标。 """
    def __init__(self, exe_unit, pcontract=None):
        """ 初始化数据列表
        
        Args:
            pcontract (PContract): 周期合约, 非空表示跟踪器，非策略。
        
        """
        super(BarTracker, self).__init__()
        self._excution = exe_unit
        # tracker中用到的时间序列
        self._series = []
        try:
            if pcontract:
                self._main_pcontract = pcontract 
                exe_unit.add_tracker(self)
            else:
                self._main_pcontract = exe_unit.pcontracts[0]
                exe_unit.add_strategy(self)
            self._main_contract = self._main_pcontract.contract
            self._data = exe_unit.data[self._main_pcontract]
            self._container_day = np.zeros(shape=(self.length_day(self._main_pcontract), ), dtype = float)
            self._init_main_data()
        except KeyError:
            ## @todo 提醒用户用法。
            raise KeyError

    def length_day(self, pcontract):
        """ 计算当天的数据量 """ 
        ## @todo local_data
        return 4


    @property
    def container_day(self):
        """ 为当天数据预留的空间  """
        return self._container_day

    def _init_main_data(self):
        # 预留了历史和当天的数据空间。
        self.open = NumberSeries(self, self._data.open, True)
        self.close = NumberSeries(self, self._data.close, True)
        self.high = NumberSeries(self, self._data.high, True)
        self.low = NumberSeries(self, self._data.low, True)
        self.volume = NumberSeries(self, self._data.volume, True)
        self.datetime = DateTimeSeries(self, self._data.index, True)
        self.curbar = 0

    def on_tick(self):
        """""" 
        pass

    def execute_strategy(self):
        self.on_tick()

    def add_series(self, series):
        self._series.append(series)

    def _open(self, pcon):
        """docstring for open""" 
        #self.open = NumberSeries(self, _data.open, True)
        #self.close = NumberSeries(self, _data.close, True)
        #self.high = NumberSeries(self, _data.high, True)
        #self.low = NumberSeries(self, _data.low, True)
        #self.volume = NumberSeries(self, _data.volume, True)
        pass

    def update_curbar(self, index):
        """ 更新当前bar索引。

        更新注册过的serie变量的索引，
        计算系列指标中的最新值。
        
        Args:
            index (int): 当前bar索引。
        
        Raises:
            SeriesIndexError
        """
        self.curbar = index
        self.open.update_curbar(index)
        self.close.update_curbar(index)
        self.high.update_curbar(index)
        self.low.update_curbar(index)
        self.volume.update_curbar(index)
        self.datetime.update_curbar(index)

        for serie in self._series:
            serie.update_curbar(index)
            serie.duplicate_last_element()

        return Bar(self.datetime[0],
                   self.open[0], self.close[0],
                   self.high[0], self.low[0],
                   self.volume[0])

direction_map = {
        'long': Direction.LONG,
        'short': Direction.SHORT }

class TradingStrategy(BarTracker, CrossTrackerMixin):
    """ 策略的基类 """
    def __init__(self, exe):
        super(TradingStrategy, self).__init__(exe, pcontract=None)
        self._indicators = []
        self._orders = []

    def add_indicator(self, indic):
        self._indicators.append(indic)

    def execute_strategy(self):
        self.on_tick()
        if self._orders:
            self.events_pool.put(SignalEvent(self._orders))
        self._orders = []

    def buy(self, direction, price, quantity, deal_type='limit', contract=None):
        """ 开仓
        
        Args:
            direction (str): 多头('long'), 或者空头('short')
            quantity (int): 数量
            price (float): 价格
            deal_type (str): 下单方式，限价单('limit'), 市价单('market')
        """
        contract = None
        con = Contract(contract) if contract else self._main_contract

        self._orders.append(Order(
                self.datetime,
                con,
                deal_type,
                TradeSide.KAI,
                direction_map[direction.lower()],
                float(price),
                quantity
        ))

    def sell(self, direction, price, quantity, deal_type='limit', contract=None):
        """ 平仓
        
        Args:
            direction (str): 多头('d'), 或者空头('k')
            quantity (int): 数量
            price (float): 价格
            deal_type (str): 下单方式，限价单('limit'), 市价单('market')
        """
        con = Contract(contract) if contract else self._main_contract
        self._orders.append(Order(
                self.datetime,
                con,
                deal_type,
                TradeSide.PING,
                direction_map[direction.lower()],
                float(price),
                quantity
        ))

    def position(self, contract=None):
        """ 当前仓位。 """
        try:
            if not contract:
                contract = self._main_contract
            return self.blotter.current_positions[contract].total
        except KeyError:
            return 0

    def cash(self):
        """ 现金。 """
        return self.blotter.current_holdings['cash']

    def equity(self):
        """ 当前权益 """
        return self.blotter.current_holdings['equity']

    def profit(self, contract=None):
        """ 当前持仓的历史盈亏 """ 
        pass

    def day_profit(self, contract=None):
        """ 当前持仓的浮动盈亏 """ 
        pass


    def update_curbar(self, index):
        """ 更新当前bar索引。

        更新注册过的serie变量的索引，
        计算系列指标中的最新值。
        
        Args:
            index (int): 当前bar索引。
        
        Raises:
            SeriesIndexError
        """
        bar = super(TradingStrategy, self).update_curbar(index)
        for indicator in self._indicators:
            indicator.calculate_latest_element()
        return bar
