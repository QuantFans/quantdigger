# -*- coding: utf8 -*-
import Queue
from quantdigger.kernel.datasource import datamanager
from quantdigger.errors import DataAlignError
from event import Event
class ExecuteUnit(object):
    """"""
    def __init__(self, begin_dt=None, end_dt=None):
        self._trackers = []  # multi algo, multi data
        self._strategies = []
        self.begin_dt = begin_dt
        self.end_dt = end_dt
        self._data = { }     # PContract -> pandas.DataFrame
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
            for algo in self._strategies:
                algo.update_curbar(curbar)
            
                algo.blotter.update_timeindex(curbar)
                algo.on_tick()

                while True:
                    # 事件处理。在回测中无需MARKET事件。
                    # 这样可以加速回测速度。
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

                            if event.type == Event.MARKET:
                                algo.blotter.update_signal(event)

                            elif event.type == Event.ORDER:
                                algo.broker.execute_order(event)

                            elif event.type == Event.FILL:
                                algo.blotter.update_fill(event)

            curbar += 1
            

    def load_data(self, pcontract):
        try:
            return self._data[pcontract]
        except KeyError:
            data = datamanager.local_data.load_data(pcontract)
            if not hasattr(self, '_data_length'):
                self._data_length = len(data) 
            elif self._data_length != len(data):
                raise DataAlignError

            self._data[pcontract] = data
            return data


    def add_tracker(self, tracker):
        pass


    def add_strategy(self, strategy):
        strategy.prepare_execution(self)
        self._strategies.append(strategy)

        for pcontract in strategy.pcontracts:
            self.load_data(pcontract)


if __name__ == '__main__':
    from strategy import DemoStrategy
    from quantdigger.kernel.datastruct import PContract, Contract, Period
    #from quantdigger import datastruct
    begin_dt, end_dt = None, None

    pcontract = PContract(Contract('SHFE', 'IF000'), Period('Minutes', 10))
    algo = DemoStrategy([pcontract])
    simulator = ExecuteUnit(begin_dt, end_dt)
    simulator.add_strategy(algo)
    simulator.run()
