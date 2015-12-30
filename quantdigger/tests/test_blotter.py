# -*- coding: utf-8 -*-
##
# @file test_blotter.py
# @brief 测试模拟器的价格撮合, 当前持仓，权益，可用资金等。
# @author wondereamer
# @version 0.3
# @date 2015-12-22


import datetime
import unittest
import pandas as pd
import os
import talib
import numpy as np
from logbook import Logger
from quantdigger.engine.qd import *
from quantdigger.datastruct import TradeSide

logger = Logger('test')
window_size = 0
CAPTIAL = 200000
OFFSET = 0.6
buy1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
buy2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
buy3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
sell1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
sell2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
sell3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()
fname = os.path.join(os.getcwd(), 'data', 'blotter.SHFE-1.Minute.csv')
source = pd.read_csv(fname, parse_dates=True, index_col=0)


class TestOneDataOneCombination(unittest.TestCase):
    """ 测试单数据单组合的价格撮合，持仓查询／默认持仓查询，可用资金等交易接口 """
        
    def test_case(self):
        ## @TODO 持仓过夜，不卖，累加仓位。
        # @todo profile
             #signals 盈利

        # @TODO deals DemoStrategy2
        cashes0, cashes1 = [], []

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
                    if curtime == sell1:
                        assert(ctx.position() == 3 and '持仓测试失败！')
                        ctx.sell(ctx.close, 2) 
                    elif curtime == sell2:
                        assert(ctx.position() == 1 and '持仓测试失败！')
                        ctx.sell(ctx.close, 1) 
                ## 前一根的交易信号在当前价格撮合后的可用资金
                cashes0.append(ctx.test_cash()) 


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
                        assert(ctx.position() == 3 and '默认持仓查询测试失败！')
                        ctx.sell(ctx.close, 2) 
                        assert(ctx.position('short') == 6 and '持仓测试失败！')
                        ctx.cover(ctx.close, 4) 
                    elif curtime == sell2:
                        assert(ctx.position('long') == 1 and '持仓测试失败！')
                        ctx.sell(ctx.close, 1) 
                        assert(ctx.position('short') == 2 and '持仓测试失败！')
                        ctx.cover(ctx.close, 2) 
                cashes1.append(ctx.test_cash()) 


        class DemoStrategy3(Strategy):
            """ 测试平仓未成交时的持仓，撤单后的持仓，撤单。 """
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.curbar == 1:
                    ctx.short(138, 1) 
                    ctx.short(138, 1) 
                    ctx.buy(ctx.close, 1)
                elif ctx.curbar == 3:
                    # 保证下一根撤单成功, 而非当前这根。
                    assert(len(ctx.open_orders) == 2 and  '撤单测试失败!')
                    ctx.cancel(ctx.open_orders[0])
                    assert(len(ctx.open_orders) == 2 and '撤单测试失败')
                elif ctx.curbar == 4:
                    assert(len(ctx.open_orders) == 1 and '撤单测试失败！')
                elif ctx.curbar == 5:
                    ctx.sell(300, 1) # 下无法成交的平仓，测试持仓。
                    assert(ctx.position() == 1 and '持仓测试失败!')
                elif ctx.curbar == 7:
                    assert(ctx.position() == 0 and '持仓测试失败!')
                    assert(len(ctx.open_orders) == 2 and '撤单测试失败！')
                    order = filter(lambda x: x.side == TradeSide.PING, ctx.open_orders)[0]
                    ctx.cancel(order)
                elif ctx.curbar == 8:
                    assert(len(ctx.open_orders) == 1 and '撤单测试失败！')
                    assert(ctx.position() == 1 and '持仓测试失败!')
                if ctx.curbar > 1 and ctx.datetime[0].date() != ctx.datetime[1].date():
                    assert(len(ctx.open_orders) == 0 and '隔夜订单清空测试失败')
                

        set_symbols(['blotter.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategy1('A1'), DemoStrategy2('A2'), DemoStrategy3('A3')], {
            'captial': CAPTIAL,
            'ratio': [0.3, 0.3, 0.4]
            })
        run()
        # all_holdings, cash()
        all_holdings = profile.all_holdings()
        all_holdings0 = profile.all_holdings(0)
        all_holdings1 = profile.all_holdings(1)
        all_holdings2 = profile.all_holdings(2)
        self.assertTrue(len(source) > 0 and len(source) ==  len(all_holdings), '模拟器测试失败！')

        target, cashes, dts = holdings_buy_maked_curbar(source, CAPTIAL*0.3)
        self.assertTrue(len(cashes0) == len(cashes), 'cash接口测试失败！')
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes0[i],cashes[i]), 'cash接口测试失败！')
        self.assertTrue(len(all_holdings) == len(target), 'all_holdings接口测试失败！')
        for i, hd in enumerate(all_holdings0):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), 'all_holdings接口测试失败！')

        target2, cashes, dts = holdings_buy_short_maked_curbar(source, CAPTIAL*0.3)
        self.assertTrue(len(cashes1) == len(cashes), 'cash接口测试失败！')
        for i in range(0, len(cashes1)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes1[i],cashes[i]), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(np.isclose(target[i]-CAPTIAL*0.3,
                                        0-(target2[i]-CAPTIAL*0.3)), '测试代码错误！')
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target2[i]), 'all_holdings接口测试失败！')
        for i in range(0, len(profile.all_holdings())):
            hd = all_holdings[i]
            hd0 = all_holdings0[i]
            hd1 = all_holdings1[i]
            hd2 = all_holdings2[i]
            self.assertTrue(hd['cash'] == hd0['cash']+hd1['cash']+hd2['cash'], 
                            'all_holdings接口测试失败！')
            self.assertTrue(hd['commission'] == hd0['commission']+
                    hd1['commission']+hd2['commission'], 'all_holdings接口测试失败！')
            self.assertTrue(hd['equity'] == hd0['equity']+hd1['equity']+hd2['equity'], 'all_holdings接口测试失败！')
            
        # holding
        hd0 = profile.holding(0) 
        hd1 = profile.holding(1) 
        hd2 = profile.holding(2) 
        hd = profile.holding()
        self.assertTrue(hd0['equity']+hd1['equity']+hd2['equity']==hd['equity'],
                        'holdings接口测试失败！')
        self.assertTrue(hd0['cash']+hd1['cash']+hd2['cash']==hd['cash'], 'holdings接口测试失败！')
        self.assertTrue(hd0['commission']+hd1['commission']+hd2['commission']==hd['commission'],
                        'holdings接口测试失败！')
        self.assertTrue(hd0['history_profit']+hd1['history_profit']+hd2['history_profit']==hd['history_profit'],
                        'holdings接口测试失败！')
        hd0last = profile.all_holdings(0)[-1]
        self.assertTrue(hd0last['equity'] == hd0['equity'], 'holdings接口测试失败！')
        self.assertTrue(hd0last['cash'] == hd0['cash'], 'holdings接口测试失败！')
        self.assertTrue(hd0last['commission'] == hd0['commission'], 'holdings接口测试失败！')
        self.assertTrue(len(profile.all_holdings()) == len(target) and
                        len(target) > 0, 'holdings接口测试失败！')
        # 绘制k线，交易信号线
        #from quantdigger.digger import finance, plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(2))


    def test_case2(self):
        """ 测试限价的延迟成交 """
        buy_entries, sell_entries = [], []
        short_entries, cover_entries = [], []
        cashes0, cashes1 = [], []

        class DemoStrategyBuy(Strategy):
            """ 只开多头仓位的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in buy_entries:
                    ctx.buy(ctx.low-OFFSET, 1) 
                # 默认多头
                elif ctx.position() > 0 and ctx.datetime[0].time() == sell1:
                    ctx.sell(ctx.close, ctx.position()) 
                    cashes0.append(ctx.test_cash())
                    return
                cashes0.append(ctx.cash())

        class DemoStrategyShort(Strategy):
            """ 只开空头仓位的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in short_entries:
                    ctx.short(ctx.high+OFFSET, 1) 
                elif ctx.position('short') > 0 and ctx.datetime[0].time() == sell1:
                    ctx.cover(ctx.close, ctx.position('short')) 
                    cashes1.append(ctx.test_cash())
                    return
                cashes1.append(ctx.cash())

        class DemoStrategySell(Strategy):
            """ 只开多头仓位的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == buy1:
                    ctx.buy(ctx.close, 1) 
                elif ctx.position('long') > 0 and ctx.datetime[0] in sell_entries:
                    ctx.sell(ctx.high+OFFSET, ctx.position()) 
                elif ctx.position('long') > 0 and ctx.datetime[0].time() == sell3:
                    ctx.sell(ctx.close, ctx.position()) 

        class DemoStrategyCover(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == buy1:
                    ctx.short(ctx.close, 1) 
                elif ctx.position('short') > 0 and ctx.datetime[0] in cover_entries:
                    ctx.cover(ctx.low-OFFSET, ctx.position('short')) 
                elif ctx.position('short') > 0 and ctx.datetime[0].time() == sell3:
                    ctx.cover(ctx.close, ctx.position('short')) 

        set_symbols(['blotter.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategyBuy('B1'), DemoStrategySell('B2'),
                                DemoStrategyShort('B3'), DemoStrategyCover('B4')],{
                                    'captial': CAPTIAL,
                                    'ratio': [0.25, 0.25, 0.25, 0.25]
                                  })
        buy_entries, sell_entries, short_entries, cover_entries = entries_maked_nextbar(source)
        run()
        # buy
        target, cashes, dts = holdings_buy_maked_nextbar(source, buy_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(0)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(0)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')
        # cash() 终点
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes0[i],cashes[i]), 'cash接口测试失败！')
        # short
        target, cashes, dts = holdings_short_maked_nextbar(source, short_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(2)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(2)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')
        for i in range(0, len(cashes0)-1):
            self.assertTrue(np.isclose(cashes1[i],cashes[i]), 'cash接口测试失败！')
        # sell
        target, dts = holdings_sell_maked_nextbar(source, sell_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(1)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')

        # cover
        target, dts = holdings_cover_maked_nextbar(source, cover_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(3)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(3)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')

        #from quantdigger.digger import plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(3))

        ## @TODO 模拟器make_market的运行次数
        return

    def test_case3(self):
        """ 测试市价成交 """
        cashes0 = []

        class DemoStrategy(Strategy):
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [buy1, buy2, buy3]:
                    ctx.buy(0, 1) 
                    ctx.short(0, 2) 
                else:
                    if curtime == sell1:
                        assert(ctx.position('long') == 3 and '持仓测试失败！')
                        ctx.sell(0, 2) 
                        assert(ctx.position('short') == 6 and '持仓测试失败！')
                        ctx.cover(0, 4) 
                    elif curtime == sell2:
                        assert(ctx.position('long') == 1 and '持仓测试失败！')
                        ctx.sell(0, 1) 
                        assert(ctx.position('short') == 2 and '持仓测试失败！')
                        ctx.cover(0, 2) 
                cashes0.append(ctx.test_cash()) 

        set_symbols(['blotter.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategy('C1')],{ 'captial': CAPTIAL, 'ratio': [1] })
        run()
        target, cashes, dts = holdings_buy_short_maked_market(source, CAPTIAL)
        self.assertTrue(len(cashes0) == len(cashes), 'cash接口测试失败！')
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes0[i],cashes[i]), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings()):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')

    def test_case4(self):
        """ 测试跨合约交易的持仓, 资金 """ 
        cashes0 = []
        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [buy1, buy2, buy3]:
                    ctx.buy(ctx.close, 1) # 默认blotter.SHFE
                    ctx.short(ctx['blotter2.SHFE-1.Minute'].close, 2, 'blotter2.SHFE') 
                else:
                    if curtime == sell1:
                        assert(ctx.position('long', 'blotter.SHFE') == 3 and '持仓测试失败！')
                        ctx.sell(ctx.close, 2) 
                        assert(ctx.position('short', 'blotter2.SHFE') == 6 and '持仓测试失败！')
                        ctx.cover(ctx['blotter2.SHFE-1.Minute'].close, 4, 'blotter2.SHFE') 
                    elif curtime == sell2:
                        assert(ctx.position('long', 'blotter.SHFE') == 1 and '跨合约持仓测试失败！')
                        ctx.sell(ctx.close, 1, 'blotter.SHFE') 
                        assert(ctx.position('short', 'blotter2.SHFE') == 2 and '持仓测试失败！')
                        ctx.cover(ctx['blotter2.SHFE-1.Minute'].close, 2, 'blotter2.SHFE') 
                cashes0.append(ctx.test_cash()) 
        set_symbols(['blotter.SHFE-1.Minute', 'blotter2.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategy('D1')],{ 'captial': CAPTIAL, 'ratio': [1] })
        run()
        fname = os.path.join(os.getcwd(), 'data', 'blotter2.SHFE-1.Minute.csv')
        source2 = pd.read_csv(fname, parse_dates=True, index_col=0)
        target1, cashes1, dts = holdings_buy_maked_curbar(source, CAPTIAL/2) # 确保资金够用，所以不影响
        target2, cashes2, dts = holdings_short_maked_curbar(source2, CAPTIAL/2)
        target = [x + y for x, y in zip(target1, target2)]
        cashes = [x + y for x, y in zip(cashes1, cashes2)]
        self.assertTrue(len(cashes0) == len(cashes), 'cash接口测试失败！')
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes0[i],cashes[i]), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings()):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), 'all_holdings接口测试失败！')

def holdings_buy_maked_curbar(data, captial):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [buy1, buy2, buy3]
        当天卖出点: [sell1, sell2]
    """ 
    buy_prices= []
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    for dt, price in data.close.iteritems():
        curtime = dt.time()
        if curtime in [buy1, buy2, buy3]:
            buy_prices.append(price)
        else:
            if curtime == sell1:
                assert(len(buy_prices) == 3)
                profit = (price-buy_prices[0]) + (price-buy_prices[1])
                close_profit += profit
                buy_prices = buy_prices[-1:]
            elif curtime == sell2:
                assert(len(buy_prices) == 1)
                close_profit += (price - buy_prices[0])
                buy_prices = []
        if dt == data.index[-1]:
            # 强平现有持仓
            for bp in buy_prices:
                close_profit += (price - bp)
            buy_prices = []
        pos_profit = sum([price-pos_price for pos_price in buy_prices]) # 持仓盈亏
        #cost = sum(buy_prices) # 股票持仓成本
        equities.append(captial+close_profit+pos_profit)
        cost = price * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        cashes.append(equities[-1]-cost)
        dts.append(dt)
    return equities, cashes, dts

def holdings_short_maked_curbar(data, captial):
    """ 策略: 空头限价开仓且当根bar成交
        买入点：[buy1, buy2, buy3]
        当天卖出点：[sell1, sell2]
    """ 
    short_prices = []
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    for dt, price in data.close.iteritems():
        curtime = dt.time()
        if curtime in [buy1, buy2, buy3]:
            short_prices.append(price)
            short_prices.append(price)
        else:
            if curtime == sell1:
                assert(len(short_prices) == 6)
                profit = (price-short_prices[0]) + (price-short_prices[1]) +  \
                         (price-short_prices[2]) + (price-short_prices[3])
                close_profit -= profit
                short_prices = short_prices[-2:]
            elif curtime == sell2:
                assert(len(short_prices) == 2)
                close_profit -= (price - short_prices[0])
                close_profit -= (price - short_prices[1])
                short_prices = []
        if dt == data.index[-1]:
            # 强平现有持仓
            for bp in short_prices:
                close_profit -= (price - bp)
            short_prices = []
        pos_profit = sum([pos_price-price for pos_price in short_prices]) # 持仓盈亏
        equities.append(captial+close_profit+pos_profit)
        ## @TODO 股票测试
        #cost = price * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        cost = price * len(short_prices) * 1 
        cashes.append(equities[-1]-cost)
        dts.append(dt)
    return equities, cashes, dts

def holdings_buy_short_maked_curbar(data, captial):
    """ 策略: 多空限价开仓且当根bar成交
        买入点：[buy1, buy2, buy3]
        当天卖出点：[sell1, sell2]
    """ 
    buy_prices= []
    short_prices = []
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    for dt, price in data.close.iteritems():
        curtime = dt.time()
        if curtime in [buy1, buy2, buy3]:
            buy_prices.append(price)
            short_prices.append(price)
            short_prices.append(price)
        else:
            if curtime == sell1:
                assert(len(buy_prices) == 3)
                profit = (price-buy_prices[0]) + (price-buy_prices[1])
                close_profit += profit
                buy_prices = buy_prices[-1:]
                assert(len(short_prices) == 6)
                profit = (price-short_prices[0]) + (price-short_prices[1]) +  \
                         (price-short_prices[2]) + (price-short_prices[3])
                close_profit -= profit
                short_prices = short_prices[-2:]
            elif curtime == sell2:
                assert(len(buy_prices) == 1)
                close_profit += (price - buy_prices[0])
                buy_prices = []
                assert(len(short_prices) == 2)
                close_profit -= (price - short_prices[0])
                close_profit -= (price - short_prices[1])
                buy_prices = []
                short_prices = []
        if dt == data.index[-1]:
            # 强平现有持仓
            for bp in buy_prices:
                close_profit += (price - bp)
            for bp in short_prices:
                close_profit -= (price - bp)
            buy_prices = []
            short_prices = []
        pos_profit = sum([price-pos_price for pos_price in buy_prices]) # 持仓盈亏
        pos_profit -= sum([price-pos_price for pos_price in short_prices]) # 持仓盈亏
        equities.append(captial+close_profit+pos_profit)
        ## @TODO 股票测试
        cost = price * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        cost += price * len(short_prices) * 1 
        cashes.append(equities[-1]-cost)
        dts.append(dt)
    return equities, cashes, dts

def entries_maked_nextbar(data):
    """ 寻找交易点，使交易在改点的下一根能成交(延迟成交) """
    buy_entries = []
    sell_entries = []
    short_entries = []
    cover_entries = []
    prehigh = data.high[0]
    predt = data.index[0]
    prelow = data.low[0]

    for  dt, low in data.low.iteritems():
        if dt.date() == predt.date() and dt.time() < sell1 and prelow - low >= OFFSET:
            buy_entries.append(predt)
        prelow = low
        predt = dt

    for  dt, high in data.high.iteritems():
        if dt.date() == predt.date() and dt.time() < sell1 and high - prehigh >= OFFSET:
            short_entries.append(predt)
            #print predt, low-prelow
        prehigh = high
        predt = dt

    for dt, high in data.high.iteritems():
        if dt.time() > buy3 and high - prehigh >= OFFSET:
            sell_entries.append(predt)
            #print predt, high-prehigh
        prehigh = high
        predt = dt

    for  dt, low in data.low.iteritems():
        if dt.time() > buy3 and prelow - low >= OFFSET:
            cover_entries.append(predt)
            #print predt, low-prelow
        prelow = low
        predt = dt
    return buy_entries, sell_entries, short_entries, cover_entries

def holdings_buy_maked_nextbar(data, buy_entries, captial):
    """ 策略: 多头限价开仓且下一根bar成交
        买入点：[相关bar的最低点减去OFFSET]
        当天卖出点：sell1
    """ 
    buy_prices= []
    close_profit = 0    # 累计平仓盈亏
    equities = [] 
    dts = []
    cashes = []
    prelow = data.low[0]
    trans_entries = map(lambda x: x+datetime.timedelta(minutes = 1), buy_entries)
    for dt, low in data.low.iteritems():
        curtime = dt.time()
        close = data.close[dt]
        if dt in trans_entries:
            buy_prices.append(prelow-OFFSET)
        elif curtime == sell1:
            for bprice in buy_prices:
                close_profit += (close-bprice)
            buy_prices = []
        elif dt == data.index[-1]:
            # 最后一根，强平现有持仓
            for bp in buy_prices:
                close_profit += (close - bp)
            buy_prices = []
        pos_profit = 0 # 持仓盈亏
        for pos_price in buy_prices:
            pos_profit += (close - pos_price)
        equities.append(close_profit+pos_profit+captial)
        cost = close * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        cashes.append(equities[-1]-cost)
        #print "**********" 
        #print dt, cost, equities[-1]-cost
        #if equities[-1] - cost > 50001:
            #assert False
        dts.append(dt)
        prelow = low
    return equities, cashes, dts

def holdings_short_maked_nextbar(data, buy_entries, captial):
    """ 策略: 空头限价开仓且下一根bar成交
        买入点：[相关bar的最高点加上OFFSET]
        当天卖出点：sell1
    """ 
    buy_prices= []
    close_profit = 0    # 累计平仓盈亏
    equities = [] 
    dts = []
    cashes = []
    prehigh = data.high[0]
    trans_entries = map(lambda x: x+datetime.timedelta(minutes = 1), buy_entries)
    for dt, high in data.high.iteritems():
        curtime = dt.time()
        close = data.close[dt]
        if dt in trans_entries:
            buy_prices.append(prehigh+OFFSET)
        elif curtime == sell1:
            for bprice in buy_prices:
                close_profit -= (close-bprice)
            buy_prices = []
        elif dt == data.index[-1]:
            # 最后一根，强平现有持仓
            for bp in buy_prices:
                close_profit -= (close - bp)
            buy_prices = []
        pos_profit = 0 # 持仓盈亏
        for pos_price in buy_prices:
            pos_profit -= (close - pos_price)
        #print dt, pos_profit, close
        #print buy_prices
        equities.append(close_profit+pos_profit+captial)
        cost = close * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        cashes.append(equities[-1]-cost)
        dts.append(dt)
        prehigh = high
    return equities, cashes, dts

def holdings_sell_maked_nextbar(data, sell_entries, captial):
    """ 策略: 多头限价平仓且下一根bar成交
        买入点：[相关bar的最高点加上OFFSET]
        当天卖出点：sell1
    """ 
    buy_prices = []
    close_profit = 0    # 累计平仓盈亏
    equities = [] 
    dts = []
    trans_entries = map(lambda x: x+datetime.timedelta(minutes = 1), sell_entries)
    bprice = None
    prehigh = data.high[0]
    for dt, high in data.high.iteritems():
        close = data.close[dt]
        if dt.time() == buy1:
            bprice = close
        elif bprice and dt in trans_entries:
            close_profit += (prehigh+OFFSET-bprice)
            bprice = None
        elif dt == data.index[-1]:
            # 最后一根, 强平现有持仓
            if bprice:
                close_profit += (close - bprice)
            bprice = None
        elif dt.time () == sell3:
            # 不隔日
            if bprice:
                close_profit += (close - bprice)
            bprice = None
        pos_profit = 0 # 持仓盈亏
        if bprice:
            pos_profit += (close - bprice)
        equities.append(close_profit+pos_profit+captial)
        dts.append(dt)
        prehigh = high
    return equities, dts

def holdings_cover_maked_nextbar(data, cover_entries, captial):
    """ 策略: 空头限价平仓且下一根bar成交
        买入点：[相关bar的最低点减去OFFSET]
        当天卖出点：sell1
    """ 
    ## @TODO 11号无法成交，可用来测试“去隔夜单”
    ## @TODO c测试股票的可平数量
    buy_prices = []
    close_profit = 0    # 累计平仓盈亏
    equities = [] 
    dts = []
    trans_entries = map(lambda x: x+datetime.timedelta(minutes = 1), cover_entries)
    bprice = None
    prelow = data.low[0]
    for dt, low in data.low.iteritems():
        close = data.close[dt]
        if dt.time() == buy1:
            bprice = close
        elif bprice and dt in trans_entries:
            close_profit -= (prelow-OFFSET-bprice)
            bprice = None
        elif dt == data.index[-1]:
            # 最后一根, 强平现有持仓
            if bprice:
                close_profit -= (close - bprice)
            bprice = None
        elif dt.time () == sell3:
            # 不隔日
            if bprice:
                close_profit -= (close - bprice)
            bprice = None
        pos_profit = 0 # 持仓盈亏
        if bprice:
            pos_profit -= (close - bprice)
        equities.append(close_profit+pos_profit+captial)
        dts.append(dt)
        prelow = low
    return equities, dts

def holdings_buy_short_maked_market(data, captial):
    """ 策略: 多空市价开仓且当根bar成交
        买入点：[buy1, buy2, buy3]
        当天卖出点：[sell1, sell2]
    """ 
    buy_prices= []
    short_prices = []
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    for index, row in data.iterrows():
        close = row['close']
        dt = index
        high, low = row['high'], row['low']
        curtime = dt.time()
        if curtime in [buy1, buy2, buy3]:
            buy_prices.append(high)
            short_prices.append(low)
            short_prices.append(low)
        else:
            if curtime == sell1:
                assert(len(buy_prices) == 3)
                profit = (low-buy_prices[0]) + (low-buy_prices[1])
                close_profit += profit
                buy_prices = buy_prices[-1:]
                assert(len(short_prices) == 6)
                profit = (high-short_prices[0]) + (high-short_prices[1]) +  \
                         (high-short_prices[2]) + (high-short_prices[3])
                close_profit -= profit
                short_prices = short_prices[-2:]
            elif curtime == sell2:
                assert(len(buy_prices) == 1)
                close_profit += (low - buy_prices[0])
                buy_prices = []
                assert(len(short_prices) == 2)
                close_profit -= (high - short_prices[0])
                close_profit -= (high - short_prices[1])
                buy_prices = []
                short_prices = []
        if dt == data.index[-1]:
            # 强平现有持仓
            for bp in buy_prices:
                close_profit += (close - bp)
            for bp in short_prices:
                close_profit -= (close - bp)
            buy_prices = []
            short_prices = []
        pos_profit = sum([close-pos_price for pos_price in buy_prices]) # 持仓盈亏
        pos_profit -= sum([close-pos_price for pos_price in short_prices]) # 持仓盈亏
        equities.append(captial+close_profit+pos_profit)
        ## @TODO 股票测试
        cost = close * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        cost += close * len(short_prices) * 1 
        cashes.append(equities[-1]-cost)
        dts.append(dt)
    return equities, cashes, dts


if __name__ == '__main__':
    unittest.main()
