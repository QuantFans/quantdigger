# -*- coding: utf8 -*-
import numpy as np

from quantdigger.datastruct import (
    Order,
    Bar,
    TradeSide,
    Direction,
    Contract,
    PriceType
)

from quantdigger.engine.exchange import Exchange
from quantdigger.engine.event import SignalEvent
from quantdigger.engine.series import NumberSeries, DateTimeSeries
from quantdigger.util import engine_logger as logger

from blotter import SimpleBlotter
from event import EventsPool

class CrossTrackerMixin(object):
    """ 夸品种数据引用。

        索引为0表示主合约。索引大于1表示夸品种数据引用。
        用于套利等策略。
    """
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
    

class BarTracker(object):
    """ 跟踪器，可能是策略，策略用到的非主合约数据，独立指标。 
    
    :ivar events_pool: 事件池。
    :ivar blotter: 订单本地处理器。
    :ivar exchange: 模拟交易所。
    :ivar _excution: 最小执行单元。
    :ivar _series: 当前跟踪器负责维护的时间序列变量集合。
    :ivar _main_pcontract: 主合约。即self.open等指向的合约。
    :ivar open: 主合约当前Bar的开盘价。
    :ivar close: 主合约当前Bar的收盘价。
    :ivar high: 主合约当前Bar的最高价。
    :ivar low: 主合约当前Bar的最低价。
    :ivar volume: 主合约当前Bar的成交量。
    :ivar datetime: 主合约当前Bar的开盘时间。
    :ivar curbar: 当前Bar索引。
    """
    def __init__(self, exe_unit, pcontract=None):
        """ 初始化数据列表
        
        Args:
            pcontract (PContract): 周期合约, 空表示仅是跟踪器，非策略。
        
        """
        self.events_pool = EventsPool()
        self.blotter = SimpleBlotter(None, self.events_pool)
        self.exchange = Exchange(self.events_pool, strict=False)

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
        """ tick数据到达时候触发。 """
        pass

    def on_bar(self):
        """ Bar数据到达时候触发。""" 
        pass

    def execute_strategy(self):
        self.on_tick()
        self.on_bar()

    def add_series(self, series):
        """ 添加时间序列变量。

        每个跟踪器都要维护策略使用的时间序列变量，当新的Bar数据
        到达后，通过BarTracker.update_curbar函数更新时间序列变量的最
        后一个值。
        """
        self._series.append(series)

    def update_curbar(self, index):
        """ 新的bar数据到达时，更新相关信息,
        如其负责维护的时间序列对象变量的最新值。
        
       :param int index: 当前bar索引。
       :return: 最新的Bar对象。
       :rtype: Bar
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


class TradingStrategy(BarTracker, CrossTrackerMixin):
    """ 策略的基类。

    负责维护用到的时间序列变量和夸品种数据引用,
    下单，查询等。
    """
    def __init__(self, exe):
        super(TradingStrategy, self).__init__(exe, pcontract=None)
        self._indicators = []
        self._orders = []

    def add_indicator(self, indic):
        self._indicators.append(indic)

    def execute_strategy(self):
        super(TradingStrategy, self).execute_strategy()
        # 一次策略循环可能产生多个委托单。
        if self._orders:
            self.events_pool.put(SignalEvent(self._orders))
        self._orders = []

    def buy(self, direction, price, quantity, price_type='LMT', contract=None):
        """ 开仓。
        
           :param str/int direction: 下单方向。多头 - 'long' / 1 ；空头 - 'short'  / 2
           :param float price: 价格。
           :param int quantity: 数量。
           :param str/int price_type: 下单价格类型。限价单 - 'lmt' / 1；市价单 - 'mkt' / 2
        """
        contract = None
        con = Contract(contract) if contract else self._main_contract
        self._orders.append(Order(
                self.datetime,
                con,
                PriceType.arg_to_type(price_type),
                TradeSide.KAI,
                Direction.arg_to_type(direction),
                float(price),
                quantity
        ))

    def sell(self, direction, price, quantity, price_type='MKT', contract=None):
        """ 平仓。
        
           :param str/int direction: 下单方向。多头 - 'long' / 1 ；空头 - 'short'  / 2
           :param float price: 价格。
           :param int quantity: 数量。
           :param str/int price_type: 下单价格类型。限价单 - 'lmt' / 1；市价单 - 'mkt' / 2
        """
        con = Contract(contract) if contract else self._main_contract
        self._orders.append(Order(
                self.datetime,
                con,
                PriceType.arg_to_type(price_type),
                TradeSide.PING,
                Direction.arg_to_type(direction),
                float(price),
                quantity
        ))

    def position(self, contract=None):
        """ 当前仓位。
        
           :param str contract: 字符串合约，默认为None表示主合约。
           :return: 该合约的持仓数目。
           :rtype: int
        """
        try:
            if not contract:
                contract = self._main_contract
            return self.blotter.current_positions[contract].quantity
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
        """ 除了完成父类函数BarTracker.update_curbar的操作外,
            还计算策略用到的指标如MA的最新值。

           :param int index: 当前Bar索引。
           :return: Bar数据。
           :rtype: Bar
           :raises SeriesIndexError: 如果时间序列索引出错。
        """
        
        bar = super(TradingStrategy, self).update_curbar(index)
        for indicator in self._indicators:
            indicator.calculate_latest_element()
        return bar
