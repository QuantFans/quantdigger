# -*- coding: utf-8 -*-
import Queue
import pandas as pd
from datetime import datetime
from quantdigger.datasource.data import data_manager
#from quantdigger.errors import DataAlignError
from quantdigger.engine.strategy import BarTracker
from quantdigger.engine.context import Context, DataContext
from quantdigger.engine.event import Event
from quantdigger.engine import series
from quantdigger.indicators.base import IndicatorBase

class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个策略同时运行。
        每个执行单元都可能跟踪多个数据(策略用到的周期合约数据集合)。
        其中第一个合约为"主合约" 。 每个执行器可加载多个策略,只要数据需求不超过pcontracts。

        :ivar dt_begin: 策略执行的时间起点。
        :ivar dt_end: 策略执行的时间终点。
        :ivar pcontracts: 策略用到的周期合约数据集合。
        :ivar trackers: 策略用到的跟踪器集合。（和周期合约一一对应）
        :ivar _strategies: 策略集合。
        :ivar datasource: 数据源。

    """
    def __init__(self, pcontracts, dt_start=datetime(1980,1,1),
                 dt_end=datetime(2100,1,1), window_size=0):
        series.g_rolling = False if window_size == 0 else True
        series.g_window = window_size
        self.dt_start = dt_start
        self.dt_end = dt_end
        self._window_size = window_size
        # 不同周期合约数据。
        self.data = { }     # PContract -> DataWrapper
        self.pcontracts = pcontracts
        self.trackers = []
        self._strategies = []
        self._context = Context(self)
        # 每个周期合约对应一个跟跟踪器。
        for pcon in pcontracts:
            self.load_data(pcon, dt_start, dt_end)
            BarTracker(self, pcon) # cursor

    def _init_strategies(self):
        for pcon, dcontext in self.data.iteritems():
            # switch context
            self._context.switch_to(pcon)
            for s in self._strategies:
                s.on_init(self._context)
                for attr, value in self._context.__dict__.iteritems():
                    if isinstance(value, series.SeriesBase):
                        dcontext.add_series(attr, value)
                    elif isinstance(value, IndicatorBase):
                        dcontext.add_indicator(attr, value)

    def add_strategy(self, strategies):
        """ 添加策略组合组合
        
        Args:
            algos (list): 一个策略组合
        
        """
        self._strategies = strategies

    def add_tracker(self, tracker):
        """ 添加跟踪器。 """
        self.trackers.append(tracker)

    def run(self):
        # 初始化策略自定义时间序列变量
        print 'runing strategies..' 
        self._init_strategies()
        print 'on_bars..' 
        for bar_index in xrange(0, self._data_length):
            # todo 对单策略优化
            for pcon, data in self.data.iteritems():
                # switch context
                self._context.switch_to(pcon)
                self._context.update_context(bar_index)
                # 策略遍历
                for s in self._strategies:
                    s.on_bar(self._context)
                # 
            for s in self._strategies:
                # on_cycle
                pass

    def run2(self):
        """""" 
        print 'running...'
        bar_index = 0
        while bar_index < self._data_length:
            #
            latest_bars = { }
            try:
                for tracker in self.trackers:
                    bar = tracker.update_curbar(bar_index)
                    latest_bars[tracker._main_contract] = bar
                # 在回测中无需MARKET事件。
                # 这样可以加速回测速度。
                for algo in self._strategies:
                    bar = algo.update_curbar(bar_index)
                    algo.exchange.update_datetime(bar.datetime)
                    algo.blotter.update_datetime(bar.datetime)
                    latest_bars[algo._main_contract] = bar
                    algo.blotter.update_bar(latest_bars)
                    #algo.exchange.make_market(bar)
                    # 对新的价格运行算法。
                    algo.execute_strategy()
                    while True:
                       # 事件处理。 
                        try:
                            event = algo.events_pool.get()
                        except Queue.Empty:
                            break
                        except IndexError:
                            break
                        else:
                            if event is not None:
                                #if event.type == 'MARKET':
                                    #strategy.calculate_signals(event)
                                    #port.update_timeindex(event)
                                if event.type == Event.SIGNAL:
                                    algo.blotter.update_signal(event)

                                elif event.type == Event.ORDER:
                                    algo.exchange.insert_order(event)

                                elif event.type == Event.FILL:
                                    # 模拟交易接口收到报单成交
                                    algo.blotter.api.on_transaction(event)
                        # 价格撮合。note: bar价格撮合要求撮合置于运算后面。
                        algo.exchange.make_market(bar)

            except Exception, e:
                print(e)
                raise
            bar_index += 1

    def load_data(self, pcontract, dt_start=datetime(1980,1,1), dt_end=datetime(2100,1,1)):
        """ 加载周期合约数据
        
        Args:
            pcontract (PContract): 周期合约
            dt_start(datetime): 开始时间
            dt_end(datetime): 结束时间
        
        Returns:
            pd.DataFrame. k线数据
        """
        try:
            return self.data[str(pcontract)]
        except KeyError:
            ## @todo 时间对齐，长度确认
            data = data_manager.load_bars(pcontract, dt_start, self.dt_end, self._window_size)
            self.data[str(pcontract)] = DataContext(data, self._window_size)
            self._data_length = len(data)
            return data

