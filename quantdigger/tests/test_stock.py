# -*- coding: utf-8 -*-
##
# @file test_blotter.py
# @brief 测试模拟器的价格撮合, 当前持仓，权益，可用资金等。
# @author wondereamer
# @version 0.3
# @date 2015-01-06


import datetime
import unittest
import pandas as pd
import os
import talib
import numpy as np
from quantdigger.datastruct import TradeSide, Contract
from quantdigger import *
from logbook import Logger
logger = Logger('test')
window_size = 0
capital = 200000
OFFSET = 0.6
buy1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
buy2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
buy3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
sell1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
sell2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
sell3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()
fname = os.path.join(os.getcwd(), 'data', 'stock.TEST-1.Minute.csv')
source = pd.read_csv(fname, parse_dates=True, index_col=0)


class TestOneDataOneCombinationStock(unittest.TestCase):
    """ 测试股票单数据单组合的价格撮合，持仓查询／默认持仓查询，可用资金等交易接口 """
        
    def test_case(self):
        t_cashes0, t_cashes1 = [], []

        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [buy1, buy2, buy3]:
                    ctx.buy(ctx.close, 1) 
                else:
                    if ctx.pos() >= 2 and curtime == sell1:
                        ctx.sell(ctx.close, 2) 
                    elif ctx.pos() >= 1 and curtime == sell2:
                        ctx.sell(ctx.close, 1) 
                ## 前一根的交易信号在当前价格撮合后的可用资金
                t_cashes0.append(ctx.test_cash()) 


        class DemoStrategy2(Strategy):
            """ 限价买多卖空的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [buy1, buy2, buy3]:
                    ctx.buy(ctx.close, 1) 
                    ctx.short(ctx.close, 2) 
                else:
                    if curtime == sell1:
                        if ctx.pos() >= 3:
                            # quantity == 6, closable == 3
                            assert(ctx.pos() == 3 and '默认持仓查询测试失败！')
                            ctx.sell(ctx.close, 2) 
                        if ctx.pos('short') >= 6:
                            assert(ctx.pos('short') == 6 and '默认持仓查询测试失败！')
                            ctx.cover(ctx.close, 4) 
                    elif curtime == sell2:
                        if ctx.pos() >= 1:
                            ctx.sell(ctx.close, 1) 
                        if ctx.pos('short') >= 2:
                            ctx.cover(ctx.close, 2) 
                t_cashes1.append(ctx.test_cash()) 


        class DemoStrategy3(Strategy):
            """ 测试平仓未成交时的持仓，撤单后的持仓，撤单。 """
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                return
                
        set_symbols(['stock.TEST-1.Minute'], window_size)
        profile = add_strategy([DemoStrategy1('A1'), DemoStrategy2('A2'), DemoStrategy3('A3')], {
            'capital': capital,
            'ratio': [0.3, 0.3, 0.4]
            })
        run()
        # all_holdings, cash()
        all_holdings = profile.all_holdings()
        all_holdings0 = profile.all_holdings(0)
        all_holdings1 = profile.all_holdings(1)
        all_holdings2 = profile.all_holdings(2)
        self.assertTrue(len(source) > 0 and len(source) ==  len(all_holdings), '模拟器测试失败！')
        lmg = Contract.long_margin_ratio('stock.TEST')
        multi = Contract.volume_multiple('stock.TEST')
        smg = Contract.short_margin_ratio('stock.TEST')
        s_equity0, s_cashes0, dts = holdings_buy_maked_curbar(source, capital*0.3, lmg, multi)
        self.assertTrue(len(t_cashes0) == len(s_cashes0), 'cash接口测试失败！')
        for i in range(0, len(t_cashes0)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(t_cashes0[i],s_cashes0[i]), 'cash接口测试失败！')
        self.assertTrue(len(all_holdings) == len(s_equity0), 'all_holdings接口测试失败！')
        for i, hd in enumerate(all_holdings0):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], s_equity0[i]), 'all_holdings接口测试失败！')

        #  确保资金够用，所以不影响
        e0, c0, dts = holdings_buy_maked_curbar(source, capital*0.3/2, lmg, multi)
        e1, c1, dts = holdings_short_maked_curbar(source, capital*0.3/2, smg, multi)
        s_equity1 = [x + y for x, y in zip(e0, e1)]
        s_cashes1 = [x + y for x, y in zip(c0, c1)]
        self.assertTrue(len(t_cashes1) == len(s_cashes1), 'cash接口测试失败！')
        for i in range(0, len(t_cashes1)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(t_cashes1[i],s_cashes1[i]), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(np.isclose(s_equity0[i]-capital*0.3,
                                        0-(s_equity1[i]-capital*0.3)), '测试代码错误！')
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], s_equity1[i]), 'all_holdings接口测试失败！')
        for i in range(0, len(profile.all_holdings())):
            hd = all_holdings[i]
            hd0 = all_holdings0[i]
            hd1 = all_holdings1[i]
            hd2 = all_holdings2[i]
            self.assertTrue(hd['cash'] == hd0['cash']+hd1['cash']+hd2['cash'], 
                            'all_holdings接口测试失败！')
            self.assertTrue(hd['commission'] == hd0['commission']+
                    hd1['commission']+hd2['commission'], 'all_holdings接口测试失败！')
            self.assertTrue(hd['equity'] == hd0['equity']+hd1['equity']+hd2['equity'],
                            'all_holdings接口测试失败！')
        # 绘制k线，交易信号线
        #from quantdigger.digger import finance, plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(0))


def holdings_buy_maked_curbar(data, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [buy1, buy2, buy3]
        当天卖出点: [sell1, sell2]
    """ 
    assert(volume_multiple == 1 and long_margin == 1)
    UNIT = 1
    buy_quantity= { }
    poscost = 0
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    for curdt, curprice in data.close.iteritems():
        pos_profit = 0
        curtime = curdt.time()
        curdate = curdt.date()
        if curtime in [buy1, buy2, buy3]:
            buy_quantity.setdefault(curdate, 0)
            quantity = sum(buy_quantity.values())
            poscost = (poscost * quantity + curprice*UNIT) / (quantity+UNIT)
            buy_quantity[curdate] += UNIT
        else:
            if curtime == sell1:
                for posdate, quantity in buy_quantity.iteritems():
                    if posdate < curdate and quantity > 0:
                        close_profit += (curprice-poscost) * 2*UNIT * volume_multiple
                        buy_quantity[posdate] -= 2*UNIT
                    elif posdate > curdate:
                        assert(False)
            elif curtime == sell2:
                for posdate, quantity in buy_quantity.iteritems():
                    if posdate < curdate and quantity > 0:
                        close_profit += (curprice-poscost) * volume_multiple
                        buy_quantity[posdate] -= UNIT
                        assert(buy_quantity[posdate] == 0)
                    elif posdate > curdate:
                        assert(False)
        if curdt == data.index[-1]:
            # 强平现有持仓
            quantity = sum(buy_quantity.values())
            close_profit += (curprice - poscost) * quantity * volume_multiple
            buy_quantity.clear()

        quantity = sum(buy_quantity.values())
        pos_profit += (curprice - poscost) * quantity * volume_multiple
        equities.append(capital+close_profit+pos_profit)
        cost = poscost * quantity * volume_multiple * long_margin
        cashes.append(equities[-1]-cost)
        dts.append(curdt)
    return equities, cashes, dts

def holdings_short_maked_curbar(data, capital, short_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [buy1, buy2, buy3]
        当天卖出点: [sell1, sell2]
    """ 
    assert(volume_multiple == 1 and short_margin == 1)
    UNIT = 2
    short_quantity= { }
    poscost = 0
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    for curdt, curprice in data.close.iteritems():
        pos_profit = 0
        curtime = curdt.time()
        curdate = curdt.date()
        if curtime in [buy1, buy2, buy3]:
            short_quantity.setdefault(curdate, 0)
            quantity = sum(short_quantity.values())
            poscost = (poscost * quantity + curprice*UNIT) / (quantity+UNIT)
            short_quantity[curdate] += UNIT
        else:
            if curtime == sell1:
                for posdate, quantity in short_quantity.iteritems():
                    if posdate < curdate and quantity > 0:
                        close_profit -= (curprice-poscost) * 2*UNIT * volume_multiple
                        short_quantity[posdate] -= 2*UNIT
                    elif posdate > curdate:
                        assert(False)
            elif curtime == sell2:
                for posdate, quantity in short_quantity.iteritems():
                    if posdate < curdate and quantity > 0:
                        close_profit -= (curprice-poscost) * volume_multiple * UNIT
                        short_quantity[posdate] -= UNIT
                        assert(short_quantity[posdate] == 0)
                    elif posdate > curdate:
                        assert(False)
        if curdt == data.index[-1]:
            # 强平现有持仓
            quantity = sum(short_quantity.values())
            close_profit -= (curprice - poscost) * quantity * volume_multiple
            short_quantity.clear()

        quantity = sum(short_quantity.values())
        pos_profit -= (curprice - poscost) * quantity * volume_multiple
        equities.append(capital+close_profit+pos_profit)
        cost = poscost * quantity * volume_multiple * short_margin
        cashes.append(equities[-1]-cost)
        dts.append(curdt)
    return equities, cashes, dts


if __name__ == '__main__':
    unittest.main()
