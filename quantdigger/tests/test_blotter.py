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
from quantdigger.engine.series import NumberSeries, DateTimeSeries

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


class TestOneDataOneCombination(unittest.TestCase):
    """ 测试单数据单组合的价格撮合，持仓，可用资金等交易接口 """
        
    def test_case(self):
        # @todo profile
             #signals 盈利

        # @TODO deals DemoStrategy2
        cashes0, cashes1 = [], []

        class DemoStrategy1(Strategy):
            """ 只买多头仓位的策略 """
            
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
                ## @note  前一根的交易信号在当前价格撮合后的可用资金
                cashes0.append(ctx.test_cash()) 


        class DemoStrategy2(Strategy):
            """ 买多卖空的策略 """
            
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
                        assert(ctx.position('long') == 3 and '持仓测试失败！')
                        ctx.sell(ctx.close, 2) 
                        assert(ctx.position('short') == 6 and '持仓测试失败！')
                        ctx.cover(ctx.close, 4) 
                    elif curtime == sell2:
                        assert(ctx.position('long') == 1 and '持仓测试失败！')
                        ctx.sell(ctx.close, 1) 
                        assert(ctx.position('short') == 2 and '持仓测试失败！')
                        ctx.cover(ctx.close, 2) 
                cashes1.append(ctx.test_cash()) 

        set_symbols(['blotter.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategy1('A1'), DemoStrategy2('A2')], {
            'captial': CAPTIAL,
            'ratio': [0.5, 0.5]
            })
        run()
        # all_holding
        fname = os.path.join(os.getcwd(), 'data', 'blotter.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertTrue(len(source) > 0 and 
                        len(source) ==  len(profile.all_holdings(0)), '模拟器测试失败！')
        self.assertTrue(len(source) > 0 and 
                        len(source) ==  len(profile.all_holdings(1)), '模拟器测试失败！')
        # cash()
        target, cashes, dts = target_all_holding1(source, CAPTIAL/2)
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes0[i],cashes[i]), 'cash接口测试失败！')
        self.assertTrue(len(cashes0) == len(cashes), 'cash接口测试失败！')
        self.assertTrue(len(profile.all_holdings(0)) == len(target) and
                        len(target) > 0, 'all_holdings接口测试失败！')

        for i, hd in enumerate(profile.all_holdings(0)):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), 'all_holdings接口测试失败！')

        target2, cashes, dts = target_all_holding2(source, CAPTIAL/2)
        self.assertTrue(len(profile.all_holdings(1)) == len(target2) and 
                        len(target2) > 0, 'all_holdings接口测试失败！')
        for i in range(0, len(cashes1)-1): # 最后一根强平了无法比较
            self.assertTrue(np.isclose(cashes1[i],cashes[i]), 'cash接口测试失败！')
        self.assertTrue(len(cashes1) == len(cashes), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(np.isclose(target[i]-CAPTIAL/2,
                                        0-(target2[i]-CAPTIAL/2)), '测试代码错误！')
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target2[i]), 'all_holdings接口测试失败！')
        #
        hd0 = profile.holding(0) 
        hd1 = profile.holding(1) 
        hd = profile.holding()
        self.assertTrue(hd0['equity']+hd1['equity']==hd['equity'], 'holdings接口测试失败！')
        self.assertTrue(hd0['cash']+hd1['cash']==hd['cash'], 'holdings接口测试失败！')
        self.assertTrue(hd0['commission']+hd1['commission']==hd['commission'], 'holdings接口测试失败！')
        self.assertTrue(hd0['history_profit']+hd1['history_profit']==hd['history_profit'], 'holdings接口测试失败！')
        hd0last = profile.all_holdings(0)[-1]
        self.assertTrue(hd0last['equity'] == hd0['equity'], 'holdings接口测试失败！')
        self.assertTrue(hd0last['cash'] == hd0['cash'], 'holdings接口测试失败！')
        self.assertTrue(hd0last['commission'] == hd0['commission'], 'holdings接口测试失败！')
        self.assertTrue(len(profile.all_holdings()) == len(target) and
                        len(target) > 0, 'holdings接口测试失败！')
        #
        ## @TODO 
        all_holdings = profile.all_holdings()
        all_holdings0 = profile.all_holdings(0)
        all_holdings1 = profile.all_holdings(1)
        for i in range(0, len(profile.all_holdings())):
            hd = all_holdings[i]
            hd0 = all_holdings0[i]
            hd1 = all_holdings1[i]
            self.assertTrue(hd['cash'] == hd0['cash'] + hd1['cash'] , 'all_holdings接口测试失败！')
            self.assertTrue(hd['commission'] == hd0['commission'] +
                    hd1['commission'], 'all_holdings接口测试失败！')
            self.assertTrue(hd['equity'] == hd0['equity'] + hd1['equity'], 'all_holdings接口测试失败！')
            
        ## 绘制k线，交易信号线
        #from quantdigger.digger import finance, plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(1))


    def test_case2(self):
        """ 测试限价的延迟成交 """
        buy_entries, sell_entries = [], []
        short_entries, cover_entries = [], []

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
                    ## @TODO 隔夜测试
                elif ctx.position('long') > 0 and ctx.datetime[0].time() == sell3:
                    ctx.sell(ctx.close, ctx.position()) 

        class DemoStrategyCover(Strategy):
            """ 只买多头仓位的策略 """
            
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
        profile = add_strategy([DemoStrategyBuy('A1'), DemoStrategySell('A2'),
                                DemoStrategyShort('A3'), DemoStrategyCover('A4')],{
                                    'captial': CAPTIAL,
                                    'ratio': [0.25, 0.25, 0.25, 0.25]
                                  })

        fname = os.path.join(os.getcwd(), 'data', 'blotter.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        buy_entries, sell_entries, short_entries, cover_entries = findTradingPoint(source)
        run()
        # buy
        target, dts = target_all_holding_buy(source, buy_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(0)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(0)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')
        # short
        target, dts = target_all_holding_short(source, short_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(2)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(2)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')
        # sell
        target, dts = target_all_holding_sell(source, sell_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(1)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')

        # cover
        target, dts = target_all_holding_cover(source, cover_entries, CAPTIAL/4)
        self.assertTrue(len(profile.all_holdings(3)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(3)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], target[i]), '模拟器测试失败！')

        #from quantdigger.digger import plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(3))

        ## @TODO 模拟器make_market的运行次数
        ## @TODO 跨日订单的清空
        return

def target_all_holding1(data, captial):
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
        cost = price * len(buy_prices) * 1  # 保证金为比例为1的期货持仓成本。
        equities.append(captial+close_profit+pos_profit)
        cashes.append(equities[-1]-cost)
        dts.append(dt)
    return equities, cashes, dts

def target_all_holding2(data, captial):
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


def findTradingPoint(data):
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

def target_all_holding_buy(data, buy_entries, captial):
    """ 返回策略多头限价开仓超过当前bar价格范围的历史资金状况 """ 
    buy_prices= []
    close_profit = 0    # 累计平仓盈亏
    equities = [] 
    dts = []
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
                buy_prices = buy_prices[-1:]
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
        dts.append(dt)
        prelow = low
    return equities, dts

def target_all_holding_short(data, buy_entries, captial):
    """ 返回策略空头限价开仓超过当前bar价格范围的历史资金状况 """ 
    buy_prices= []
    close_profit = 0    # 累计平仓盈亏
    equities = [] 
    dts = []
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
                buy_prices = buy_prices[-1:]
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
        dts.append(dt)
        prehigh = high
    return equities, dts

def target_all_holding_sell(data, sell_entries, captial):
    """ 返回策略多头限价平仓超过当前bar价格范围的历史资金状况 """ 
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

def target_all_holding_cover(data, cover_entries, captial):
    """ 返回策略空头限价平仓超过当前bar价格范围的历史资金状况 """ 
    ## @TODO 11号无法成交，可用来测试“去隔夜单”
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


if __name__ == '__main__':
    unittest.main()
