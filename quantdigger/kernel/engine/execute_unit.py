# -*- coding: utf8 -*-
import Queue
import pandas as pd
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
        # 不同周期合约数据。
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
            for tracker in self._trackers:
                pass
            # 在回测中无需MARKET事件。
            # 这样可以加速回测速度。
            for algo in self._strategies:
                bar = algo.update_curbar(curbar)
                algo.exchange.update_datetime(bar.datetime)
                algo.blotter.update_datetime(bar.datetime)
                # ## @todo 未来支持多个合约。
                algo.blotter.update_bar({algo._main_contract: bar})
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
            data['row'] = pd.Series(xrange(0, len(data.index)), index=data.index)
            self.data[pcontract] = data
            return data


    def add_tracker(self, tracker):
        pass


    def add_strategy(self, strategy):
        strategy.prepare_execution(self)
        self._strategies.append(strategy)

        for pcontract in strategy.pcontracts:
            self.load_data(pcontract)


#def plot_result(price_data, indicators, signals, blotter):
    #import matplotlib
    #matplotlib.use('TkAgg')
    #import matplotlib.pyplot as plt
    #from quantdigger.plugin.mplotwidgets import techmplot
    #from quantdigger.plugin.mplotwidgets import widgets
    #from quantdigger.kernel.indicators.common import *

    ##price_data, entry_x, entry_y, exit_x, exit_y, colors = data.get_stock_signal_data()
    ##print zip(zip(entry_x,entry_y),zip(exit_x,exit_y))
    ##assert False

    #fig = plt.figure()
    #frame = techmplot.TechMPlot(fig,
                                #price_data,
                                #50          # 窗口显示k线数量。
                                #)

    ## 添加k线
    #kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
    #frame.add_widget(0, kwindow, True)
    ## 交易信号。
    #signal = TradingSignalPos(None, price_data, signals, lw=2)
    #frame.add_indicator(0, signal)

    ## 添加指标
    #k_axes, = frame
    #for indic in indicators:
        #indic.plot(k_axes)
    #frame.draw_window()


    ## at most 5 ticks, pruning the upper and lower so they don't overlap
    ## with other ticks
    ##ax_volume.yaxis.set_major_locator(techmplot.MyLocator(5, prune='both'))

    ## sharex 所有所有的窗口都移动

    #fig2 = plt.figure()
    #ax = fig2.add_axes((0.1, 0.1, 0.9, 0.9))
    #ax.plot(blotter.equity_curve.total)
    #plt.show()

#def pcontract(exchange, contract, time_unit, unit_count):
    #""" 构建周期合约结构的便捷方式。
    
    #Args:
        #exchange (str): 交易所
        #contract (str): 合约
        #time_unit (str): 时间单位
        #unit_count (int): 时间数目
    
    #Returns:
        #int. The result
    #Raises:
    #"""
    #"""docstring for pco""" 
    #return PContract(Contract(exchange, contract),
                     #Period(time_unit, unit_count))

#if __name__ == '__main__':
    #from strategy import DemoStrategy
    #from quantdigger.kernel.datastruct import PContract, Contract, Period

    #begin_dt, end_dt = None, None
    #pcon = pcontract('SHFE', 'IF000', 'Minutes', 10)
    #algo = DemoStrategy([pcon])
    #simulator = ExecuteUnit(begin_dt, end_dt)
    #simulator.add_strategy(algo)
    #simulator.run()

    #blotter = algo.blotter
    #blotter.create_equity_curve_dataframe()
    #print blotter.output_summary_stats()

    #plot_result(simulator.data[pcon], algo._indicators,
            #algo.blotter.deal_positions, blotter)
