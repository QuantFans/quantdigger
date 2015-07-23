# -*- coding: utf8 -*-
import Queue
import pandas as pd
from quantdigger.kernel.datasource.data import local_data
from quantdigger.errors import DataAlignError
from quantdigger.kernel.engine.strategy import BarTracker
from quantdigger.kernel.engine.event import Event
class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个策略同时运行。
        每个执行单元都可能跟踪多个数据(策略用到的周期合约数据集合)。
        其中第一个合约为"主合约" 。 每个执行器可加载多个策略,只要数据需求不超过pcontracts。

        :ivar begin_dt: 策略执行的时间起点。
        :vartype begin_dt: datetime
        :ivar end_dt: 策略执行的时间终点。
        :vartype end_dt: datetime
        :ivar pcontracts: 策略用到的周期合约数据集合。
        :vartype pcontracts: list
        :ivar trackers: 策略用到的跟踪器集合。（和周期合约一一对应）
        :vartype trackers: list
        :ivar _strategies: 策略集合。
        :vartype _strategies: list

    """
    def __init__(self, pcontracts, begin_dt=None, end_dt=None):
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
        
        self.load_data(pcontracts[0])
        # 每个周期合约对应一个跟跟踪器。
        for pcon in pcontracts[1:]:
            self.load_data(pcon)
            BarTracker(self, pcon)

    def run(self):
        """""" 
        print 'running...'
        bar_index = 0
        while bar_index < self._data_length:
            #
            latest_bars = { }
            print bar_index
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
                                    algo.exchange.update_order(event)

                                elif event.type == Event.FILL:
                                    algo.blotter.update_fill(event)
                        # 价格撮合。note: bar价格撮合要求撮合置于运算后面。
                        algo.exchange.make_market(bar)

            except Exception, e:
                print(e)
                raise
            bar_index += 1

    def load_data(self, pcontract):
        """ 加载周期合约数据
        
           :param PContract pcontract: 周期合约。
           :return: 周期合约数据。
           :rtype: pandas.DataFrame
        """
        try:
            return self.data[pcontract]
        except KeyError:
            data = local_data.load_data(pcontract)
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
