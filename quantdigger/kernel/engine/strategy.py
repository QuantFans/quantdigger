# -*- coding: utf8 -*-
from quantdigger.kernel.engine.series import NumberSeries
import numpy as np
from blotter import SimpleBlotter
from pool import EventPool
from broker import SimulateBroker
from event import OrderEvent

class Simulator(object):
    """docstring for Simulator"""
    def __init__(self):
        self.events_pool = EventPool()
        self.blotter = SimpleBlotter(None, self.events_pool)
        self.broker = SimulateBroker(self.events_pool)

    
class BarTracker(Simulator):
    def __init__(self, pcontracts):
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
        except KeyError:
            ## @todo 提醒用户用法。
            raise KeyError
        self._container_day = np.zeros(shape=(self.length_day(self._main_pcontract), ), dtype = float)


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
        self.init_trading()


    def init_trading(self):
        raise NotImplementedError
        

    @property
    def container_day(self):
        return self._container_day

    def _init_main_data(self, pcontract):
        data = self.get_data(pcontract)
        self.open = NumberSeries(self, data.open, True)
        self.close = NumberSeries(self, data.close, True)
        self.high = NumberSeries(self, data.high, True)
        self.low = NumberSeries(self, data.low, True)
        self.volume = NumberSeries(self, data.volume, True)
        self.curbar = 0


    def get_data(self, pcontract):
        return self._excution.load_data(pcontract)

    def on_tick(self):
        """""" 
        pass

    def add_series(self, series):
        self._series.append(series)


class TradingStrategy(BarTracker):
    """docstring for TradingStrategy"""
    def __init__(self, pcontracts):
        super(TradingStrategy, self).__init__(pcontracts)
        self._indicators = []


    def add_indicator(self, indic):
        self._indicators.append(indic)


    def update_curbar(self, index):
        """ 更新当前bar索引。

        更新注册过的serie变量的索引，
        计算系列指标中的最新值。
        
        Args:
            index (int.): 当前bar索引。
        
        Raises:
            SerieIndexError
        """
        self.curbar = index
        self.open.update_curbar(index)
        self.close.update_curbar(index)
        self.high.update_curbar(index)
        self.low.update_curbar(index)
        self.volume.update_curbar(index)

        for serie in self._series:
            serie.update_curbar(index)
            serie.duplicate_last_element()

        for indicator in self._indicators:
            indicator.calculate_latest_element()


    def order(self):
        """docstring for order""" 
        #self.events_pool.put()
        #OrderEvent
        pass


def average(series, n):
    """""" 
    sum_ = 0
    for i in range(0, n):
        sum_ += series[i]
    return sum_ / n


from quantdigger.kernel.indicators.sys_indicator import *
class DemoStrategy(TradingStrategy):
    def __init__(self, pcontracts):
        super(DemoStrategy, self).__init__(pcontracts)


    def init_trading(self):
        self.ma = MA(self, self.open, 2)
        self.ma2 = NumberSeries(self)


    def on_tick(self):
        """""" 
        self.ma2.update(average(self.open, 2))

        print self.open, self.ma2, self.ma
        #print self.ma

        #for v in self.ma._serie._data:
            #print v
        #assert False
        pass
