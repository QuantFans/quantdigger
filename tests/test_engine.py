# -*- coding: utf-8 -*-
##
# @file test_engine_vector.py
# @brief 测试策略向量化运行中的序列变量，指标计算，跨周期时间对齐，策略和数据的组合遍历。
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
from quantdigger import *

logger = Logger('test')

class TestSeries(unittest.TestCase):
        
    def test_case(self):
        logger.info('***** 序列变量测试开始 *****')
        close, open, dt, high, low, volume = [], [], [], [], [], []
        open3, dt3 = [], []
        ma3, ma2 = [], []
        svar = []
        transform_test = []
        uvars = {
                'dlist': [],
                'numseries': [],
                'numseries3': [],
                'dtseries': [],
                }

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                ctx.ma3 = MA(ctx.close, 3)
                ctx.svar = NumberSeries()
                ctx.numseries = NumberSeries()
                ctx.dtseries = DateTimeSeries()
                ctx.dlist = []
                return

            def on_symbol(self, ctx):
                ## @TODO + - * /
                transform_test.append(ctx.open-0 == ctx.open[0])
                transform_test.append(ctx.close-0 == ctx.close[0])
                transform_test.append(ctx.high-0 == ctx.high[0])
                transform_test.append(ctx.low-0 == ctx.low[0])
                transform_test.append(ctx.volume-0 == ctx.volume[0])
                ctx.dlist.append(ctx.curbar)
                if ctx.curbar >= 100 and ctx.curbar < 300:
                    ctx.numseries.update(100) 
                    ctx.dtseries.update(datetime.datetime(1000,1,1))
                elif ctx.curbar >= 300:
                    ctx.dtseries.update(datetime.datetime(3000,1,1))
                    ctx.numseries.update(300) 

                open.append(ctx.open[0])
                close.append(ctx.close[0])
                high.append(ctx.high[0])
                low.append(ctx.low[0])
                volume.append(int(ctx.volume[0]))
                dt.append(ctx.datetime[0])
                open3.append(ctx.open[3])
                dt3.append(ctx.datetime[3])
                svar.append(ctx.svar[0])

                uvars['numseries3'].append(ctx.numseries[3])
                uvars['numseries'].append(ctx.numseries[0])
                uvars['dtseries'].append(ctx.dtseries[0])
                uvars['dlist'] = ctx.dlist

        set_symbols(['BB.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1')])
        run()

        # 默认值
        self.assertTrue(NumberSeries.DEFAULT_VALUE == 0.0, "默认值测试成功")
        self.assertTrue(DateTimeSeries.DEFAULT_VALUE == datetime.datetime(1980,1,1))
        logger.info('-- 默认值测试成功 --')

        # 类型转化测试
        self.assertTrue(all(transform_test), "类型转化错误!")
        logger.info('-- 类型转化测试成功 --')

        # 值测试
        target = pd.DataFrame({
            'open': open,
            'close': close,
            'high': high,
            'low': low,
            'volume': volume,
            })
        target = target.ix[:, ['open', 'close', 'high', 'low', 'volume']]
        target.index = dt
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'BB.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        #print 'target', target['open'][0:10]
        #print 'source', source['open'][0:10]
        self.assertTrue(source.equals(target), "系统时间序列变量正测试出错")
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'CC.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertFalse(source.equals(target), "系统时间序列变量反测试出错")
        logger.info('-- 系统序列变量值的正确性测试成功 --')

        #
        for i in xrange(0, len(uvars['dlist'])):
            self.assertTrue(i+1 == uvars['dlist'][i])
        self.assertTrue(len(uvars['numseries'])==len(open) and len(open)>0, '系列变量长度不一致')
        logger.info('-- 用户普通变量测试成功 --')
        logger.info('-- curbar测试成功 --')

        # 自动追加测试
        numseries = uvars['numseries']
        dtseries = uvars['dtseries']
        dt1980 = datetime.datetime(1980,1,1)
        dt1000 = datetime.datetime(1000,1,1)
        dt3000 = datetime.datetime(3000,1,1)
        for i in xrange(0, len(numseries)):
            if i < 99:
                self.assertTrue(numseries[i] == 0.0, '用户数字序列变量测试失败!') 
                self.assertTrue(dtseries[i] == dt1980, '用户时间序列变量测试失败!') 
            elif i >= 99 and i < 299:
                self.assertTrue(numseries[i] == 100, '用户数字序列变量测试失败!') 
                self.assertTrue(dtseries[i] == dt1000, '用户时间序列变量测试失败!') 
            elif i >= 299:
                self.assertTrue(numseries[i] == 300, '用户数字序列变量测试失败!') 
                self.assertTrue(dtseries[i] == dt3000, '用户时间序列变量测试失败!') 
        logger.info('-- 用户序列变量自动追加测试成功 --')

        # 回溯测试
        for i in xrange(0, len(open)):
            if i-3 >= 0:
                self.assertTrue(open3[i] == open[i-3], "系统序列变量回溯测试失败！" )
                self.assertTrue(dt3[i] == dt[i-3], "系统序列变量回溯测试失败！" )
                self.assertTrue(uvars['numseries3'][i] == numseries[i-3], "用户序列变量回溯测试失败！" )
            else:
                self.assertTrue(open3[i] == NumberSeries.DEFAULT_VALUE,
                                            "系统序列变量回溯测试失败！")
                self.assertTrue(uvars['numseries3'][i] == NumberSeries.DEFAULT_VALUE,
                                            "用户序列变量回溯测试失败！")
                self.assertTrue(dt3[i] == DateTimeSeries.DEFAULT_VALUE,
                                                "系统序列时间变量回溯测试失败！")
            self.assertTrue(svar[i] == NumberSeries.DEFAULT_VALUE)
        logger.info('-- 序列变量回溯测试成功 --')
        logger.info('***** 序列变量测试结束 *****\n')

class TestIndicator(unittest.TestCase):
        
    def test_case(self):
        logger.info('***** 指标测试开始 *****')
        close, open, ma2 = [], [], []
        pre_ma2 = []
        true_test = []
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
                ctx.ma2 = MA(ctx.close, 2)
                ctx.boll = BOLL(ctx.close, 2)

            def on_symbol(self, ctx):
                if ctx.curbar>=2:
                    ## @todo + - * /
                    true_test.append(ctx.ma2-0 == ctx.ma2[0])
                    
                pre_ma2.append(ctx.ma2[3])
                ma2.append(ctx.ma2[0])
                #a = (ctx.close[1] + ctx.close[0])/2
                #print ctx.ma2[0], a
                close.append(ctx.close[0])
                open.append(ctx.open[0])
                boll['upper'].append(float(ctx.boll['upper']))
                boll['middler'].append(ctx.boll['middler'][0])
                boll['lower'].append(ctx.boll['lower'][0])
                boll3['upper'].append(ctx.boll['upper'][3])
                boll3['middler'].append(ctx.boll['middler'][3])
                boll3['lower'].append(ctx.boll['lower'][3])


            def on_bar(self, ctx):
                return

            def on_exit(self, ctx):
                return

        set_symbols(['BB.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1')])
        run()
        self.assertTrue(all(true_test), "指标转化错误!")
        logger.info('-- 指标转化测试成功 --')

        # 分别测试单值和多值指标函数。
        source_ma2 = talib.SMA(np.asarray(close), 2)
        true_test, false_test = [], []
        for i in xrange(0, len(close)):
            if i >=  1:
                true_test.append(ma2[i] == source_ma2[i])
            else:
                false_test.append(ma2[i] == ma2[i])

        self.assertFalse(any(false_test), "单值指标正例测试失败!")
        self.assertTrue(all(true_test), "单值指标正例测试失败!")
        source_ma2 = talib.SMA(np.asarray(open), 2)
        true_test, false_test = [], []
        for i in xrange(0, len(open)):
            if i >=  1:
                true_test.append(ma2[i] == source_ma2[i])
            else:
                false_test.append(ma2[i] == ma2[i])
        self.assertFalse(any(false_test), "单值指标反例测试失败!")
        self.assertFalse(all(true_test), "单值指标反例测试失败!")
        logger.info('-- 单值指标测试成功 --')

        true_test, false_test = [], []
        source_ma2 = talib.SMA(np.asarray(close), 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(pre_ma2[i] == source_ma2[i-3])
            else:
                # 指标序列变量的默认值为nan
                false_test.append(pre_ma2[i] == pre_ma2[i])
        self.assertTrue(all(true_test), "单值指标回溯正例测试失败")
        self.assertFalse(any(false_test), "单值指标回溯正例测试失败")
        true_test, false_test = [], []
        source_ma2 = talib.SMA(np.asarray(open), 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(pre_ma2[i] == source_ma2[i-3])
            else:
                # 指标序列变量的默认值为nan
                false_test.append(pre_ma2[i] == pre_ma2[i])
        self.assertFalse(all(true_test), "单值指标回溯反例测试失败")
        self.assertFalse(any(false_test), "单值指标回溯反例测试失败")
        logger.info('-- 单值指标回溯测试成功 --')

        #
        u, m, l = talib.BBANDS(np.asarray(close), 2, 2, 2)
        true_test, false_test = [], []
        for i in xrange(0, len(close)):
            if i >=  1:
                true_test.append(boll['upper'][i] == u[i])
                true_test.append(boll['middler'][i] == m[i])
                true_test.append(boll['lower'][i] == l[i])
            else:
                false_test.append(boll['upper'][i] == boll['upper'][i])
                false_test.append(boll['middler'][i] == boll['middler'][i])
                false_test.append(boll['lower'][i] == boll['lower'][i])
        self.assertFalse(any(false_test), "多值指标正例测试失败!")
        self.assertTrue(all(true_test), "多值指标正例测试失败!")
        u, m, l = talib.BBANDS(np.asarray(open), 2, 2, 2)
        true_test, false_test = [], []
        for i in xrange(0, len(close)):
            if i >=  1:
                true_test.append(boll['upper'][i] == u[i])
                true_test.append(boll['middler'][i] == m[i])
                true_test.append(boll['lower'][i] == l[i])
            else:
                false_test.append(boll['upper'][i] == boll['upper'][i])
                false_test.append(boll['middler'][i] == boll['middler'][i])
                false_test.append(boll['lower'][i] == boll['lower'][i])
        self.assertFalse(any(false_test), "多值指标反例测试失败!")
        self.assertFalse(all(true_test), "多值指标反例测试失败!")
        logger.info('-- 多值指标测试成功 --')


        true_test, false_test = [], []
        u, m, l = talib.BBANDS(np.asarray(close), 2, 2, 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(boll3['upper'][i] ==  u[i-3])
            else:
                false_test.append(boll3['upper'][i] ==  boll3['upper'][i])
        self.assertTrue(all(true_test), "多值指标回溯正例测试失败")
        self.assertFalse(any(false_test), "多值指标回溯正例测试失败")
        true_test, false_test = [], []
        u, m, l = talib.BBANDS(np.asarray(open), 2, 2, 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(boll3['upper'][i] == u[i-3])
            else:
                false_test.append(boll3['upper'][i] == boll3['upper'][i])
        self.assertFalse(all(true_test), "多值指标回溯反例测试失败")
        self.assertFalse(any(false_test), "多值指标回溯反例测试失败")
        logger.info('-- 多值指标回溯测试成功 --')
        logger.info('***** 指标测试结束 *****\n')


class TestMultipleCombination(unittest.TestCase):
    """ 多组合策略, 测试数据、策略遍历
    """
        
    def test_case(self):
        logger.info('***** 多组合策略测试开始 *****')
        on_exit = {
                'strategy': [],
                }

        on_bar = {
                'strategy': [],
                }
        on_symbol = {
                'combination': set(),
                'count': 0
                }

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                return

            def on_symbol(self, ctx):
                #print ctx.strategy, ctx.pcontract
                on_symbol['combination'].add((str(ctx.pcontract), ctx.strategy))
                on_symbol['count'] += 1
                pass

            def on_bar(self, ctx):
                on_bar['strategy'].append(ctx.strategy)

            def on_exit(self, ctx):
                on_exit['strategy'].append(ctx.strategy)
                return

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
        self.assertTrue(on_symbol['combination'] == sample)
        sample.pop()
        self.assertFalse(on_symbol['combination'] == sample)
        self.assertTrue(on_symbol['count'] == alen*4 + blen*4)
        self.assertFalse(on_symbol['count'] == alen*3 + blen*4)
        self.assertTrue(['A1', 'A2', 'B1', 'B2']*max(blen, alen) == on_bar['strategy'],
                        'on_bar测试失败！')
        self.assertFalse(['C1', 'A2', 'B1', 'B2']*max(blen, alen) == on_bar['strategy'],
                        'on_bar测试失败！')
        self.assertTrue(['A1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        self.assertFalse(['C1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        logger.info('-- 多组合策略测试成功 --')


class TestDiffPeriod(unittest.TestCase):
    """ 跨周期多组合策略测试 
        主要测试时间对齐和数据、策略遍历
    """
        
    def test_case(self):
        logger.info('***** 跨周期多组合策略测试开始 *****')
        on_exit = {
                'strategy': [],
                }

        on_bar = {
                'strategy': [],
                'diffPeriod': [],
                }
        on_symbol = {
                'diffPeriod': [],
                'count': 0
                }

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                return

            def on_symbol(self, ctx):
                on_symbol['count'] += 1
                on_symbol['diffPeriod'].append("%s %s %s %s"%(ctx.pcontract,
                    ctx.strategy, ctx.datetime, ctx.curbar))
                pass

            def on_bar(self, ctx):
                on_bar['strategy'].append(ctx.strategy)
                t = ctx['oneday.TEST-1.Minute']
                on_bar['diffPeriod'].append("%s %s %s"%(t.pcontract, t.datetime, t.curbar))
                t = ctx['TWODAY.TEST-5.Second']
                on_bar['diffPeriod'].append("%s %s %s"%(t.pcontract, t.datetime, t.curbar))

            def on_exit(self, ctx):
                on_exit['strategy'].append(ctx.strategy)
                return

        set_symbols(['TWODAY.TEST-5.Second', 'oneday.TEST-1.Minute'])
        # 每个策略的没个时间点会允许一次on_bar。
        add_strategy([DemoStrategy('A1'), DemoStrategy('A2')])
        add_strategy([DemoStrategy('B1'), DemoStrategy('B2')])
        run()

        # on_symbol
        fname = os.path.join(os.getcwd(), 'data', '1MINUTE', 'TEST', 'ONEDAY.csv')
        blen = len(pd.read_csv(fname))
        fname = os.path.join(os.getcwd(), 'data', '5SECOND', 'TEST', 'TWODAY.csv')
        alen = len(pd.read_csv(fname))
        self.assertTrue(on_symbol['count'] == alen*4 + blen*4)
        self.assertFalse(on_symbol['count'] == alen*3 + blen*4)
        fname = os.path.join(os.getcwd(), 'data', 'diffPeriodOnSymbol.txt')
        with open(fname) as f:
            source =  f.readlines()
            assert(len(source)>0 and source[0] != "")
            i = 0
            for t in on_symbol['diffPeriod']:
                if source[i].startswith('*'):
                    i+=1
                self.assertTrue(t == source[i].rstrip('\n'), "跨周期合约on_symbol失败")
                i+=1

        # on_bar
        fname = os.path.join(os.getcwd(), 'data', 'diffPeriodOnBar.txt')
        with open(fname) as f:
            source =  f.readlines()
            assert(len(source)>0 and source[0] != "")
            i = 0
            for t in on_bar['diffPeriod']:
                if source[i].startswith('*'):
                    i+=1
                self.assertTrue(t == source[i].rstrip('\n'), "跨周期合约引用失败")
                i+=1

        self.assertTrue(['A1', 'A2', 'B1', 'B2'] * 6498 == on_bar['strategy'],
                        'on_bar测试失败！')
        self.assertFalse(['C1', 'A2', 'B1', 'B2'] * 6498 == on_bar['strategy'],
                        'on_bar测试失败！')

        # on_exit
        self.assertTrue(['A1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        self.assertFalse(['C1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        logger.info('-- 跨周期多组合策略测试成功 --')

        logger.info('***** 跨周期多组合策略测试结束 *****\n')


class TestPContractsWithSameContract(unittest.TestCase):
        
    def test_case(self):
        logger.info('***** 序列变量测试开始 *****')

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                return

            def on_bar(self, ctx):
                # 相同合约不同周期的数据，当前价总是等于最小周期的数据。
                assert(ctx.open == ctx['TWODAY.TEST-5.Second'].open)
                assert(ctx.close == ctx['TWODAY.TEST-5.Second'].close)
                assert(ctx.high == ctx['TWODAY.TEST-5.Second'].high)
                assert(ctx.low == ctx['TWODAY.TEST-5.Second'].low)

        set_symbols(['TWODAY.TEST-5.Second', 'TWODAY.TEST-1.Minute'])
        add_strategy([DemoStrategy('A1')])
        run()


def test_engine():
    unittest.main()
