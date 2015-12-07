# -*- coding: utf-8 -*-
from quantdigger.engine.qd import *
from quantdigger.engine.series import NumberSeries, DateTimeSeries
import datetime
import unittest
import pandas as pd
import os
import talib
import numpy as np
class TestSeries(unittest.TestCase):
        
    def test_case(self):
        close, open, dt, high, low, volume = [], [], [], [], [], []
        open3, dt3 = [], []
        ma3, ma2 = [], []
        svar = []

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                ctx.ma3 = MA(ctx.close, 3)
                ctx.svar = NumberSeries()
                return

            def on_bar(self, ctx):
                open.append(ctx.open-0)
                close.append(ctx.close-0)
                high.append(ctx.high-0)
                low.append(ctx.low-0)
                volume.append(int(ctx.volume-0))
                dt.append(ctx.datetime[0])
                open3.append(ctx.open[3])
                dt3.append(ctx.datetime[3])
                svar.append(ctx.svar[0])

            def on_final(self, ctx):
                return

            def on_exit(self, ctx):
                return

        ## @todo 滚动的时候无法通过测试
        set_pcontracts([pcontract('BB.SHFE', '1.Minute')], 0)
        add_strategy([DemoStrategy('A1')])
        run()
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
        fname = os.path.join(os.getcwd(), 'data', 'BB.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertTrue(source.equals(target), "系统时间序列变量正测试出错")
        fname = os.path.join(os.getcwd(), 'data', 'CC.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertFalse(source.equals(target), "系统时间序列变量反测试出错")
        # 回溯测试
        conopen = [open[0] for i in xrange(0, len(open))]
        condt = [dt[0] for i in xrange(0, len(open))]
        for i in xrange(0, len(open)):
            if i-3 >= 0:
                self.assertTrue(open3[i] == open[i-3], "系统序列变量回溯测试失败！" )
                self.assertTrue(dt3[i] == dt[i-3], "系统序列变量回溯测试失败！" )
            else:
                self.assertTrue(open3[i] == NumberSeries.DEFAULT_VALUE,
                                            "系统序列变量回溯测试失败！")
                self.assertTrue(dt3[i] == DateTimeSeries.DEFAULT_VALUE,
                                                "系统序列时间变量回溯测试失败！")
            self.assertTrue(svar[i] == NumberSeries.DEFAULT_VALUE)
        self.assertTrue(NumberSeries.DEFAULT_VALUE == 0.0)
        self.assertTrue(DateTimeSeries.DEFAULT_VALUE == datetime.datetime(1980,1,1))
        # 保证非常量，从而保证回溯有效。
        self.assertFalse(open == conopen)
        self.assertFalse(dt == condt)


class TestIndicator(unittest.TestCase):
        
    def test_case(self):
        close, ma2 = [], []
        pre_ma2 = []

        class DemoStrategy(Strategy):
            def on_init(self, ctx):
                """初始化数据""" 
                ctx.ma2 = MA(ctx.close, 2)
                ctx.boll = BOLL(ctx.close, 2)

            def on_bar(self, ctx):
                pre_ma2.append(ctx.ma2[3])
                ma2.append(ctx.ma2-0)
                close.append(ctx.close-0)
                print ctx.boll['upper'][1], ctx.boll['middler'][1], ctx.boll['lower'][1]


            def on_final(self, ctx):
                return

            def on_exit(self, ctx):
                return

        ## @todo 滚动的时候无法通过测试
        set_pcontracts([pcontract('BB.SHFE', '1.Minute')], 0)
        add_strategy([DemoStrategy('A1')])
        run()
        source_ma2 = talib.SMA(np.asarray(close), 2)
        for i in xrange(0, len(close)):
            if i >= 1:
                self.assertTrue(ma2[i] == source_ma2[i])
            else:
                self.assertFalse(ma2[i] == ma2[i])
        #print pre_ma2[0:8]
        #print source_ma2[0:8]
        for i in xrange(0, len(close)):
            if i >= 4:
                self.assertTrue(pre_ma2[i] == source_ma2[i-3])
            else:
                # 指标序列变量的默认值为nan
                self.assertFalse(pre_ma2[i] == pre_ma2[i])
        ## @todo 多值函数测试




if __name__ == '__main__':
    unittest.main()
