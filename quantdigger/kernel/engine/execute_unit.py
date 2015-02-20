# -*- coding: utf8 -*-
import Queue
from quantdigger.kernel.datasource import datamanager
from quantdigger.errors import DataAlignError
from event import Event
class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个策略同时运行。"""
    def __init__(self, begin_dt=None, end_dt=None):
        self._trackers = []  # multi algo, multi data
        self._strategies = []
        self.begin_dt = begin_dt
        self.end_dt = end_dt
        self.data = { }     # PContract -> pandas.DataFrame
        # 如果begin_dt, end_dt 等于None，做特殊处理。
        # accociate with a mplot widget
        #tracker.pcontracts
        #for pcontract in pcontracts:
            #pass
            ## load data

    def run(self):
        """""" 
        print 'running...'
        curbar = 0
        while curbar < self._data_length:
            print "=====================================" 
            for tracker in self._trackers:
                pass
            # 在回测中无需MARKET事件。
            # 这样可以加速回测速度。
            for algo in self._strategies:
                bar = algo.update_curbar(curbar)
                algo.exchange.update_datetime(bar.datetime)
                algo.blotter.update_datetime(bar.datetime)
                # 价格撮合。
                algo.exchange.make_market(bar)
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

            curbar += 1
            

    def load_data(self, pcontract):
        try:
            return self.data[pcontract]
        except KeyError:
            data = datamanager.local_data.load_data(pcontract)
            if not hasattr(self, '_data_length'):
                self._data_length = len(data) 
            elif self._data_length != len(data):
                raise DataAlignError

            self.data[pcontract] = data
            return data


    def add_tracker(self, tracker):
        pass


    def add_strategy(self, strategy):
        strategy.prepare_execution(self)
        self._strategies.append(strategy)

        for pcontract in strategy.pcontracts:
            self.load_data(pcontract)


def plot_result(price_data, signals):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from quantdigger.plugin.mplotwidgets import techmplot
    from quantdigger.plugin.mplotwidgets import widgets
    from quantdigger.kernel.indicators.sys_indicator import *


    #price_data, entry_x, entry_y, exit_x, exit_y, colors = get_stock_signal_data()
    colors = [(1,0,0,1) if price_data.close[i] > price_data.open[i] else (0,1,0,1) for i in xrange(len(price_data))]

    fig = plt.figure()
    frame = techmplot.TechMPlot(fig,
                                price_data,
                                50          # 窗口显示k线数量。
                                )

    # 添加k线和交易信号。
    kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
    frame.add_widget(0, kwindow, True)
    #signal = TradingSignal(None, zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), c=colors, lw=2)
    #frame.add_indicator(0, signal)

    # 添加指标
    ma = frame.add_indicator(0, MA(None, price_data.close, 20, 'MA20', 'simple', 'y', 2))
    frame.add_indicator(0, MA(None, price_data.close, 30, 'MA30', 'simple', 'b', 2))
    frame.draw_window()


    # at most 5 ticks, pruning the upper and lower so they don't overlap
    # with other ticks
    #ax_volume.yaxis.set_major_locator(techmplot.MyLocator(5, prune='both'))

    # sharex 所有所有的窗口都移动

    plt.show()

if __name__ == '__main__':
    from strategy import DemoStrategy
    from quantdigger.kernel.datastruct import PContract, Contract, Period
    begin_dt, end_dt = None, None
    pcontract = PContract(Contract('SHFE', 'IF000'), Period('Minutes', 10))
    algo = DemoStrategy([pcontract])
    simulator = ExecuteUnit(begin_dt, end_dt)
    simulator.add_strategy(algo)
    simulator.run()
    plot_result(simulator.data[pcontract], None)
