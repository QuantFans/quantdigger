# -*- coding: utf-8 -*-
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.indicators.common import MA, BOLL
from quantdigger.kernel.engine.strategy import TradingStrategy
from quantdigger.util import  pcontract, stock
from quantdigger.digger import deals
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
        print self.open_(1)[1], self.open
        #print self.position(), self.cash()
        #print self.datetime, self.b_upper, self.b_middler, self.b_lower

if __name__ == '__main__':
    try:
        pcon = pcontract('IF000.SHFE', '10.Minute')
        begin_dt, end_dt = None, None
        #begin_dt, end_dt = '2015-05-25', '2015-06-01'
        #pcon = stock('600848','10.Minute')  # 通过tushare下载股票数据
        simulator = ExecuteUnit([pcon, pcon], begin_dt, end_dt)
        algo = DemoStrategy(simulator)
        #algo1 = DemoStrategy(simulator)
        #algo2 = DemoStrategy(simulator)
        simulator.run()

        #for deal in algo.blotter.deal_positions:
            ## code...
            #print("----------------")
            #print("开仓时间: %s；成交价格: %f；买卖方向: %s；成交量: %d；") % \
                #(deal.open_datetime, deal.open_price, Direction.type_to_str(deal.direction), deal.quantity)
            #print("平仓时间: %s；成交价格: %f；买卖方向: %s；成交量: %d；盈亏: %f；") % \
                #(deal.close_datetime, deal.close_price, Direction.type_to_str(deal.direction), deal.quantity, deal.profit())

        # 显示回测结果
        a = {}
        b = []
        try:
            for trans in algo.blotter.transactions:
                deals.update_positions(a, b, trans);
        except Exception, e:
            print e
        plotting.plot_result(simulator.data[pcon],
                                    algo._indicators,
                                    b,
                                    algo.blotter)

        
    except Exception, e:
        import traceback
        print traceback.format_exc()
        #print e

