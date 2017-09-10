# -*- coding: utf-8 -*-
##
# @file test_blotter.py
# @brief 测试模拟器的价格撮合, 当前持仓，权益，可用资金等。
# @author wondereamer
# @version 0.3
# @date 2015-01-06

import datetime
import os

import six
import pandas as pd
import unittest
from quantdigger.datastruct import  Contract
from stock_util import *
from quantdigger import *
from logbook import Logger
logger = Logger('test')
capital = 200000000
fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'STOCK.csv')
source = pd.read_csv(fname, parse_dates=True, index_col=0)


class TestOneDataOneCombinationStock(unittest.TestCase):
    """ 测试股票单数据单组合的价格撮合，持仓查询／默认持仓查询，可用资金等交易接口 """

    def test_case(self):
        lmg = Contract.long_margin_ratio('stock.TEST')
        multi = Contract.volume_multiple('stock.TEST')
        smg = Contract.short_margin_ratio('stock.TEST')
        profile = None


        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                self.cashes = []
                self.equities = []

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [buy1, buy2, buy3]:
                    ctx.buy(ctx.close, 1)
                elif ctx.pos() >= 2 and curtime == sell1:
                    ctx.sell(ctx.close, 2)
                elif ctx.pos() >= 1 and curtime == sell2:
                    ctx.sell(ctx.close, 1)
                ## 前一根的交易信号在当前价格撮合后的可用资金
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                equities, cashes, open_equities, open_cashes, dts = trade_closed_curbar(source, capital*0.3, lmg, smg, multi, 1)

                test.assertTrue(len(self.cashes) == len(cashes), 'cash接口测试失败！')
                for i in range(0, len(self.cashes)): # 最后一根强平了无法比较
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])
                    test.assertAlmostEqual(self.equities[i], open_equities[i])

                for i, hd in enumerate(profile.all_holdings(0)):
                    test.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
                    test.assertAlmostEqual(hd['equity'], equities[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])


        class DemoStrategy2(Strategy):
            """ 限价买多卖空的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                self.cashes = []

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [buy1, buy2, buy3]:
                    ctx.buy(ctx.close, 1)
                    ctx.short(ctx.close, 1)
                elif curtime == sell1:
                    if ctx.pos() >= 3:
                        # quantity == 6, closable == 3
                        assert(ctx.pos() == 3 and '默认持仓查询测试失败！')
                        ctx.sell(ctx.close, 2)
                    if ctx.pos('short') >= 3:
                        assert(ctx.pos('short') == 3 and '默认持仓查询测试失败！')
                        ctx.cover(ctx.close, 2)
                elif curtime == sell2:
                    if ctx.pos() >= 1:
                        ctx.sell(ctx.close, 1)
                    if ctx.pos('short') >= 1:
                        ctx.cover(ctx.close, 1)
                self.cashes.append(ctx.test_cash())

            def test(self, test):
                #  确保资金够用，所以不影响
                e0, c0, oe0, oc0, dts = trade_closed_curbar(source, capital*0.3/2, lmg, smg, multi, 1)
                e1, c1, oe1, oc1, dts = trade_closed_curbar(source, capital*0.3/2, lmg, smg, multi, -1)
                equities = [x + y for x, y in zip(e0, e1)]
                cashes = [x + y for x, y in zip(c0, c1)]
                for i, hd in enumerate(profile.all_holdings(1)):
                    test.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
                    test.assertAlmostEqual(hd['equity'], equities[i])
                test.assertTrue(len(self.cashes) == len(cashes), 'cash接口测试失败！')
                for i in range(0, len(self.cashes)-1): # 最后一根强平了无法比较
                    test.assertAlmostEqual(self.cashes[i],cashes[i])



        class DemoStrategy3(Strategy):
            """ 测试平仓未成交时的持仓，撤单后的持仓，撤单。 """
            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                return

        set_symbols(['stock.TEST-1.Minute'])
        a1 = DemoStrategy1('A1')
        a2 = DemoStrategy2('A2')
        a3 = DemoStrategy3('A3')
        profile = add_strategy([a1, a2, a3], {
            'capital': capital,
            'ratio': [0.3, 0.3, 0.4]
            })
        run()

        a1.test(self)
        a2.test(self)


        all_holdings = profile.all_holdings()
        self.assertTrue(len(source) > 0 and len(source) ==  len(all_holdings), '模拟器测试失败！')
        for i in range(0, len(profile.all_holdings())):
            hd = all_holdings[i]
            hd0 = profile.all_holdings(0)[i]
            hd1 = profile.all_holdings(1)[i]
            hd2 = profile.all_holdings(2)[i]
            self.assertTrue(hd['cash'] == hd0['cash'] + hd1['cash'] + hd2['cash'],
                            'all_holdings接口测试失败！')
            self.assertTrue(hd['commission'] == hd0['commission'] +
                            hd1['commission'] + hd2['commission'], 'all_holdings接口测试失败！')
            self.assertTrue(hd['equity'] == hd0['equity'] + hd1['equity'] + hd2['equity'], 'all_holdings接口测试失败！')



class TestMultiDataOneCombinationStock(unittest.TestCase):
    """ 测试日线交易接口 """

    def test_case(self):
        t_cashes0, t_equity0 = {}, { }
        t_cashes1, t_equity1 = {}, { }

        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                ctx.tobuy = False
                ctx.tosell = False

            def on_symbol(self, ctx):
                """"""
                weekday = ctx.datetime[0].weekday()
                if weekday == 0:
                    ctx.tobuy = True
                elif weekday == 4:
                    ctx.tosell = True

            def on_bar(self, ctx):
                #weekday = ctx.datetime[0].weekday()
                if ctx['600521'].tobuy:
                    ctx.buy(ctx['600521'].close, 1)
                if ctx['600521'].tosell and ctx.pos(symbol='600521.SH')>0:
                    ctx.sell(ctx['600521'].close, ctx.pos(symbol='600521.SH'))
                ctx['600521'].tobuy = False
                ctx['600521'].tosell = False
                t_cashes0[ctx.datetime[0]] = ctx.test_cash()
                t_equity0[ctx.datetime[0]] = ctx.test_equity()


        class DemoStrategy2(Strategy):
            """ 限价买多卖空的策略 """
            def __init__(self, name):
                super(DemoStrategy2, self).__init__(name)
                self.tobuys = []
                self.tosells = []

            def on_symbol(self, ctx):
                """"""
                weekday = ctx.datetime[0].weekday()
                if weekday == 0:
                    self.tobuys.append(ctx.symbol)
                elif weekday == 4:
                    self.tosells.append(ctx.symbol)

            def on_bar(self, ctx):
                """初始化数据"""
                ## @TODO all_positions
                for symbol in self.tobuys:
                    ctx.buy(ctx[symbol].close, 1, symbol)
                for symbol in self.tosells:
                    if ctx.pos(symbol=symbol)>0:
                        ctx.sell(ctx[symbol].close, ctx.pos(symbol=symbol), symbol)

                t_equity1[ctx.datetime[0]] = ctx.test_equity()
                t_cashes1[ctx.datetime[0]] = ctx.test_cash()
                self.tobuys = []
                self.tosells = []


        class DemoStrategy3(Strategy):
            """ 测试平仓未成交时的持仓，撤单后的持仓，撤单。 """
            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                return

        set_symbols(['600521', '600522'])
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
        lmg = Contract.long_margin_ratio('600521.SH')
        multi = Contract.volume_multiple('600521.SH')
        fname = os.path.join(os.getcwd(), 'data', '1DAY', 'SH', '600521.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        s_equity0, s_cashes0, dts = buy_monday_sell_friday(source, capital*0.3, lmg, multi)
        count = 0
        for i, hd in enumerate(all_holdings0):
            # 刚好最后一根没持仓，无需考虑强平, 见weekday输出
            dt = hd['datetime']
            if dt in s_cashes0:
                self.assertAlmostEqual(hd['cash'], s_cashes0[dt])
                self.assertAlmostEqual(t_cashes0[dt], s_cashes0[dt])
                self.assertAlmostEqual(hd['equity'], s_equity0[dt])
                self.assertAlmostEqual(t_equity0[dt], s_equity0[dt])
                count += 1
            else:
                self.assertAlmostEqual(all_holdings0[i-1]['cash'], hd['cash'])
                self.assertAlmostEqual(all_holdings0[i-1]['equity'], hd['equity'])
        self.assertTrue(count == len(dts))

        # test Strategy2
        fname = os.path.join(os.getcwd(), 'data', '1DAY', 'SH', '600522.csv')
        source2 = pd.read_csv(fname, parse_dates=True, index_col=0)
        s_equity0, s_cashes0, dts = buy_monday_sell_friday(source, capital*0.3/2, lmg, multi)
        s_equity1, s_cashes1, dts = buy_monday_sell_friday(source2, capital*0.3/2, 1, 1)
        last_equity0 = 0
        last_equity1 = 0
        last_cash0 = 0
        last_cash1 = 0
        for i, hd in enumerate(all_holdings1):
            # 刚好最后一根没持仓，无需考虑强平, 见weekday输出
            dt = hd['datetime']
            equity = 0
            cash = 0
            if dt in s_equity0:
                equity += s_equity0[dt]
                cash += s_cashes0[dt]
                last_equity0 = s_equity0[dt]
                last_cash0 = s_cashes0[dt]
            else:
                equity += last_equity0
                cash += last_cash0
            if dt in s_equity1:
                equity += s_equity1[dt]
                cash += s_cashes1[dt]
                last_equity1 = s_equity1[dt]
                last_cash1 = s_cashes1[dt]
            else:
                equity += last_equity1
                cash += last_cash1
            self.assertAlmostEqual(hd['equity'], equity)
            self.assertAlmostEqual(hd['cash'], cash)
            self.assertAlmostEqual(t_cashes1[dt], cash)
            self.assertAlmostEqual(t_equity1[dt], equity)




if __name__ == '__main__':
    unittest.main()
