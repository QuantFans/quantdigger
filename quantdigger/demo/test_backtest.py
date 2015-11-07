# -*- coding: utf-8 -*-
from quantdigger.engine.execute_unit import ExecuteUnit
from quantdigger.indicators.common import MA, BOLL
from quantdigger.engine.strategy import TradingStrategy
from quantdigger.util import  pcontract, stock
from quantdigger.digger import deals
import plotting

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
        print 'start: ', self.datetime[0]

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
        #print self.position(), self.cash()
        #print self.datetime, self.b_upper, self.b_middler, self.b_lower
        #print self.datetime[0]

if __name__ == '__main__':
    try:
        pcon = pcontract('BB.SHFE', '1.Minute')
        #begin_dt, end_dt = '2015-05-25', '2015-06-01'
        #pcon = stock('600848','10.Minute')  # 通过tushare下载股票数据
        simulator = ExecuteUnit([pcon, pcon])
        algo = DemoStrategy(simulator)
        #algo1 = DemoStrategy(simulator)
        #algo2 = DemoStrategy(simulator)
        simulator.run()


        # 显示回测结果
        from quantdigger.datastruct import TradeSide
        ping = 0
        kai = 0
        for t in algo.blotter.transactions:
            if t.side == TradeSide.PING:
                ping += t.quantity
            elif t.side == TradeSide.KAI:
                kai += t.quantity
            else:
                raise "error" 
        print "ping: ", ping
        print "kai: ", kai
        assert kai >= ping

