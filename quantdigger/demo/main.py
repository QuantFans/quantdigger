# -*- coding: utf8 -*-
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.indicators.common import MA, BOLL
from quantdigger.kernel.engine.strategy import TradingStrategy
from quantdigger.util import  pcontract, stock
import plotting
#from quantdigger.kernel.engine.series import NumberSeries

#def average(series, n):
    #""" 一个可选的平均线函数 """ 
    ### @todo plot element
    #sum_ = 0
    #for i in range(0, n):
        #sum_ += series[i]
    #return sum_ / n


class DemoStrategy(TradingStrategy):
    """ 策略实例 """
    def __init__(self, exe):
        super(DemoStrategy, self).__init__(exe)

        self.ma20 = MA(self, self.close, 20,'ma20', 'b', '1')
        self.ma10 = MA(self, self.close, 10,'ma10', 'y', '1')
        self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')
        #self.ma2 = NumberSeries(self)

    def on_bar(self):
        """ 策略函数，对每根Bar运行一次。""" 
        #self.ma2.update(average(self.open, 10))
        if self.ma10[1] < self.ma20[1] and self.ma10 > self.ma20:
            self.buy('long', self.open, 1, contract = 'IF000.SHFE') 
        elif self.position() > 0 and self.ma10[1] > self.ma20[1] and self.ma10 < self.ma20:
            self.sell('long', self.open, 1) 

        # 夸品种数据引用
        print self.open_(1)[1], self.open
        #print self.position(), self.cash()
        #print self.datetime, self.b_upper, self.b_middler, self.b_lower

try:
    begin_dt, end_dt = None, None
    pcon = pcontract('IF000.SHFE', '10.Minute')
    #pcon = stock('600848')
    simulator = ExecuteUnit([pcon, pcon], begin_dt, end_dt)
    algo = DemoStrategy(simulator)
    #algo2 = DemoStrategy(simulator)
    simulator.run()

    # 显示回测结果
    plotting.plot_result(simulator.data[pcon],
                                algo._indicators,
                                algo.blotter.deal_positions,
                                algo.blotter)
    
except Exception, e:
    print e

#plotting.plot_result(simulator.data[pcon],
            #algo2._indicators,
            #algo2.blotter.deal_positions,
            #algo2.blotter)
