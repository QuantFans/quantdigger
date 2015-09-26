# -*- coding: utf-8 -*-
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.indicators.common import MA, BOLL
from quantdigger.kernel.engine.strategy import TradingStrategy
from quantdigger.util import  pcontract, stock
from quantdigger.digger import deals
import plotting
import random
import pdb

import ds163

code = '600331'

class DemoStrategy(TradingStrategy):
    """ 策略实例 """
    def __init__(self, exe):
        super(DemoStrategy, self).__init__(exe)
        print 'start: ', self.datetime[0]

        self.mabase = MA(self, self.close, 100,'mabase', 'r', '1')
        self.mabig = MA(self, self.close, 10,'mabig', 'b', '1')
        self.masmall = MA(self, self.close, 5,'masmall', 'y', '1')
        self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')
        self.stoploss = None
        self.num_cont = 0
        self.num_stoploss = 0
        self.num_win = 0

    def __determine_position(self):
        P = 10  # 最少交易股数，这里假设是10
        quantity = int(self.cash() / self.open / P) * P
        return quantity

    def on_bar(self):
        """ 策略函数，对每根Bar运行一次。"""
        if self.volume == 0: return # 这天没有成交量，跳过
        if self.position() == 0 and self.masmall[2] <= self.mabig[2] and self.masmall[1] > self.mabig[1]:
            quantity = self.__determine_position()
            if quantity > 0:
                self.buy('long', self.open, quantity, contract = code)
                self.buy_price = self.open
                self.num_cont += 1
                print 'buy', self.datetime[0].date(), self.open, quantity
        elif self.position() > 0 and self.masmall[1] < self.mabig[1]:
            self.sell('long', self.open, self.position())
            print 'sel', self.datetime[0].date(), self.open, self.position()
            if self.open > self.buy_price:
                self.num_win += 1

if __name__ == '__main__':
    pcon = stock(code)
    simulator = ExecuteUnit([pcon], None, '2015-07-01',
                            # 使用自定义的数据源
                            datasource=ds163.Stock163Source())
    algo = DemoStrategy(simulator)
    simulator.run()
    #print 'close: ', algo.close.data
    #print 'close length: ', algo.close.length_history
    print 'total: %s, win: %s, stoploss: %s' % (algo.num_cont, algo.num_win, algo.num_stoploss)

    # 显示回测结果
    a = {}
    b = []
    try:
        for trans in algo.blotter.transactions:
            deals.update_positions(a, b, trans);
    except Exception, e:
        print e
    plotting.plot_result(simulator.data[pcon], algo._indicators, b, algo.blotter)

