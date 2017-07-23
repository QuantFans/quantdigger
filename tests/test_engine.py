# encoding: utf-8

import six
from six.moves import range
import datetime
import unittest
import pandas as pd
import os
import talib
import numpy as np
from quantdigger.util.log import gen_log as logger
from quantdigger import (
    add_strategy,
    NumberSeries,
    DateTimeSeries,
    MA,
    BOLL,
    set_symbols,
    Strategy,
    run
)


class TestSeries(unittest.TestCase):
    """
    测试：
    * 序列变量
        1）用户时间，数字序列变量。
        2）序列变量回溯引用。      ctx.open[3]
        3) 序列变量和数值的运算。ctx.open-0
        4) NumberSeries.DEFAULT_VALUE, DateTimeSeries.DEFAULT_VALUE
        5) open, close, high, low, volume, datetime等系统序列变量值。
    * 普通变量。   ctx.curbar_list
    * ctx.curbar。  ctx.curbar_list
    """
    def test_case(self):
        close, open, dt, high, low, volume = [], [], [], [], [], []
        open3, dt3 = [], []
        operator_test = []
        user_vars = {
            'curbar_list': [],
            'numseries': [],
            'numseries3': [],
            'dtseries': [],
        }

        class DemoStrategy(Strategy):
            def on_init(self, ctx):
                """初始化数据"""
                ctx.ma3 = MA(ctx.close, 3)
                ctx.numseries = NumberSeries()
                ctx.dtseries = DateTimeSeries()
                ctx.curbar_list = []

            def on_symbol(self, ctx):
                # @TODO * /
                operator_test.append(ctx.open - 0 == ctx.open[0])
                operator_test.append(ctx.close - 0 == ctx.close[0])
                operator_test.append(ctx.high + 0 == ctx.high[0])
                operator_test.append(ctx.low + 0 == ctx.low[0])
                operator_test.append(ctx.volume + 0 == ctx.volume[0])
                open.append(ctx.open[0])
                close.append(ctx.close[0])
                high.append(ctx.high[0])
                low.append(ctx.low[0])
                volume.append(int(ctx.volume[0]))
                dt.append(ctx.datetime[0])
                open3.append(ctx.open[3])
                dt3.append(ctx.datetime[3])

                if ctx.curbar >= 100 and ctx.curbar < 300:
                    ctx.numseries.update(100)
                    ctx.dtseries.update(datetime.datetime(1000, 1, 1))
                elif ctx.curbar >= 300:
                    ctx.dtseries.update(datetime.datetime(3000, 1, 1))
                    ctx.numseries.update(300)
                ctx.curbar_list.append(ctx.curbar)
                user_vars['numseries3'].append(ctx.numseries[3])
                user_vars['numseries'].append(ctx.numseries[0])
                user_vars['dtseries'].append(ctx.dtseries[0])
                user_vars['curbar_list'] = ctx.curbar_list

        set_symbols(['BB.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1')])
        run()

        # 序列变量默认值
        self.assertTrue(NumberSeries.DEFAULT_VALUE == 0.0, "默认值测试失败")
        self.assertTrue(DateTimeSeries.DEFAULT_VALUE == datetime.datetime(1980, 1, 1), "默认值测试失败")
        self.assertTrue(all(operator_test), "类型转化错误!")

        # 系统序列变量测试
        target = pd.DataFrame({
            'open': open,
            'close': close,
            'high': high,
            'low': low,
            'volume': volume
        })
        target.index = dt
        target = target.loc[:, ['open', 'close', 'high', 'low', 'volume']]
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'BB.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertTrue(source.equals(target), "系统时间序列变量正测试出错")
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'CC.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertFalse(source.equals(target), "系统时间序列变量反测试出错")

        # ctx.curbar，用户普通变量测试
        for i in range(0, len(user_vars['curbar_list'])):
            self.assertTrue(i + 1 == user_vars['curbar_list'][i])
        self.assertTrue(len(user_vars['numseries'])==len(open) and len(open)>0, '系列变量长度不一致')
        logger.info('-- 用户普通变量测试成功 --')
        logger.info('-- curbar测试成功 --')

        # 用户序列变量
        numseries = user_vars['numseries']
        dtseries = user_vars['dtseries']
        dt1980 = datetime.datetime(1980, 1, 1)
        dt1000 = datetime.datetime(1000, 1, 1)
        dt3000 = datetime.datetime(3000, 1, 1)
        for i in range(0, len(numseries)):
            # 用户序列变量自动追加测试成功
            if i < 99:
                self.assertTrue(numseries[i] == NumberSeries.DEFAULT_VALUE, '用户数字序列变量测试失败!')
                self.assertTrue(dtseries[i] == dt1980, '用户时间序列变量测试失败!')
            elif i >= 99 and i < 299:
                self.assertTrue(numseries[i] == 100, '用户数字序列变量测试失败!')
                self.assertTrue(dtseries[i] == dt1000, '用户时间序列变量测试失败!')
            elif i >= 299:
                self.assertTrue(numseries[i] == 300, '用户数字序列变量测试失败!')
                self.assertTrue(dtseries[i] == dt3000, '用户时间序列变量测试失败!')

        # 序列变量回溯测试
        for i in range(0, len(open)):
            if i - 3 >= 0:
                self.assertTrue(open3[i] == open[i - 3], "系统序列变量回溯测试失败！")
                self.assertTrue(dt3[i] == dt[i - 3], "系统序列变量回溯测试失败！")
                self.assertTrue(user_vars['numseries3'][i] == numseries[i - 3], "用户序列变量回溯测试失败！")
            else:
                self.assertTrue(open3[i] == NumberSeries.DEFAULT_VALUE, "系统序列变量回溯测试失败！")
                self.assertTrue(user_vars['numseries3'][i] == NumberSeries.DEFAULT_VALUE, "用户序列变量回溯测试失败！")
                self.assertTrue(dt3[i] == DateTimeSeries.DEFAULT_VALUE, "系统序列时间变量回溯测试失败！")
        logger.info('-- 序列变量测试成功 --')


class TestTechnical(unittest.TestCase):

    def test_case(self):
        """
        测试：
        * 指标变量
            1) 指标变量和数值间的运算。 ctx.ma2 - 0
            2) 指标变量回溯  ctx.ma2[3]
            3) 单值和多值测试
        """
        close, open, ma, ma3, tech_operator = [], [], [], [], []
        boll = {
            'upper': [],
            'middler': [],
            'lower': []
        }
        boll3 = {
            'upper': [],
            'middler': [],
            'lower': []
        }

        class DemoStrategy(Strategy):
            def on_init(self, ctx):
                """初始化数据"""
                ctx.ma = MA(ctx.close, 2)
                ctx.boll = BOLL(ctx.close, 2)

            def on_symbol(self, ctx):
                if ctx.curbar>=2:
                    # @todo + * /
                    tech_operator.append(ctx.ma - 0 == ctx.ma[0])

                ma3.append(ctx.ma[3])
                ma.append(ctx.ma[0])
                close.append(ctx.close[0])
                open.append(ctx.open[0])
                boll['upper'].append(float(ctx.boll['upper']))
                boll['middler'].append(ctx.boll['middler'][0])
                boll['lower'].append(ctx.boll['lower'][0])
                boll3['upper'].append(ctx.boll['upper'][3])
                boll3['middler'].append(ctx.boll['middler'][3])
                boll3['lower'].append(ctx.boll['lower'][3])
                assert(isinstance(ctx.boll['lower'], NumberSeries))
                assert(isinstance(ctx.ma, MA))

        set_symbols(['BB.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1')])
        run()

        # 单值指标运算和回溯测试
        source_ma = talib.SMA(np.asarray(close), 2)
        self.assertTrue(all(tech_operator), "指标运算错误!")
        self.assertFalse(ma[0] == ma[0], "指标NaN值测试失败!")
        for source, target in zip(source_ma[1:], ma[1:]):
            self.assertTrue(target == source, "单值指标计算测试失败!")
        for source, target in zip(ma[1:], ma3[4:]):
            self.assertTrue(target == source, "单值指标回溯测试失败!")
        for nan in ma3[:4]:
            self.assertFalse(nan == nan, "单值指标回溯NaN值测试失败!")
        logger.info('-- 单值指标测试成功 --')

        # 多值指标运算和回溯测试
        upper, middler, lower = talib.BBANDS(np.asarray(close), 2, 2, 2)
        ta_boll = {
            'upper': upper,
            'middler': middler,
            'lower': lower
        }
        for v in ['upper', 'lower', 'middler']:
            self.assertFalse(boll[v][0] == boll[v][0], "多值指标NaN值测试失败!")
            for source, target in zip(ta_boll[v][1:], boll[v][1:]):
                self.assertTrue(target == source, "多值指标计算测试失败!")
            for nan in boll3[v][:4]:
                self.assertFalse(nan == nan, "多值指标回溯NaN值测试失败!")
            for source, target in zip(boll[v][1:], boll3[v][4:]):
                self.assertTrue(target == source, "多值指标回溯测试失败!")
        logger.info('-- 多值指标测试成功 --')
        logger.info('***** 指标测试成功 *****\n')


class TestMainFunction(unittest.TestCase):
    def test_case(self):
        """
        案例：两个策略组合，每个策略组合下分别有两个策略，每个组合运行于两个周期合约中。
        测试：on_bar, on_symbol, on_exit 的运行频次，数据和策略遍历的粗粒度测试;
              ctx.prontract, ctx.strategy
        """
        on_exit = {
            'strategy': [],
        }
        on_bar = {
            'strategy': [],
        }
        on_symbol = {
            'combination': set(),
            'step_num': 0
        }

        class DemoStrategy(Strategy):

            def on_init(self, ctx):
                """初始化数据"""
                return

            def on_symbol(self, ctx):
                # six.print_(ctx.strategy, ctx.pcontract)
                on_symbol['combination'].add((str(ctx.pcontract), ctx.strategy))
                on_symbol['step_num'] += 1

            def on_bar(self, ctx):
                on_bar['strategy'].append(ctx.strategy)

            def on_exit(self, ctx):
                on_exit['strategy'].append(ctx.strategy)

        set_symbols(['BB.TEST-1.Minute', 'AA.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1'), DemoStrategy('A2')])
        add_strategy([DemoStrategy('B1'), DemoStrategy('B2')])
        run()

        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'BB.csv')
        blen = len(pd.read_csv(fname))
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'AA.csv')
        alen = len(pd.read_csv(fname))
        sample = set([
            ('BB.TEST-1.MINUTE', 'A1'),
            ('BB.TEST-1.MINUTE', 'A2'),
            ('AA.TEST-1.MINUTE', 'A1'),
            ('AA.TEST-1.MINUTE', 'A2'),
            ('BB.TEST-1.MINUTE', 'B1'),
            ('BB.TEST-1.MINUTE', 'B2'),
            ('AA.TEST-1.MINUTE', 'B1'),
            ('AA.TEST-1.MINUTE', 'B2')
        ])
        self.assertTrue(alen > 0 and blen > 0)

        # 测试on_symbol
        self.assertTrue(on_symbol['combination'] == sample, "on_symbol测试失败!")
        self.assertTrue(on_symbol['step_num'] == alen * 4 + blen * 4, "on_symbol测试失败!")
        self.assertTrue(['A1', 'A2', 'B1', 'B2'] * max(blen, alen) == on_bar['strategy'],
                        'on_bar测试失败！')
        self.assertTrue(['A1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        logger.info('-- 策略on_xxx主函数测试成功 --')


class TestTimeAlign(unittest.TestCase):
    """
        案例：不同时间长度和不同时间步频的数据下策略组合的合约时间对齐和数据引用。
        测试：合约名称大小写不敏感。
              on_symbol时间对齐
              on_bar时间对齐, 跨合约数据引用（只测了时间）
        Note: 更多细节看'diffPeriodOnSymbol.txt', 'diffPeriodOnSymbol.txt'。
    """

    def test_case(self):
        on_bar_timestep = []
        on_symbol_timestep = []

        class DemoStrategy(Strategy):

            def on_init(self, ctx):
                """初始化数据"""
                return

            def on_symbol(self, ctx):
                on_symbol_timestep.append("%s %s %s %s" % (ctx.pcontract,
                                          ctx.strategy, ctx.datetime, ctx.curbar))

            def on_bar(self, ctx):
                t = ctx['oneday.TEST-1.Minute']
                on_bar_timestep.append("%s %s %s" % (t.pcontract, t.datetime, t.curbar))
                t = ctx['TWODAY.TEST-5.Second']
                on_bar_timestep.append("%s %s %s" % (t.pcontract, t.datetime, t.curbar))

        set_symbols(['TWODAY.TEST-5.Second', 'oneday.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1'), DemoStrategy('A2')])
        add_strategy([DemoStrategy('B1'), DemoStrategy('B2')])
        run()

        # on_symbol
        fname = os.path.join(os.getcwd(), 'data', 'diffPeriodOnSymbol.txt')
        with open(fname) as f:
            lines = [line.rstrip('\n') for line in f]
        assert(len(lines) > 0)
        count = 0
        for line in lines:
            if line.startswith("*"):
                continue
            self.assertTrue(on_symbol_timestep[count] == line, "on_symbol时间对齐失败")
            count += 1

        # on_bar
        fname = os.path.join(os.getcwd(), 'data', 'diffPeriodOnBar.txt')
        lines = [line.rstrip('\n') for line in open(fname)]
        assert(len(lines) > 0)
        count = 0
        for line in lines:
            if line.startswith("*"):
                continue
            self.assertTrue(on_bar_timestep[count] == line, "on_bar时间对齐失败")
            count += 1
        logger.info('on_symbol, on_bar 时间对齐测试成功！')


class TestDefaultPContract(unittest.TestCase):

    def test_case(self):
        class DemoStrategy(Strategy):

            def on_init(self, ctx):
                """初始化数据"""
                return

            def on_bar(self, ctx):
                assert(ctx.open == ctx['TWODAY.TEST-5.Second'].open)
                assert(ctx.close == ctx['TWODAY.TEST-5.Second'].close)
                assert(ctx.high == ctx['TWODAY.TEST-5.Second'].high)
                assert(ctx.low == ctx['TWODAY.TEST-5.Second'].low)

        set_symbols(['TWODAY.TEST-5.Second', 'TWODAY.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1')])
        logger.info("默认合约测试成功！")
        run()


if __name__ == '__main__':
    unittest.main()
