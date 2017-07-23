# -*- coding: utf-8 -*-

import six
from six.moves import range
import datetime
import unittest
import pandas as pd
import os
from logbook import Logger
from quantdigger.datastruct import TradeSide, Contract, Direction
from quantdigger import (
    add_strategy,
    set_symbols,
    Strategy,
    settings,
    run
)

logger = Logger('test')
window_size = 0
capital = 20000000
OFFSET = 0.6
bt1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
bt2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
bt3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
st1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
st2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
st3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()
fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'FUTURE.csv')
source = pd.read_csv(fname, parse_dates=True, index_col=0)


class TestOneDataOneCombination(unittest.TestCase):
    """ 测试单数据单组合的价格撮合，持仓查询／默认持仓查询，可用资金等交易接口 """

    def test_case(self):
        """
        测试：
            1) 可平仓位。ctx.pos()
            2) profile.all_holdings 每根bar收盘时间的价格撮合。
            3) 都头买卖。ctx.buy, ctx.sell
        """
        # @TODO 持仓过夜，不卖，累加仓位。
        # @todo profile
        # signals 盈利

        # @TODO deals DemoStrategy2
        t_cashes0, t_cashes1 = [], []
        t_ocashes0 = []
        t_oequity0 = []
        t_equity0 = []

        class DemoStrategy1(Strategy):
            """ 限价只买多头仓位的策略 """

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
                ## 前一根的交易信号在当前价格撮合后的可用资金
                t_ocashes0.append(ctx.cash())
                t_oequity0.append(ctx.equity())
                t_cashes0.append(ctx.test_cash())
                t_equity0.append(ctx.test_equity())


        class DemoStrategy2(Strategy):
            """ 限价买多卖空的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1)
                    ctx.short(ctx.close, 2)
                else:
                    if curtime == st1:
                        assert(ctx.pos() == 3 and '默认持仓查询测试失败！')
                        ctx.sell(ctx.close, 2)
                        assert(ctx.pos('short') == 6 and '持仓测试失败！')
                        ctx.cover(ctx.close, 4)
                    elif curtime == st2:
                        assert(ctx.pos('long') == 1 and '持仓测试失败！')
                        ctx.sell(ctx.close, 1)
                        assert(ctx.pos('short') == 2 and '持仓测试失败！')
                        ctx.cover(ctx.close, 2)
                t_cashes1.append(ctx.test_cash())


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
                    assert(len(ctx.open_orders) == 2)
                    ctx.cancel(ctx.open_orders[0])
                    assert(len(ctx.open_orders) == 2 and '撤单测试失败')
                elif ctx.curbar == 4:
                    assert(len(ctx.open_orders) == 1 and '撤单测试失败！')
                elif ctx.curbar == 5:
                    assert(ctx.pos() == 1)
                    ctx.sell(300, 1) # 下无法成交的平仓，测试持仓。
                elif ctx.curbar == 7:
                    assert(ctx.pos() == 0 and '持仓测试失败!')
                    assert(len(ctx.open_orders) == 2 and '撤单测试失败！')
                    order = list(filter(lambda x: x.side == TradeSide.PING, ctx.open_orders))[0]
                    ctx.cancel(order)
                elif ctx.curbar == 8:
                    assert(len(ctx.open_orders) == 1 and '撤单测试失败！')
                    assert(ctx.pos() == 1 and '持仓测试失败!')
                if ctx.curbar > 1 and ctx.datetime[0].date() != ctx.datetime[1].date():
                    assert(len(ctx.open_orders) == 0 and '隔夜订单清空测试失败')

        set_symbols(['future.TEST-1.Minute'])
        profile = add_strategy([DemoStrategy1('A1'), DemoStrategy2('A2'), DemoStrategy3('A3')], {
            'capital': capital,
            'ratio': [0.3, 0.3, 0.4]
        })

        run()

        # 绘制k线，交易信号线
        #from quantdigger.digger import finance, plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(0))
        # all_holdings, cash()

        all_holdings = profile.all_holdings()
        all_holdings0 = profile.all_holdings(0)
        all_holdings1 = profile.all_holdings(1)
        all_holdings2 = profile.all_holdings(2)
        self.assertTrue(len(source) > 0 and len(source) == len(all_holdings), '模拟器测试失败！')

        lmg = Contract.long_margin_ratio('future.TEST')
        multi = Contract.volume_multiple('future.TEST')
        smg = Contract.short_margin_ratio('future.TEST')
        s_equity0, s_cashes0, s_oequity0, s_ocashes0, dts = buy_closed_curbar1(source, capital * 0.3, lmg, multi)
        for i in range(len(dts)):
            self.assertAlmostEqual(t_equity0[i], s_equity0[i])
            self.assertAlmostEqual(t_oequity0[i], s_oequity0[i])
            self.assertAlmostEqual(t_ocashes0[i], s_ocashes0[i])
            self.assertAlmostEqual(t_cashes0[i], s_cashes0[i])
        for i, hd in enumerate(all_holdings0):
            self.assertAlmostEqual(hd['equity'], s_equity0[i])
            self.assertAlmostEqual(hd['cash'], s_cashes0[i])
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
        # 最后一根强平了无法比较, 可以通过Profile的all_holding去比较
        for i in range(0, len(t_cashes0) - 1):
            self.assertAlmostEqual(t_cashes0[i], s_cashes0[i])

        #  确保资金够用，所以不影响
        e0, c0, dts = buy_closed_curbar(source, capital * 0.3 / 2, lmg, multi)
        e1, c1, dts = holdings_short_maked_curbar(source, capital * 0.3 / 2, smg, multi)
        s_equity1 = [x + y for x, y in zip(e0, e1)]
        s_cashes1 = [x + y for x, y in zip(c0, c1)]
        self.assertTrue(len(t_cashes1) == len(s_cashes1), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertAlmostEqual(hd['equity'], s_equity1[i])
        # 最后一根强平了无法比较, 可以通过Profile的all_holding去比较
        for i in range(0, len(t_cashes1) - 1):
            self.assertAlmostEqual(t_cashes1[i], s_cashes1[i])
        for i in range(0, len(profile.all_holdings())):
            hd = all_holdings[i]
            hd0 = all_holdings0[i]
            hd1 = all_holdings1[i]
            hd2 = all_holdings2[i]
            self.assertTrue(hd['cash'] == hd0['cash'] + hd1['cash'] + hd2['cash'],
                            'all_holdings接口测试失败！')
            self.assertTrue(hd['commission'] == hd0['commission'] +
                            hd1['commission'] + hd2['commission'], 'all_holdings接口测试失败！')
            self.assertTrue(hd['equity'] == hd0['equity'] + hd1['equity'] + hd2['equity'], 'all_holdings接口测试失败！')

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
        self.assertTrue(len(profile.all_holdings()) == len(s_equity0) and
                        len(s_equity0) > 0, 'holdings接口测试失败！')
        ## 绘制k线，交易信号线
        ##from quantdigger.digger import finance, plotting
        ##plotting.plot_strategy(profile.data(), deals=profile.deals(0))


    def test_case2(self):
        """ 测试限价的延迟成交, 与是否是期货还是股票无关。
            测试延迟成交的资金占用
        """
        buy_entries, sell_entries = [], []
        short_entries, cover_entries = [], []
        cashes0, cashes1, cashes2 = [], [], []

        class DemoStrategyBuy(Strategy):
            """ 只开多头仓位的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in buy_entries:
                    ctx.buy(ctx.low-OFFSET, 1) # 确保在下一根Bar成交
                # 默认多头
                elif ctx.pos() > 0 and ctx.datetime[0].time() == st1:
                    ctx.sell(ctx.close, ctx.pos())
                cashes0.append(ctx.test_cash())

        class DemoStrategyShort(Strategy):
            """ 只开空头仓位的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0] in short_entries:
                    ctx.short(ctx.high+OFFSET, 1)
                elif ctx.pos('short') > 0 and ctx.datetime[0].time() == st1:
                    ctx.cover(ctx.close, ctx.pos('short'))
                cashes1.append(ctx.test_cash())

        class DemoStrategySell(Strategy):
            """ 只开多头仓位的策略 """

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == bt1:
                    ctx.buy(ctx.close, 1)
                elif ctx.pos('long') > 0 and ctx.datetime[0] in sell_entries:
                    ctx.sell(ctx.high+OFFSET, ctx.pos())
                elif ctx.pos('long') > 0 and ctx.datetime[0].time() == st3:
                    ctx.sell(ctx.close, ctx.pos())
                cashes2.append(ctx.test_cash())

        class DemoStrategyCover(Strategy):

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                if ctx.datetime[0].time() == bt1:
                    ctx.short(ctx.close, 1)
                elif ctx.pos('short') > 0 and ctx.datetime[0] in cover_entries:
                    ctx.cover(ctx.low-OFFSET, ctx.pos('short'))
                elif ctx.pos('short') > 0 and ctx.datetime[0].time() == st3:
                    ctx.cover(ctx.close, ctx.pos('short'))

        set_symbols(['future.TEST-1.Minute'])
        profile = add_strategy([DemoStrategyBuy('B1'), DemoStrategySell('B2'),
                                DemoStrategyShort('B3'), DemoStrategyCover('B4')],{
                                    'capital': capital,
                                    'ratio': [0.25, 0.25, 0.25, 0.25]
                                  })
        buy_entries, sell_entries, short_entries, cover_entries = entries_maked_nextbar(source)
        run()
        # buy
        lmg = Contract.long_margin_ratio('future.TEST')
        multi = Contract.volume_multiple('future.TEST')
        smg = Contract.short_margin_ratio('future.TEST')
        target, cashes, dts = holdings_buy_maked_nextbar(source, buy_entries, capital/4, lmg, multi)
        self.assertTrue(len(profile.all_holdings(0)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(0)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertAlmostEqual(hd['equity'], target[i])

        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertAlmostEqual(cashes0[i],cashes[i])
        # short
        target, cashes, dts = holdings_short_maked_nextbar(source, short_entries, capital/4, smg, multi)
        self.assertTrue(len(profile.all_holdings(2)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(2)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertAlmostEqual(hd['equity'], target[i])
        for i in range(0, len(cashes1)-1):
            self.assertAlmostEqual(cashes1[i],cashes[i])
        ## sell
        target, cashes, dts = holdings_sell_maked_nextbar(source, sell_entries, capital/4, lmg, multi)
        self.assertTrue(len(profile.all_holdings(1)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertAlmostEqual(hd['equity'], target[i])
            self.assertAlmostEqual(hd['cash'], cashes[i])
        for i in range(0, len(cashes2)-1):
            self.assertAlmostEqual(cashes2[i],cashes[i])
        # cover
        target, cashes, dts = holdings_cover_maked_nextbar(source, cover_entries, capital/4, smg, multi)
        self.assertTrue(len(profile.all_holdings(3)) == len(target) and
                        len(target) > 0, '模拟器测试失败！')
        for i, hd in enumerate(profile.all_holdings(3)):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertAlmostEqual(hd['equity'], target[i])
            self.assertAlmostEqual(hd['cash'], cashes[i])

        #from quantdigger.digger import plotting
        #plotting.plot_strategy(profile.data(), deals=profile.deals(0))

        ## @TODO 模拟器make_market的运行次数
        return


    def test_case4(self):
        """ 测试市价成交 """
        cashes0 = []

        class DemoStrategy(Strategy):
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
                cashes0.append(ctx.test_cash())

        set_symbols(['future.TEST-1.Minute'])
        profile = add_strategy([DemoStrategy('C1')],{ 'capital': capital})
        run()
        lmg = Contract.long_margin_ratio('future.TEST')
        multi = Contract.volume_multiple('future.TEST')
        smg = Contract.short_margin_ratio('future.TEST')
        target, cashes, dts = holdings_buy_short_maked_market(source, capital,
                                                                lmg, smg, multi)
        self.assertTrue(len(cashes0) == len(cashes), 'cash接口测试失败！')
        for i, hd in enumerate(profile.all_holdings()):
            self.assertTrue(hd['datetime'] == dts[i], '模拟器测试失败！')
            self.assertAlmostEqual(hd['equity'], target[i])
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertAlmostEqual(cashes0[i],cashes[i])

    def test_case5(self):
        """ 测试跨合约交易的持仓, 资金 """
        cashes0 = []
        class DemoStrategy(Strategy):

            def on_init(self, ctx):
                """初始化数据"""
                pass

            def on_bar(self, ctx):
                curtime = ctx.datetime[0].time()
                if curtime in [bt1, bt2, bt3]:
                    ctx.buy(ctx.close, 1) # 默认future.TEST
                    ctx.short(ctx['future2.TEST-1.Minute'].close, 2, 'future2.TEST')
                else:
                    if curtime == st1:
                        for pos in ctx.all_positions():
                            if str(pos.contract) == 'FUTURE.TEST':
                                assert(pos.quantity == 3)
                                assert(pos.closable == 3)
                                assert(pos.direction == Direction.LONG)
                            else:
                                assert(pos.quantity == 6)
                                assert(pos.closable == 6)
                                assert(pos.direction == Direction.SHORT)

                        assert(ctx.pos('long', 'future.TEST') == 3 and '持仓测试失败！')
                        ctx.sell(ctx.close, 2)
                        assert(ctx.pos('short', 'future2.TEST') == 6 and '持仓测试失败！')
                        ctx.cover(ctx['future2.TEST-1.Minute'].close, 4, 'future2.TEST')
                    elif curtime == st2:
                        assert(ctx.pos('long', 'future.TEST') == 1 and '跨合约持仓测试失败！')
                        ctx.sell(ctx.close, 1, 'future.TEST')
                        assert(ctx.pos('short', 'future2.TEST') == 2 and '持仓测试失败！')
                        ctx.cover(ctx['future2.TEST-1.Minute'].close, 2, 'future2.TEST')
                cashes0.append(ctx.test_cash())

        set_symbols(['future.TEST-1.Minute', 'future2.TEST-1.Minute'])
        profile = add_strategy([DemoStrategy('D1')],{ 'capital': capital })
        run()
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'FUTURE2.csv')
        source2 = pd.read_csv(fname, parse_dates=True, index_col=0)

        lmg = Contract.long_margin_ratio('future.TEST')
        multi = Contract.volume_multiple('future.TEST')
        #  确保资金够用，所以不影响
        target1, cashes1, dts = buy_closed_curbar(source, capital/2, lmg, multi)
        # 期货
        multi = Contract.volume_multiple('future2.TEST')
        smg = Contract.short_margin_ratio('future2.TEST')
        target2, cashes2, dts = holdings_short_maked_curbar(source2, capital/2, smg, multi)
        target = [x + y for x, y in zip(target1, target2)]
        cashes = [x + y for x, y in zip(cashes1, cashes2)]
        self.assertTrue(len(cashes0) == len(cashes), 'cash接口测试失败！')
        for i in range(0, len(cashes0)-1): # 最后一根强平了无法比较
            self.assertAlmostEqual(cashes0[i],cashes[i])
        for i, hd in enumerate(profile.all_holdings()):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertAlmostEqual(hd['equity'], target[i])

def buy_closed_curbar1(data, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [bt1, bt2, bt3]
        当天卖出点: [st1, st2]
    """
    quantity = 0
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    unit = 1
    poscost = 0

    open_cashes = []
    open_equities = []
    open_close_profit = 0
    open_quantity = 0
    open_poscost = 0
    for dt, price in data.close.iteritems():
        open_price = data.open[dt]
        curtime = dt.time()
        if curtime in [bt1, bt2, bt3]:
            open_poscost = poscost
            poscost = (poscost*quantity + price*(1+settings['future_commission'])*unit) / (quantity+unit)
            open_quantity = quantity
            quantity += unit
        else:
            if curtime == st1:
                assert(quantity == unit*3)
                open_close_profit = close_profit
                open_quantity = quantity
                close_profit += (price * (1-settings['future_commission']) - poscost) *\
                                 2*unit * volume_multiple
                quantity -= 2 * unit
            elif curtime == st2:
                assert(quantity == unit*1)
                open_close_profit = close_profit
                open_quantity = quantity
                close_profit += (price*(1-settings['future_commission']) - poscost) *\
                                unit * volume_multiple
                quantity = 0
            else:
                # 非交易节点
                open_quantity = quantity
                open_poscost = poscost
                open_close_profit = close_profit

        if dt == data.index[-1]:
            # 强平现有持仓
            close_profit += (price*(1-settings['future_commission']) - poscost) *\
                             quantity* volume_multiple
            open_close_profit += (open_price*(1-settings['future_commission']) - open_poscost) *\
                            open_quantity * volume_multiple
            open_quantity = quantity
            quantity = 0

        pos_profit = (price-poscost) * volume_multiple * quantity # 持仓盈亏
        posmargin = price * quantity * volume_multiple * long_margin
        equities.append(capital + close_profit + pos_profit)
        cashes.append(equities[-1] - posmargin)

        open_pos_profit = (open_price-open_poscost) * volume_multiple * open_quantity
        open_posmargin = open_price * open_quantity * volume_multiple * long_margin
        open_equities.append(capital + open_close_profit + open_pos_profit)
        open_cashes.append(open_equities[-1] - open_posmargin)
        dts.append(dt)
    return equities, cashes, open_equities, open_cashes, dts

def buy_closed_curbar(data, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [bt1, bt2, bt3]
        当天卖出点: [st1, st2]
    """
    quantity = 0
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    UNIT = 1
    poscost = 0
    for dt, price in data.close.iteritems():
        curtime = dt.time()
        if curtime in [bt1, bt2, bt3]:
            poscost = (poscost*quantity + price*(1+settings['future_commission'])*UNIT)/ (quantity+UNIT)
            quantity += UNIT
        else:
            if curtime == st1:
                assert(quantity == UNIT*3)
                close_profit += (price*(1-settings['future_commission']) - poscost) *\
                                2*UNIT * volume_multiple
                quantity -= 2 * UNIT
            elif curtime == st2:
                assert(quantity == UNIT*1)
                close_profit += (price*(1-settings['future_commission']) - poscost) *\
                                UNIT * volume_multiple
                quantity = 0
        if dt == data.index[-1]:
            # 强平现有持仓
            close_profit += (price*(1-settings['future_commission']) - poscost) *\
                            quantity* volume_multiple
            quantity = 0
        pos_profit = (price-poscost)*volume_multiple * quantity # 持仓盈亏
        equities.append(capital+close_profit+pos_profit)
        posmargin = price * quantity * volume_multiple * long_margin
        cashes.append(equities[-1]-posmargin)
        dts.append(dt)
        #if close_profit != 0 or pos_profit != 0:
            #print close_profit, pos_profit, equities[-1]
            #assert False
    return equities, cashes, dts

def holdings_short_maked_curbar(data, capital, short_margin, volume_multiple):
    """ 策略: 空头限价开仓且当根bar成交
        买入点：[bt1, bt2, bt3]
        当天卖出点：[st1, st2]
    """
    quantity = 0
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    UNIT = 2
    poscost = 0
    for dt, price in data.close.iteritems():
        curtime = dt.time()
        if curtime in [bt1, bt2, bt3]:
            poscost = (poscost*quantity + price*(1-settings['future_commission'])*UNIT)/ (quantity+UNIT)
            quantity += UNIT
        else:
            if curtime == st1:
                assert(quantity == UNIT*3)
                close_profit -= (price*(1+settings['future_commission']) - poscost) *\
                                2*UNIT * volume_multiple
                quantity -= UNIT * 2
            elif curtime == st2:
                assert(quantity == UNIT)
                close_profit -= (price*(1+settings['future_commission']) - poscost) *\
                                UNIT * volume_multiple
                quantity = 0
        if dt == data.index[-1]:
            # 强平现有持仓
            close_profit -= (price*(1+settings['future_commission']) - poscost) *\
                            quantity * volume_multiple
            quantity = 0
         # 持仓盈亏
        pos_profit = (poscost-price)*volume_multiple * quantity # 持仓盈亏
        equities.append(capital+close_profit+pos_profit)
        posmargin = price * quantity * volume_multiple * short_margin
        cashes.append(equities[-1]-posmargin)
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
        if dt.date() == predt.date() and dt.time() < st1 and prelow - low >= OFFSET:
            buy_entries.append(predt)
        prelow = low
        predt = dt

    for  dt, high in data.high.iteritems():
        if dt.date() == predt.date() and dt.time() < st1 and high - prehigh >= OFFSET:
            short_entries.append(predt)
            #print predt, low-prelow
        prehigh = high
        predt = dt

    for dt, high in data.high.iteritems():
        if dt.time() > bt3 and high - prehigh >= OFFSET:
            sell_entries.append(predt)
            #print predt, high-prehigh
        prehigh = high
        predt = dt

    for  dt, low in data.low.iteritems():
        if dt.time() > bt3 and prelow - low >= OFFSET:
            cover_entries.append(predt)
            #print predt, low-prelow
        prelow = low
        predt = dt
    return buy_entries, sell_entries, short_entries, cover_entries

def holdings_buy_maked_nextbar(data, buy_entries, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且下一根bar成交
        买入点：[相关bar的最低点减去OFFSET]
        当天卖出点：st1
    """
    close_profit = 0    # 累计平仓盈亏
    equities = []
    dts = []
    cashes = []
    prelow = data.low[0]
    trans_entries = list(map(lambda x: x+datetime.timedelta(minutes = 1), buy_entries))
    quantity = 0
    poscost = 0
    preclose = 0
    UNIT = 1
    for dt, low in data.low.iteritems():
        curtime = dt.time()
        close = data.close[dt]
        if dt in trans_entries:
            # 交易成交时间点
            poscost = (poscost*quantity + (prelow-OFFSET)*(1+settings['future_commission'])*UNIT)/ (quantity+UNIT)
            quantity += UNIT
        elif curtime == st1 or dt == data.index[-1]:
            close_profit += (close*(1-settings['future_commission']) - poscost) *\
                            quantity * volume_multiple
            quantity = 0
        pos_profit = (close-poscost)*volume_multiple * quantity # 持仓盈亏
        equities.append(close_profit+pos_profit+capital)
        posmargin =  close* quantity * volume_multiple * long_margin
        cashes.append(equities[-1]-posmargin)
        if dt in trans_entries:
            # 算上未成交单的资金占用, 修改成交点的上一个cash
            cashes[-2] -= preclose * volume_multiple * long_margin
        dts.append(dt)
        prelow = low
        preclose = close
    return equities, cashes, dts

def holdings_short_maked_nextbar(data, buy_entries, capital, short_margin, volume_multiple):
    """ 策略: 空头限价开仓且下一根bar成交
        买入点：[相关bar的最高点加上OFFSET]
        当天卖出点：st1
    """
    equities = []
    dts = []
    cashes = []
    prehigh = data.high[0]
    trans_entries = list(map(lambda x: x+datetime.timedelta(minutes = 1), buy_entries))
    poscost = 0
    quantity = 0
    preclose = 0
    close_profit = 0    # 累计平仓盈亏
    UNIT = 1
    for dt, high in data.high.iteritems():
        curtime = dt.time()
        close = data.close[dt]
        if dt in trans_entries:
            poscost = (poscost*quantity + (prehigh+OFFSET)*(1-settings['future_commission'])*UNIT)/ (quantity+UNIT)
            quantity += UNIT
        elif curtime == st1 or dt == data.index[-1]:
            close_profit -= (close*(1+settings['future_commission']) - poscost) *\
                            quantity * volume_multiple
            quantity = 0
        pos_profit = -(close-poscost)*volume_multiple * quantity # 持仓盈亏
        equities.append(close_profit+pos_profit+capital)
        posmargin = close * quantity * volume_multiple * short_margin
        cashes.append(equities[-1]-posmargin)
        if dt in trans_entries:
            # 算上未成交单的资金占用, 修改成交点的上一个cash
            cashes[-2] -= preclose * volume_multiple * short_margin
        dts.append(dt)
        prehigh = high
        preclose = close
    return equities, cashes, dts

def holdings_sell_maked_nextbar(data, sell_entries, capital, long_margin, volume_multiple):
    """ 策略: 多头限价平仓且下一根bar成交
        买入点：[相关bar的最高点加上OFFSET]
        当天卖出点：st1
    """
    close_profit = 0    # 累计平仓盈亏
    equities = []
    cashes = []
    dts = []
    # 从平仓点计算平仓成交点
    trans_entries = list(map(lambda x: x+datetime.timedelta(minutes = 1), sell_entries))
    bprice = None
    prehigh = data.high[0]
    for dt, high in data.high.iteritems():
        close = data.close[dt]
        if dt.time() == bt1:
            bprice = close * (1+settings['future_commission'])
        elif bprice and dt in trans_entries:
            close_profit += ((prehigh+OFFSET)*(1-settings['future_commission'])-bprice) * volume_multiple
            bprice = None
        elif dt == data.index[-1] or dt.time() == st3:
            # 最后一根, 强平现有持仓
            # 不隔日
            if bprice:
                close_profit += (close*(1-settings['future_commission']) - bprice) * volume_multiple
            bprice = None
        pos_profit = 0 # 持仓盈亏
        posmargin = 0
        if bprice:
            pos_profit += (close - bprice) * volume_multiple
            posmargin = close * volume_multiple * long_margin # quantity == 1
        equities.append(close_profit+pos_profit+capital)
        cashes.append(equities[-1]-posmargin)
        dts.append(dt)
        prehigh = high
    return equities, cashes, dts

def holdings_cover_maked_nextbar(data, cover_entries, capital, short_margin, volume_multiple):
    """ 策略: 空头限价平仓且下一根bar成交
        买入点：[相关bar的最低点减去OFFSET]
        当天卖出点：st1
    """
    ## @TODO 11号无法成交，可用来测试“去隔夜单”
    ## @TODO c测试股票的可平数量
    close_profit = 0    # 累计平仓盈亏
    equities = []
    cashes = []
    dts = []
    trans_entries = list(map(lambda x: x+datetime.timedelta(minutes = 1), cover_entries))
    bprice = None
    prelow = data.low[0]
    for dt, low in data.low.iteritems():
        close = data.close[dt]
        if dt.time() == bt1:
            bprice = close * (1-settings['future_commission'])
        elif bprice and dt in trans_entries:
            close_profit -= ((prelow-OFFSET)*(1+settings['future_commission'])-bprice) * volume_multiple
            bprice = None
        elif dt == data.index[-1] or dt.time() == st3:
            # 最后一根, 强平现有持仓
            # 不隔日
            if bprice:
                close_profit -= (close*(1+settings['future_commission']) - bprice) * volume_multiple
            bprice = None
        pos_profit = 0 # 持仓盈亏
        posmargin = 0
        if bprice:
            pos_profit -= (close - bprice) * volume_multiple
            posmargin = close * volume_multiple * short_margin # quantity == 1
        equities.append(close_profit+pos_profit+capital)
        cashes.append(equities[-1]-posmargin)
        dts.append(dt)
        prelow = low
    return equities, cashes, dts


def holdings_buy_short_maked_market(data, capital, long_margin, short_margin,
                                    volume_multiple):
    """ 策略: 多空市价开仓且当根bar成交
        买入点：[bt1, bt2, bt3]
        当天卖出点：[st1, st2]
    """
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []
    lquantity = 0
    squantity = 0
    lposcost = 0
    sposcost = 0
    for index, row in data.iterrows():
        close = row['close']
        dt = index
        high, low = row['high'], row['low']
        curtime = dt.time()
        if curtime in [bt1, bt2, bt3]:
            lposcost = (lposcost*lquantity + high*(1+settings['future_commission'])) / (lquantity+1)
            sposcost = (sposcost*squantity + low*(1-settings['future_commission'])*2) / (squantity+2)
            lquantity += 1
            squantity += 2
        else:
            if curtime == st1:
                assert(lquantity == 3)
                close_profit += (low*(1-settings['future_commission'])-lposcost) * 2  * volume_multiple
                lquantity = 1
                assert(squantity == 6)
                close_profit -= (high*(1+settings['future_commission'])-sposcost) * 4 * volume_multiple
                squantity = 2
            elif curtime == st2:
                assert(lquantity == 1)
                close_profit += (low*(1-settings['future_commission'])-lposcost) * volume_multiple
                lquantity = 0
                #assert(squantity == 2)
                close_profit -= (high*(1+settings['future_commission'])-sposcost) * 2 * volume_multiple
                squantity = 0

        if dt == data.index[-1]:
            # 强平现有持仓
            close_profit += (close*(1-settings['future_commission'])-sposcost)*lquantity*volume_multiple
            close_profit -= (close*(1+settings['future_commission'])-sposcost)*squantity*volume_multiple
            lquantity = 0
            squantity = 0
        pos_profit = (close-lposcost) * lquantity * volume_multiple
        pos_profit -= (close-sposcost) * squantity * volume_multiple
        equities.append(capital+close_profit+pos_profit)
        posmargin = close * lquantity * long_margin * volume_multiple
        posmargin += close * squantity * short_margin * volume_multiple
        cashes.append(equities[-1]-posmargin)
        dts.append(dt)
    return equities, cashes, dts


if __name__ == '__main__':
    unittest.main()
