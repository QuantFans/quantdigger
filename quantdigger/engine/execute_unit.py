# -*- coding: utf-8 -*-
import Queue
import pandas as pd
from datetime import datetime
from quantdigger.datasource.data import data_manager
from quantdigger.errors import DataAlignError
from quantdigger.engine.strategy import BarTracker
from quantdigger.engine.event import Event
class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个策略同时运行。
        每个执行单元都可能跟踪多个数据(策略用到的周期合约数据集合)。
        其中第一个合约为"主合约" 。 每个执行器可加载多个策略,只要数据需求不超过pcontracts。

        :ivar begin_dt: 策略执行的时间起点。
        :ivar end_dt: 策略执行的时间终点。
        :ivar pcontracts: 策略用到的周期合约数据集合。
        :ivar trackers: 策略用到的跟踪器集合。（和周期合约一一对应）
        :ivar _strategies: 策略集合。
        :ivar datasource: 数据源。

    """
    def __init__(self, pcontracts, begin_dt=datetime(1970,1,1),
                 end_dt=datetime(2100,1,1)):
        self.begin_dt = begin_dt
        self.end_dt = end_dt
        # 不同周期合约数据。
        self.data = { }     # PContract -> pandas.DataFrame
        self.pcontracts = pcontracts
        self.trackers = []
        self._strategies = []

        # 如果begin_dt, end_dt 等于None，做特殊处理。
        # accociate with a mplot widget
        #tracker.pcontracts
        
        self.load_data(pcontracts[0], begin_dt, end_dt)
        # 每个周期合约对应一个跟跟踪器。
        for pcon in pcontracts[1:]:
            self.load_data(pcon, begin_dt, end_dt)
            BarTracker(self, pcon)

    def run(self):
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

    def load_data(self, pcontract, dt_start=datetime(1970,1,1), dt_end=datetime(2100,1,1)):
        """ 加载周期合约数据
        
        Args:
            pcontract (PContract): 周期合约
            dt_start(datetime): 开始时间
            dt_end(datetime): 结束时间
        
        Returns:
            pd.DataFrame. k线数据
        """
        try:
            return self.data[pcontract]
        except KeyError:
            data = data_manager.load_bars(pcontract, self.begin_dt, self.end_dt)
            if not hasattr(self, '_data_length'):
                self._data_length = len(data) 
            elif self._data_length != len(data):
                raise DataAlignError
            data['row'] = pd.Series(xrange(0, len(data.index)), index=data.index)
            self.data[pcontract] = data
            return data

    def add_tracker(self, tracker):
        """ 添加跟踪器。 """
        self.trackers.append(tracker)

    def add_strategy(self, strategy):
        """ 添加策略。 """
        self._strategies.append(strategy)
