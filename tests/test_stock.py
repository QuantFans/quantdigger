# -*- coding: utf-8 -*-
##
# @file test_blotter.py
# @brief 测试模拟器的价格撮合, 当前持仓，权益，可用资金等。
# @author wondereamer
# @version 0.3
# @date 2015-01-06

import six
import datetime
import unittest
import pandas as pd
import os
from quantdigger.datastruct import  Contract
from quantdigger import *
from logbook import Logger
logger = Logger('test')
capital = 200000000
OFFSET = 0.6
buy1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
buy2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
buy3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
sell1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
sell2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
sell3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()
fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'STOCK.csv')
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

        set_symbols(['stock.TEST-1.Minute'])
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
            self.assertAlmostEqual(t_cashes0[i],s_cashes0[i])
        self.assertTrue(len(all_holdings) == len(s_equity0), 'all_holdings接口测试失败！')
        for i, hd in enumerate(all_holdings0):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertAlmostEqual(hd['equity'], s_equity0[i])

        #  确保资金够用，所以不影响
        e0, c0, dts = holdings_buy_maked_curbar(source, capital*0.3/2, lmg, multi)
        e1, c1, dts = holdings_short_maked_curbar(source, capital*0.3/2, smg, multi)
        s_equity1 = [x + y for x, y in zip(e0, e1)]
        s_cashes1 = [x + y for x, y in zip(c0, c1)]
        for i, hd in enumerate(profile.all_holdings(1)):
            self.assertTrue(hd['datetime'] == dts[i], 'all_holdings接口测试失败！')
            self.assertAlmostEqual(hd['equity'], s_equity1[i])
        self.assertTrue(len(t_cashes1) == len(s_cashes1), 'cash接口测试失败！')
        for i in range(0, len(t_cashes1)-1): # 最后一根强平了无法比较
            self.assertAlmostEqual(t_cashes1[i],s_cashes1[i])

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
            poscost = (poscost * quantity + curprice*(1+settings['stock_commission'])*UNIT) / (quantity+UNIT)
            buy_quantity[curdate] += UNIT
        else:
            if curtime == sell1:
                for posdate, quantity in six.iteritems(buy_quantity):
                    if posdate < curdate and quantity > 0:
                        close_profit += (curprice*(1-settings['stock_commission'])-poscost) *\
                                        2*UNIT * volume_multiple
                        buy_quantity[posdate] -= 2*UNIT
                    elif posdate > curdate:
                        assert(False)
            elif curtime == sell2:
                for posdate, quantity in six.iteritems(buy_quantity):
                    if posdate < curdate and quantity > 0:
                        close_profit += (curprice*(1-settings['stock_commission'])-poscost) *\
                                        UNIT * volume_multiple
                        buy_quantity[posdate] -= UNIT
                        assert(buy_quantity[posdate] == 0)
                    elif posdate > curdate:
                        assert(False)
        if curdt == data.index[-1]:
            # 强平现有持仓
            quantity = sum(buy_quantity.values())
            close_profit += (curprice*(1-settings['stock_commission'])-poscost) *\
                            quantity * volume_multiple
            buy_quantity.clear()

        quantity = sum(buy_quantity.values())
        pos_profit += (curprice - poscost) * quantity * volume_multiple
        equities.append(capital+close_profit+pos_profit)
        posmargin = curprice * quantity * volume_multiple * long_margin
        cashes.append(equities[-1]-posmargin)
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
            poscost = (poscost * quantity + curprice*(1-settings['stock_commission'])*UNIT) / (quantity+UNIT)
            short_quantity[curdate] += UNIT
        else:
            if curtime == sell1:
                for posdate, quantity in six.iteritems(short_quantity):
                    if posdate < curdate and quantity > 0:
                        close_profit -= (curprice*(1+settings['stock_commission'])-poscost) *\
                                        2*UNIT * volume_multiple
                        short_quantity[posdate] -= 2*UNIT
                    elif posdate > curdate:
                        assert(False)
            elif curtime == sell2:
                for posdate, quantity in six.iteritems(short_quantity):
                    if posdate < curdate and quantity > 0:
                        close_profit -= (curprice*(1+settings['stock_commission'])-poscost) *\
                                        UNIT * volume_multiple
                        short_quantity[posdate] -= UNIT
                        assert(short_quantity[posdate] == 0)
                    elif posdate > curdate:
                        assert(False)
        if curdt == data.index[-1]:
            # 强平现有持仓
            quantity = sum(short_quantity.values())
            close_profit -= (curprice*(1+settings['stock_commission'])-poscost) *\
                            quantity * volume_multiple
            short_quantity.clear()

        quantity = sum(short_quantity.values())
        pos_profit -= (curprice - poscost) * quantity * volume_multiple
        equities.append(capital+close_profit+pos_profit)
        posmargin= curprice * quantity * volume_multiple * short_margin
        cashes.append(equities[-1]-posmargin)
        dts.append(curdt)
    return equities, cashes, dts


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


def buy_monday_sell_friday(data, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [buy1, buy2, buy3]
        当天卖出点: [sell1, sell2]
    """
    assert(volume_multiple == 1 and long_margin == 1)
    UNIT = 1
    poscost = 0
    quantity = 0
    close_profit = 0
    equities = {} # 累计平仓盈亏
    dts = []
    cashes = { }
    for curdt, curprice in data.close.iteritems():
        pos_profit = 0
        weekday = curdt.weekday()
        if weekday == 0:
            poscost = (poscost * quantity + curprice*(1+settings['stock_commission'])*UNIT) / (quantity+UNIT)
            quantity += UNIT
        else:
            if weekday == 4 and quantity>0:
                close_profit += (curprice*(1-settings['stock_commission'])-poscost) *\
                                quantity * volume_multiple
                quantity = 0
        pos_profit += (curprice - poscost) * quantity * volume_multiple
        equities[curdt] = capital+close_profit+pos_profit
        posmargin = curprice * quantity * volume_multiple * long_margin
        cashes[curdt] = capital+close_profit+pos_profit -posmargin
        dts.append(curdt)
    return equities, cashes, dts



if __name__ == '__main__':
    unittest.main()
