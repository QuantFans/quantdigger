# -*- coding: utf-8 -*-

import unittest
import pandas as pd
import os

from six.moves import range

from quantdigger.datastruct import TradeSide, Contract, Direction
from quantdigger import (
    add_strategy,
    set_symbols,
    Strategy,
    run
)

from .future_util import (
    trade_closed_curbar,
    in_closed_nextbar,
    out_closed_nextbar,
    entries_maked_nextbar,
    market_trade_closed_curbar,
    OFFSET,
    capital,
    bt1,
    bt2,
    bt3,
    st1,
    st2,
    st3,
)

fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'FUTURE.csv')
source = pd.read_csv(fname, parse_dates=True, index_col=0)

lmg = Contract.long_margin_ratio('future.TEST')
multi = Contract.volume_multiple('future.TEST')
smg = Contract.short_margin_ratio('future.TEST')


class TestOneDataOneCombination(unittest.TestCase):
    """
    分钟线日内限价交易, 且当根bar成交。
    测试：
        Strategy1, Strategy2:
           profile.all_holdings(x)
           ctx.buy, ctx.sell
           ctx.cash(), ctx.equity()

        Strategy3:
           隔夜未成交订单自动清空。
           保证测单动作从下一个Bar开始执行。
           ctx.cancel(), ctx.open_orders()
           ctx.pos(), ctx.all_positions()
    """

    def test_case(self):
        profile = None

        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """
            def __init__(self, name):
                super(DemoStrategy1, self).__init__(name)
                self.open_cash = []
                self.open_equity = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1)
                else:
                    if curtime == st1:
                        assert(ctx.pos() == 3 and '持仓测试失败！')
                        ctx.sell(ctx.close, 2)
                    elif curtime == st2:
                        assert(ctx.pos() == 1 and '持仓测试失败！')
                        ctx.sell(ctx.close, 1)
                # 前一根的交易信号在当前价格撮合后的可用资金
                self.open_cash.append(ctx.cash())
                self.open_equity.append(ctx.equity())

            def test(self, test):
                close_equity, close_cash, open_equity, open_cashes, dts = trade_closed_curbar(source,
                                                                                              capital * 0.3,
                                                                                              lmg,
                                                                                              smg,
                                                                                              multi,
                                                                                              1)
                for i, hd in enumerate(profile.all_holdings(0)):
                    test.assertAlmostEqual(self.open_equity[i], open_equity[i])
                    test.assertAlmostEqual(self.open_cash[i], open_cashes[i])
                    test.assertAlmostEqual(hd['equity'], close_equity[i])
                    test.assertAlmostEqual(hd['cash'], close_cash[i])
                    test.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
                    test.assertTrue(len(profile.all_holdings()) == len(close_equity) and
                                    len(close_equity) > 0, 'holdings接口测试失败！')

        class DemoStrategy2(Strategy):
            """ 限价买多卖空的策略 """
            def __init__(self, name):
                super(DemoStrategy2, self).__init__(name)
                self.open_cash = []
                self.open_equity = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1)
                    ctx.short(ctx.close, 1)
                else:
                    if curtime == st1:
                        assert(ctx.pos() == 3 and '默认持仓查询测试失败！')
                        ctx.sell(ctx.close, 2)
                        assert(ctx.pos('short') == 3 and '持仓测试失败！')
                        ctx.cover(ctx.close, 2)
                    elif curtime == st2:
                        assert(ctx.pos('long') == 1 and '持仓测试失败！')
                        ctx.sell(ctx.close, 1)
                        assert(ctx.pos('short') == 1 and '持仓测试失败！')
                        ctx.cover(ctx.close, 1)
                self.open_cash.append(ctx.cash())
                self.open_equity.append(ctx.equity())

            def test(self, test):
                #  确保资金够用，所以不影响
                e0, c0, oe0, oc0, dts = trade_closed_curbar(source, capital * 0.3 / 2, lmg, smg, multi, 1)
                e1, c1, oe1, oc1, dts = trade_closed_curbar(source, capital * 0.3 / 2, lmg, smg, multi, -1)
                close_equity = [x + y for x, y in zip(e0, e1)]
                close_cash = [x + y for x, y in zip(c0, c1)]
                open_equity = [x + y for x, y in zip(oe0, oe1)]
                open_cash = [x + y for x, y in zip(oc0, oc1)]
                test.assertTrue(len(close_equity) == len(profile.all_holdings(1)))
                for i in range(len(close_equity)):
                    hd = profile.all_holdings(1)[i]
                    test.assertAlmostEqual(self.open_equity[i], open_equity[i])
                    test.assertAlmostEqual(self.open_cash[i], open_cash[i])
                    test.assertAlmostEqual(hd['equity'], close_equity[i])
                    test.assertAlmostEqual(hd['cash'], close_cash[i])
                    test.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
                    test.assertTrue(len(profile.all_holdings()) == len(close_equity) and
                                    len(close_equity) > 0, 'holdings接口测试失败！')

        class DemoStrategy3(Strategy):
            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.curbar == 1:
                    ctx.short(138, 1)
                    ctx.short(138, 1)
                    ctx.buy(ctx.close, 1)

                # 保证测单动作不会在当前时间点生效，而是从下一个时间点开始。
                if ctx.curbar == 3:
                    assert(len(ctx.open_orders) == 2)
                    ctx.cancel(ctx.open_orders[0])
                    assert(len(ctx.open_orders) == 2 and '撤单测试失败')
                elif ctx.curbar == 4:
                    assert(len(ctx.open_orders) == 1 and '撤单测试失败！')

                # 测试可平仓位和所有仓位不同。
                if ctx.curbar == 5:
                    assert(ctx.pos() == 1)
                    ctx.sell(300, 1)  # 下无法成交的平仓，测试持仓。
                elif ctx.curbar == 7:
                    assert(len(ctx.all_positions()) == 1 and '持仓测试失败!')
                    assert(ctx.pos() == 0 and '持仓测试失败!')
                    assert(len(ctx.open_orders) == 2 and '撤单测试失败！')
                    order = list(filter(lambda x: x.side == TradeSide.PING, ctx.open_orders))[0]
                    ctx.cancel(order)
                elif ctx.curbar == 8:
                    assert(len(ctx.open_orders) == 1 and '撤单测试失败！')
                    assert(ctx.pos() == 1 and '持仓测试失败!')

                # 隔夜未成交订单自动清空。
                if ctx.curbar == 9:
                    ctx.sell(300, 1)
                elif ctx.curbar == 10:
                    assert(ctx.pos() == 0 and '持仓测试失败!')
                elif ctx.curbar > 1 and ctx.datetime[0].date() != ctx.datetime[1].date():
                    assert(ctx.pos() == 1 and '隔夜未成交订单清空测试失败')
                    assert(len(ctx.open_orders) == 0 and '隔夜未成交订单清空测试失败')

        set_symbols(['future.TEST-1.Minute'])
        s1 = DemoStrategy1('A1')
        s2 = DemoStrategy2('A2')
        s3 = DemoStrategy3('A3')
        profile = add_strategy([s1, s2, s3], {
            'capital': capital,
            'ratio': [0.3, 0.3, 0.4]
        })

        run()

        # 绘制k线，交易信号线
        # from quantdigger.digger import finance, plotting
        # plotting.plot_strategy(profile.data(), deals=profile.deals(0))

        all_holdings = profile.all_holdings()
        self.assertTrue(len(source) > 0 and len(source) == len(all_holdings), '模拟器测试失败！')
        self.assertAlmostEqual(lmg, 0.4)
        self.assertAlmostEqual(smg, 0.4)
        self.assertAlmostEqual(multi, 3)

        s1.test(self)
        s2.test(self)

        # test all_holdings
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


class TestOneDataOneCombination2(unittest.TestCase):

    def test_case2(self):
        """ 测试限价的延迟成交, 与是否是期货还是股票无关。
            测试延迟成交的资金占用
        """
        buy_entries, sell_entries = [], []
        short_entries, cover_entries = [], []

        class DemoStrategyBuy(Strategy):
            """ 只开多头仓位的策略 """

            def __init__(self, name):
                super(DemoStrategyBuy, self).__init__(name)
                self.cashes = []
                self.equities = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in buy_entries:
                    ctx.buy(ctx.low - OFFSET, 1)  # 确保在下一根Bar成交
                # 默认多头
                elif ctx.pos() > 0 and ctx.datetime[0].time() == st1:
                    ctx.sell(ctx.close, ctx.pos())
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                equities, cashes, open_equities, open_cashes, dts =\
                    in_closed_nextbar(source, buy_entries, capital / 4, lmg, smg, multi, 1)
                test.assertTrue(len(profile.all_holdings(0)) == len(equities) and len(equities) > 0, '模拟器测试失败！')
                for i, hd in enumerate(profile.all_holdings(0)):
                    test.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
                    test.assertAlmostEqual(hd['equity'], equities[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])

                for i in range(0, len(self.equities)):
                    test.assertAlmostEqual(self.equities[i], open_equities[i])
                for i in range(0, len(self.cashes)):
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])

        class DemoStrategyShort(Strategy):
            """ 只开空头仓位的策略 """
            def __init__(self, name):
                super(DemoStrategyShort, self).__init__(name)
                self.cashes = []
                self.equities = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in short_entries:
                    ctx.short(ctx.high + OFFSET, 1)
                elif ctx.pos('short') > 0 and ctx.datetime[0].time() == st1:
                    ctx.cover(ctx.close, ctx.pos('short'))
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                # short
                equities, cashes, open_equities, open_cashes, dts =\
                    in_closed_nextbar(source, short_entries, capital / 4, lmg, smg, multi, -1)
                test.assertTrue(len(profile.all_holdings(2)) == len(equities) and len(equities) > 0, '模拟器测试失败！')
                for i, hd in enumerate(profile.all_holdings(2)):
                    test.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
                    test.assertAlmostEqual(hd['equity'], equities[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])

                for i in range(0, len(self.equities)):
                    test.assertAlmostEqual(self.equities[i], open_equities[i])
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])

        class DemoStrategySell(Strategy):
            """ 只开多头仓位的策略 """
            def __init__(self, name):
                super(DemoStrategySell, self).__init__(name)
                self.cashes = []
                self.equities = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == bt1:
                    ctx.buy(ctx.close, 1)
                elif ctx.pos('long') > 0 and ctx.datetime[0] in sell_entries:
                    ctx.sell(ctx.high + OFFSET, ctx.pos())
                elif ctx.pos('long') > 0 and ctx.datetime[0].time() == st3:
                    ctx.sell(ctx.close, ctx.pos())
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                target, cashes, open_equities, open_cashes, dts =\
                    out_closed_nextbar(source, sell_entries, capital / 4, lmg, smg, multi, 1)
                test.assertTrue(len(profile.all_holdings(1)) == len(target) and
                                len(target) > 0, '模拟器测试失败！')
                for i, hd in enumerate(profile.all_holdings(1)):
                    test.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
                    test.assertAlmostEqual(hd['equity'], target[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])

                for i in range(0, len(self.cashes)):
                    test.assertAlmostEqual(self.equities[i], open_equities[i])
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])

        class DemoStrategyCover(Strategy):

            def __init__(self, name):
                super(DemoStrategyCover, self).__init__(name)
                self.cashes = []
                self.equities = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == bt1:
                    ctx.short(ctx.close, 1)
                elif ctx.pos('short') > 0 and ctx.datetime[0] in cover_entries:
                    ctx.cover(ctx.low - OFFSET, ctx.pos('short'))
                elif ctx.pos('short') > 0 and ctx.datetime[0].time() == st3:
                    ctx.cover(ctx.close, ctx.pos('short'))
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                target, cashes, open_equities, open_cashes, dts =\
                    out_closed_nextbar(source, cover_entries, capital / 4, lmg, smg, multi, -1)
                test.assertTrue(len(profile.all_holdings(3)) == len(target) and len(target) > 0, '模拟器测试失败！')
                for i, hd in enumerate(profile.all_holdings(3)):
                    test.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
                    test.assertAlmostEqual(hd['equity'], target[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])
                for i in range(0, len(self.cashes)):
                    test.assertAlmostEqual(self.equities[i], open_equities[i])
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])

        set_symbols(['future.TEST-1.Minute'])
        b1 = DemoStrategyBuy('B1')
        b2 = DemoStrategySell('B2')
        b3 = DemoStrategyShort('B3')
        b4 = DemoStrategyCover('B4')
        profile = add_strategy([b1, b2, b3, b4], {'capital': capital, 'ratio': [0.25, 0.25, 0.25, 0.25]})
        buy_entries, sell_entries, short_entries, cover_entries = entries_maked_nextbar(source)
        run()

        b1.test(self)
        b2.test(self)
        b3.test(self)
        b4.test(self)
        return


class TestOneDataOneCombination3(unittest.TestCase):

    def test_case(self):
        """ 策略: 多空市价开仓且当根bar成交
            买入点：[bt1, bt2, bt3]
            当天卖出点：[st1, st2]
        """

        class DemoStrategy(Strategy):
            def __init__(self, name):
                super(DemoStrategy, self).__init__(name)
                self.cashes = []
                self.equities = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(0, 1)
                    ctx.short(0, 2)
                else:
                    if curtime == st1:
                        assert(ctx.pos('long') == 3 and '持仓测试失败！')
                        ctx.sell(0, 2)
                        assert(ctx.pos('short') == 6 and '持仓测试失败！')
                        ctx.cover(0, 4)
                    elif curtime == st2:
                        assert(ctx.pos('long') == 1 and '持仓测试失败！')
                        ctx.sell(0, 1)
                        assert(ctx.pos('short') == 2 and '持仓测试失败！')
                        ctx.cover(0, 2)
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                target, cashes, open_equities, open_cashes, dts =\
                    market_trade_closed_curbar(source, capital, lmg, smg, multi)
                for i, hd in enumerate(profile.all_holdings()):
                    test.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
                    test.assertAlmostEqual(hd['equity'], target[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])

                for i in range(0, len(self.cashes)):
                    test.assertAlmostEqual(self.equities[i], open_equities[i])
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])

        set_symbols(['future.TEST-1.Minute'])
        c1 = DemoStrategy('C1')
        profile = add_strategy([c1], {'capital': capital})
        run()
        c1.test(self)


class TestOneDataOneCombination4(unittest.TestCase):

    def test_case(self):
        """ 测试跨合约交易的持仓, 资金, 持仓"""
        class DemoStrategy(Strategy):
            def __init__(self, name):
                super(DemoStrategy, self).__init__(name)
                self.cashes = []
                self.equities = []

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1)  # 默认future.TEST
                    ctx.short(ctx['future2.TEST-1.Minute'].close, 1, 'future2.TEST')
                else:
                    if curtime == st1:
                        for pos in ctx.all_positions():
                            if str(pos.contract) == 'FUTURE.TEST':
                                assert(pos.quantity == 3)
                                assert(pos.closable == 3)
                                assert(pos.direction == Direction.LONG)
                            else:
                                assert(pos.quantity == 3)
                                assert(pos.closable == 3)
                                assert(pos.direction == Direction.SHORT)

                        assert(ctx.pos('long', 'future.TEST') == 3 and '持仓测试失败！')
                        ctx.sell(ctx.close, 2)
                        assert(ctx.pos('short', 'future2.TEST') == 3 and '持仓测试失败！')
                        ctx.cover(ctx['future2.TEST-1.Minute'].close, 2, 'future2.TEST')
                    elif curtime == st2:
                        assert(ctx.pos('long', 'future.TEST') == 1 and '跨合约持仓测试失败！')
                        ctx.sell(ctx.close, 1, 'future.TEST')
                        assert(ctx.pos('short', 'future2.TEST') == 1 and '持仓测试失败！')
                        ctx.cover(ctx['future2.TEST-1.Minute'].close, 1, 'future2.TEST')
                self.cashes.append(ctx.cash())
                self.equities.append(ctx.equity())

            def test(self, test):
                fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'FUTURE2.csv')
                source2 = pd.read_csv(fname, parse_dates=True, index_col=0)
                global smg, multi
                target1, cashes1, t1, c1, dts = trade_closed_curbar(source, capital / 2, lmg, smg, multi, 1)
                # 期货
                multi = Contract.volume_multiple('future2.TEST')
                smg = Contract.short_margin_ratio('future2.TEST')
                target2, cashes2, t2, c2, dts = trade_closed_curbar(source2, capital / 2, lmg, smg, multi, -1)
                target = [x + y for x, y in zip(target1, target2)]
                cashes = [x + y for x, y in zip(cashes1, cashes2)]
                open_equities = [x + y for x, y in zip(t1, t2)]
                open_cashes = [x + y for x, y in zip(c1, c2)]

                test.assertTrue(len(self.cashes) == len(cashes), 'cash接口测试失败！')
                for i in range(0, len(self.cashes) - 1):  # 最后一根强平了无法比较
                    test.assertAlmostEqual(self.cashes[i], open_cashes[i])
                    test.assertAlmostEqual(self.equities[i], open_equities[i])

                for i, hd in enumerate(profile.all_holdings()):
                    test.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
                    test.assertAlmostEqual(hd['equity'], target[i])
                    test.assertAlmostEqual(hd['cash'], cashes[i])

        set_symbols(['future.TEST-1.Minute', 'future2.TEST-1.Minute'])
        d1 = DemoStrategy('D1')
        profile = add_strategy([d1], {'capital': capital})
        run()

        d1.test(self)


if __name__ == '__main__':
    unittest.main()
