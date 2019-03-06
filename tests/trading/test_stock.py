# -*- coding: utf-8 -*-
import os
import pandas as pd
import unittest
from quantdigger.datastruct import Contract
from quantdigger.engine.profile import Profile

from quantdigger import (
    add_strategies,
    Strategy
)

from .stock_util import (
    buy_monday_sell_friday,
    trade_closed_curbar,
    capital,
    bt1,
    bt2,
    bt3,
    st1,
    st2
)

fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'STOCK.csv')
source = pd.read_csv(fname, parse_dates=True, index_col=0)

class TestOneDataOneCombinationStock(unittest.TestCase):
    """
    ctx.pos 可平仓位, 当天买隔天卖，当天不能卖。
    """

    def test_case(self):
        lmg = Contract.long_margin_ratio('stock.TEST')
        multi = Contract.volume_multiple('stock.TEST')
        smg = Contract.short_margin_ratio('stock.TEST')
        profiles = None

        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                self.cashes = []
                self.equities = []

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1)
                elif ctx.pos() >= 2 and curtime == st1:
                    ctx.sell(ctx.close, 2)
                elif ctx.pos() >= 1 and curtime == st2:
                    ctx.sell(ctx.close, 1)
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                equities, cashes, open_equities, open_casheses, dts =\
                    trade_closed_curbar(source, capital * 0.3, lmg, smg, multi, 1)

                test.assertTrue(len(self.cashes) == len(cashes), 'cash接口测试失败！')
                for i in range(0, len(self.cashes)):
                    test.assertAlmostEqual(self.cashes[i], open_casheses[i])
                    test.assertAlmostEqual(self.equities[i], open_equities[i])

                for i, hd in enumerate(profiles[0].all_holdings()):
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
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1)
                    ctx.short(ctx.close, 1)
                elif curtime == st1:
                    if ctx.pos() >= 3:
                        assert(ctx.pos() == 3 and '默认持仓查询测试失败！')
                        ctx.sell(ctx.close, 2)
                    if ctx.pos('short') >= 3:
                        assert(ctx.pos('short') == 3 and '默认持仓查询测试失败！')
                        ctx.cover(ctx.close, 2)
                elif curtime == st2:
                    if ctx.pos() >= 1:
                        ctx.sell(ctx.close, 1)
                    if ctx.pos('short') >= 1:
                        ctx.cover(ctx.close, 1)
                self.cashes.append(ctx.test_cash())

            def test(self, test):
                e0, c0, oe0, oc0, dts = trade_closed_curbar(source, capital * 0.3 / 2, lmg, smg, multi, 1)
                e1, c1, oe1, oc1, dts = trade_closed_curbar(source, capital * 0.3 / 2, lmg, smg, multi, -1)
                equities = [x + y for x, y in zip(e0, e1)]
                cashes = [x + y for x, y in zip(c0, c1)]
                for i, hd in enumerate(profiles[1].all_holdings()):
                    test.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
                    test.assertAlmostEqual(hd['equity'], equities[i])
                test.assertTrue(len(self.cashes) == len(cashes), 'cash接口测试失败！')
                for i in range(0, len(self.cashes) - 1):  # 最后一根强平了无法比较
                    test.assertAlmostEqual(self.cashes[i], cashes[i])

        class DemoStrategy3(Strategy):
            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                return

        a1 = DemoStrategy1('A1')
        a2 = DemoStrategy2('A2')
        a3 = DemoStrategy3('A3')
        profiles = add_strategies(['stock.TEST-1.Minute'], [
            {
                'strategy': a1,
                'capital': capital * 0.3,
            },
            {
                'strategy': a2,
                'capital': capital * 0.3,
            },
            {
                'strategy': a3,
                'capital': capital * 0.4,
            },
        ])

        a1.test(self)
        a2.test(self)

        all_holdings = Profile.all_holdings_sum(profiles)
        self.assertTrue(len(source) > 0 and len(source) == len(all_holdings), '模拟器测试失败！')
        for i in range(0, len(all_holdings)):
            hd = all_holdings[i]
            hd0 = profiles[0].all_holdings()[i]
            hd1 = profiles[1].all_holdings()[i]
            hd2 = profiles[2].all_holdings()[i]
            self.assertTrue(hd['cash'] == hd0['cash'] + hd1['cash'] + hd2['cash'],
                            'all_holdings接口测试失败！')
            self.assertTrue(hd['commission'] == hd0['commission'] +
                            hd1['commission'] + hd2['commission'], 'all_holdings接口测试失败！')
            self.assertTrue(hd['equity'] == hd0['equity'] + hd1['equity'] + hd2['equity'], 'all_holdings接口测试失败！')


#class TestMultiDataOneCombinationStock(unittest.TestCase):
class TestMultiDataOneCombinationStock(object):
    """ 跨合约引用的交易 """

    def test_case(self):

        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """

            def __init__(self, name):
                super(DemoStrategy1, self).__init__(name)
                self.tobuy = {}
                self.tosell = {}
                self._cashes = {}
                self._equities = {}

            def on_init(self, ctx):
                pass

            def on_symbol(self, ctx):
                """"""
                weekday = ctx.datetime[0].weekday()
                self.tobuy[ctx.symbol] = False
                self.tosell[ctx.symbol] = False
                if weekday == 0:
                    self.tobuy[ctx.symbol] = True
                elif weekday == 4:
                    self.tosell[ctx.symbol] = True

            def on_bar(self, ctx):
                if self.tobuy['600522.SH']:
                    ctx.buy(ctx['600522.SH'].close, 1, symbol='600522.SH')
                if self.tosell['600522.SH'] and ctx.pos(symbol='600522.SH')>0:
                    ctx.sell(ctx['600522.SH'].close, ctx.pos(symbol='600522.SH'), '600522.SH')

                self._cashes[ctx.datetime[0]] = ctx.cash()
                self._equities[ctx.datetime[0]] = ctx.equity()

            def test(self, test, profiles):
                lmg = Contract.long_margin_ratio('600522.SH')
                multi = Contract.volume_multiple('600522.SH')
                test.assertTrue(lmg == 1)
                test.assertTrue(multi == 1)
                fname = os.path.join(os.getcwd(), 'data', '1DAY', 'SH', '600522.csv')
                source = pd.read_csv(fname, parse_dates=True, index_col=0)
                equities, cashes, open_equities, open_cashes, dts = \
                    buy_monday_sell_friday(source, capital * 0.3, lmg, multi)
                count = 0
                all_holdings0 = profiles[0].all_holdings()
                for i, hd in enumerate(all_holdings0):
                    dt = hd['datetime']
                    if dt in cashes:
                        test.assertAlmostEqual(hd['cash'], cashes[dt])
                        test.assertAlmostEqual(hd['equity'], equities[dt])
                        test.assertAlmostEqual(self._cashes[dt], open_cashes[dt])
                        test.assertAlmostEqual(self._equities[dt], open_equities[dt])
                        count += 1
                    else:
                        # 两支股票的混合，总数据长度和source不一样。
                        test.assertAlmostEqual(all_holdings0[i - 1]['cash'], hd['cash'])
                        test.assertAlmostEqual(all_holdings0[i - 1]['equity'], hd['equity'])
                test.assertTrue(count == len(dts))

        class DemoStrategy2(Strategy):
            """ 选股，并且时间没对齐的日线数据。 """
            def __init__(self, name):
                super(DemoStrategy2, self).__init__(name)
                self.tobuys = []
                self.tosells = []
                self._cashes = {}
                self._equities = {}

            def on_symbol(self, ctx):
                """"""
                weekday = ctx.datetime[0].weekday()
                if weekday == 0:
                    self.tobuys.append(ctx.symbol)
                elif weekday == 4:
                    self.tosells.append(ctx.symbol)

            def on_bar(self, ctx):
                """初始化数据"""
                for symbol in self.tobuys:
                    ctx.buy(ctx[symbol].close, 1, symbol)
                for symbol in self.tosells:
                    if ctx.pos(symbol=symbol) > 0:
                        ctx.sell(ctx[symbol].close, ctx.pos(symbol=symbol), symbol)

                self._equities[ctx.datetime[0]] = ctx.equity()
                self._cashes[ctx.datetime[0]] = ctx.cash()
                self.tobuys = []
                self.tosells = []

            def test(self, test, profiles):
                fname = os.path.join(os.getcwd(), 'data', '1DAY', 'SH', '600521.csv')
                source = pd.read_csv(fname, parse_dates=True, index_col=0)
                fname = os.path.join(os.getcwd(), 'data', '1DAY', 'SH', '600522.csv')
                source2 = pd.read_csv(fname, parse_dates=True, index_col=0)
                equities0, cashes0, open_equities0, open_cashes0, dts = \
                    buy_monday_sell_friday(source, capital * 0.3 / 2, 1, 1)
                equities1, cashes1, open_equities1, open_cashes1, dts = \
                    buy_monday_sell_friday(source2, capital * 0.3 / 2, 1, 1)
                last_equity0 = 0
                last_equity1 = 0
                last_cash0 = 0
                last_cash1 = 0
                for i, hd in enumerate(profiles.all_holdings(1)):
                    dt = hd['datetime']
                    equity = 0
                    cash = 0
                    open_equity = 0
                    open_cash = 0
                    if dt in equities0:
                        equity = equities0[dt]
                        cash = cashes0[dt]
                        open_equity = open_equities0[dt]
                        open_cash = open_cashes0[dt]
                        last_equity0 = equities0[dt]
                        last_cash0 = cashes0[dt]
                    else:
                        equity += last_equity0
                        cash += last_cash0
                        open_equity += last_equity0
                        open_cash += last_cash0

                    if dt in equities1:
                        equity += equities1[dt]
                        cash += cashes1[dt]
                        last_equity1 = equities1[dt]
                        last_cash1 = cashes1[dt]
                        open_equity += open_equities1[dt]
                        open_cash += open_cashes1[dt]
                    else:
                        equity += last_equity1
                        cash += last_cash1
                        open_equity += last_equity1
                        open_cash += last_cash1

                    test.assertAlmostEqual(hd['equity'], equity)
                    test.assertAlmostEqual(hd['cash'], cash)
                    test.assertAlmostEqual(self._equities[dt], open_equity)
                    test.assertAlmostEqual(self._cashes[dt], open_cash)

        class DemoStrategy3(Strategy):
            """ 测试平仓未成交时的持仓，撤单后的持仓，撤单。 """
            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                return

        b1 = DemoStrategy1('B1')
        b2 = DemoStrategy2('B2')
        b3 = DemoStrategy3('B3')
        profiles = add_strategies(['600521', '600522'], [
            {
                'strategy': b1,
                'capital': capital * 0.3,
            },
            {
                'strategy': b2,
                'capital': capital * 0.3,
            },
            {
                'strategy': b3,
                'capital': capital * 0.4,
            },
        ])
        b1.test(self, profiles)
        b2.test(self, profiles)


if __name__ == '__main__':
    unittest.main()
