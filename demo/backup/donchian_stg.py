#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quantdigger.indicators.common import MA, BOLL
from quantdigger.engine.strategy import TradingStrategy
import pdb
import fw

class DonChianStrategy(TradingStrategy):
    '''唐奇安通道策略'''
    def __init__(self, exe):
        super(DonChianStrategy, self).__init__(exe)
        print 'start: ', self.datetime[0]
        self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')
        self.num_cont = 0
        self.num_win = 0

    def __get_position_size(self, price):
        P = 10  # 最少交易股数，这里假设是10
        quantity = int(self.cash() / price / P) * P
        return quantity

    def on_bar(self):
        """ 策略函数，对每根Bar运行一次。"""
        if self.volume == 0: return # 这天没有成交量，跳过
        IN = 20
        OUT = 10
        price = self.close[0]
        upper = max([self.close[i] for i in range(0, IN)])
        down = min([self.close[i] for i in range(0, OUT)])
        if self.position() == 0 and self.high >= upper:
            quantity = self.__get_position_size(price)
            if quantity > 0:
                self.buy('long', price, quantity)
                self.buy_price = price
                self.num_cont += 1
                #print 'buy', self.datetime[0].date(), price, quantity
        elif self.position() > 0 and self.low <= down:
            self.sell('long', price, self.position())
            #print 'sel', self.datetime[0].date(), price, self.position()
            #print '---'
            if price > self.buy_price:
                self.num_win += 1


if __name__ == '__main__':
    import sys
    code = sys.argv[1]
    fw.run(DonChianStrategy, code)
