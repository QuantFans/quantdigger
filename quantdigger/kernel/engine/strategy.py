# -*- coding: utf8 -*-
import numpy as np

from quantdigger.kernel.datastruct import Order, Bar
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

    
class BarTracker(Simulator):
    def __init__(self, pcontracts, exe):
        """ 初始化数据列表
        
        每个Tracker都可能跟踪多个数据。
        其中第一个合约为@主合约
        Args:
            pcontracts (PContract list): 周期合约列表，长度至少唯一。
        
        """
        super(BarTracker, self).__init__()
        self._excution = None
        # 如果一次性给出所有合约，加载可以更快。
        self.pcontracts = pcontracts
        self._series = []
        try:
            self._main_pcontract = self.pcontracts[0]
            self._main_contract = self._main_pcontract.contract
        except KeyError:
            ## @todo 提醒用户用法。
            raise KeyError
        self._container_day = np.zeros(shape=(self.length_day(self._main_pcontract), ), dtype = float)
        exe.add_strategy(self)

    def length_day(self, pcontract):
        """ 计算当天的数据量 """ 
        ## @todo local_data
        return 4

    def set_pcontracts(self, pcontracts):
        """ 在用户类的初始化中可被调用。 """
        ## @todo property, set
        self.pcontracts = pcontracts

    def prepare_execution(self, exe):
        """ 数据加载，关键数据变量初始化, 设置执行器。
        
        Args:
            exe (ExecuteUnit): 执行器。
        
        """
        self._excution = exe
        for pcontract in self.pcontracts:
            self.get_data(pcontract)
        self._init_main_data(self._main_pcontract)


    @property
    def container_day(self):
        return self._container_day

    def _init_main_data(self, pcontract):
        data = self.get_data(pcontract)
        # 预留了历史和当天的数据空间。
        self.open = NumberSeries(self, data.open, True)
        self.close = NumberSeries(self, data.close, True)
        self.high = NumberSeries(self, data.high, True)
        self.low = NumberSeries(self, data.low, True)
        self.volume = NumberSeries(self, data.volume, True)
        self.datetime = DateTimeSeries(self, data.index, True)
        self.curbar = 0

    def get_data(self, pcontract):
        return self._excution.load_data(pcontract)

    def on_tick(self):
        """""" 
        pass

    def execute_strategy(self):
        self.on_tick()

    def add_series(self, series):
        self._series.append(series)


class TradingStrategy(BarTracker):
    """ 策略的基类 """
    def __init__(self, pcontracts, exe):
        super(TradingStrategy, self).__init__(pcontracts, exe)
        self._indicators = []
        self._orders = []

    def add_indicator(self, indic):
        self._indicators.append(indic)

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

        for indicator in self._indicators:
            indicator.calculate_latest_element()
        return Bar(self.datetime[0],
                   self.open[0], self.close[0],
                   self.high[0], self.low[0],
                   self.volume[0])

    def execute_strategy(self):
        self.on_tick()
        if self._orders:
            self.generate_signals_event()
        self._orders = []

    def generate_signals_event(self):
        self.events_pool.put(SignalEvent(self._orders))

    def buy(self, direction, price, quantity, deal_type='limit'):
        """ 开仓
        
        Args:
            direction (str): 多头('d'), 或者空头('k')
            quantity (int): 数量
            price (float): 价格
            deal_type (str): 下单方式，限价单('limit'), 市价单('market')
        """
        self._orders.append(Order(
                self.datetime,
                self._main_contract,
                deal_type,
                'k',
                direction,
                float(price),
                quantity
        ))

    def sell(self, direction, price, quantity, deal_type='limit'):
        """ 平仓
        
        Args:
            direction (str): 多头('d'), 或者空头('k')
            quantity (int): 数量
            price (float): 价格
            deal_type (str): 下单方式，限价单('limit'), 市价单('market')
        """
        self._orders.append(Order(
                self.datetime,
                self._main_contract,
                deal_type,
                'p',
                direction,
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
