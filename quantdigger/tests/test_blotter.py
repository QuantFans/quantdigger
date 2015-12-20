# -*- coding: utf-8 -*-
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

def target_all_holding1(data):
    buy_prices= []
    close_profit = 0
    profits = [] # 累计平仓盈亏
    dts = []
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
        pos_profit = 0 # 持仓盈亏
        for pos_price in buy_prices:
            pos_profit += (price - pos_price)
        profits.append(close_profit+pos_profit)
        dts.append(dt)
    return profits, dts

def target_all_holding2(data):
    buy_prices= []
    short_prices = []
    close_profit = 0
    profits = [] # 累计平仓盈亏
    dts = []
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
        pos_profit = 0 # 持仓盈亏
        for pos_price in buy_prices:
            pos_profit += (price - pos_price)
        for pos_price in short_prices:
            pos_profit -= (price - pos_price)
        profits.append(close_profit+pos_profit)
        dts.append(dt)
    return profits, dts


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
            print predt, high-prehigh
        prehigh = high
        predt = dt

    for  dt, low in data.low.iteritems():
        if dt.time() > buy3 and prelow - low >= OFFSET:
            cover_entries.append(predt)
            #print predt, low-prelow
        prelow = low
        predt = dt
    return buy_entries, sell_entries, short_entries, cover_entries

def target_all_holding_buy(data, buy_entries):
    """ 返回策略多头限价开仓超过当前bar价格范围的历史资金状况 """ 
    buy_prices= []
    close_profit = 0    # 累计平仓盈亏
    profits = [] 
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
        profits.append(close_profit+pos_profit)
        dts.append(dt)
        prelow = low
    return profits, dts

def target_all_holding_sell(data, sell_entries):
    """ 返回策略多头限价平仓超过当前bar价格范围的历史资金状况 """ 
    buy_prices= []
    close_profit = 0    # 累计平仓盈亏
    profits = [] 
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
        profits.append(close_profit+pos_profit)
        dts.append(dt)
        prehigh = high
    return profits, dts


class TestSimulator(unittest.TestCase):
    """ 多组合策略测试 """
        
    def test_case(self):
        # @todo profile
             #signals 盈利

        # @TODO deals DemoStrategy2
        pass

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

        set_symbols(['blotter.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategy1('A1'), DemoStrategy2('A2')], {
            'captial': CAPTIAL,
            'ratio': [0.5, 0.5]
            })
        run()

        fname = os.path.join(os.getcwd(), 'data', 'blotter.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertTrue(len(source) > 0 and 
                        len(source) ==  len(profile.all_holdings(0)), '模拟器测试失败！')
        self.assertTrue(len(source) > 0 and 
                        len(source) ==  len(profile.all_holdings(1)), '模拟器测试失败！')
        target, dts = target_all_holding1(source)
        self.assertTrue(len(profile.all_holdings(0)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(0)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], CAPTIAL/2+target[i]), '模拟器测试失败！')

        target2, dts = target_all_holding2(source)
        self.assertTrue(len(profile.all_holdings(1)) == len(target2) and 
                        len(target2) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(np.isclose(target[i], 0-target2[i]), '测试代码错误！')
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], CAPTIAL/2+target2[i]), '模拟器测试失败！')
        hd0 = profile.holding(0) 
        hd1 = profile.holding(1) 
        hd = profile.holding()
        self.assertTrue(hd0['equity']+hd1['equity']==hd['equity'])
        self.assertTrue(hd0['cash']+hd1['cash']==hd['cash'])
        self.assertTrue(hd0['commission']+hd1['commission']==hd['commission'])
        self.assertTrue(hd0['history_profit']+hd1['history_profit']==hd['history_profit'])

        hd0last = profile.all_holdings(0)[-1]
        self.assertTrue(hd0last['equity'] == hd0['equity'])
        self.assertTrue(hd0last['cash'] == hd0['cash'])
        self.assertTrue(hd0last['commission'] == hd0['commission'])

        self.assertTrue(len(profile.all_holdings()) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        ## @TODO 
        for i in range(0, len(profile.all_holdings())):
            pass
            
        ## 绘制k线，交易信号线
        #from quantdigger.digger import finance, plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(1))


    def test_case2(self):
        """ 测试限价的延迟成交 """
        buy_entries, sell_entries = [], []
        short_entries, cover_entries = [], []

        class DemoStrategyBuy(Strategy):
            """ 只买多头仓位的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in buy_entries:
                    ctx.buy(ctx.low-OFFSET, 1) 
                elif ctx.position('long') > 0 and ctx.datetime[0].time() == sell1:
                    ctx.sell(ctx.close, ctx.position()) 


        class DemoStrategySell(Strategy):
            """ 只买多头仓位的策略 """
            
            def on_init(self, ctx):
                """初始化数据""" 
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == buy1:
                    ctx.buy(ctx.close, 1) 
                    #print 'buy', ctx.datetime[0], ctx.close
                elif ctx.position('long') > 0 and ctx.datetime[0] in sell_entries:
                    #print 'sell', ctx.datetime[0], ctx.high+OFFSET
                    ctx.sell(ctx.high+OFFSET, ctx.position()) 
                elif ctx.position('long') > 0 and ctx.datetime[0].time() == sell3:
                    #print 'sell', ctx.datetime[0], ctx.close
                    ctx.sell(ctx.close, ctx.position()) 


        set_symbols(['blotter.SHFE-1.Minute'], window_size)
        profile = add_strategy([DemoStrategyBuy('A1'), DemoStrategySell('A2'),
                                DemoStrategyBuy('A3'), DemoStrategyBuy('A4')],{
                                    'captial': CAPTIAL,
                                    'ratio': [0.25, 0.25, 0.25, 0.25]
                                  })

        fname = os.path.join(os.getcwd(), 'data', 'blotter.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        buy_entries, sell_entries, short_entries, cover_entries = findTradingPoint(source)
        run()
        #
        target, dts = target_all_holding_buy(source, buy_entries)
        self.assertTrue(len(profile.all_holdings(0)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(0)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], CAPTIAL/4+target[i]), '模拟器测试失败！')
        #
        target, dts = target_all_holding_sell(source, sell_entries)
        self.assertTrue(len(profile.all_holdings(1)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')

        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertTrue(np.isclose(hd['equity'], CAPTIAL/4+target[i]), '模拟器测试失败！')
        from quantdigger.digger import plotting
        plotting.plot_strategy(profile.data(), deals=profile.deals(1))

        ## @TODO 模拟器make_market的运行次数
        ## @TODO 跨日订单的清空
        return

if __name__ == '__main__':
    unittest.main()
