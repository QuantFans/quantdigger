# -*- coding: utf-8 -*-

# @file plot_strategy.py
# @brief 策略运行和图表展示
# @author wondereamer
# @version 0.2
# @date 2015-12-09

import six
#from quantdigger.engine.series import NumberSeries
#from quantdigger.indicators.common import MA
#from quantdigger.util import  pcontract
from quantdigger import *

boll = {
        'upper': [],
        'middler': [],
        'lower': []
        }

class DemoStrategy(Strategy):
    """ 策略A1 """
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma100 = MA(ctx.close, 100, 'ma100', 'y', 2) #, 'ma200', 'b', '1')
        ctx.ma200 = MA(ctx.close, 200, 'ma200', 'b', 2) #, 'ma200', 'b', '1')
        ctx.boll = BOLL(ctx.close, 20)
        ctx.ma2 = NumberSeries()

    #def on_symbol(self, ctx):
        #pass

    def on_bar(self, ctx):
        if ctx.curbar > 1:
            ctx.ma2.update((ctx.close + ctx.close[1])/2)
        if ctx.curbar > 200:
            if ctx.pos() == 0 and ctx.ma100[2] < ctx.ma200[2] and ctx.ma100[1] > ctx.ma200[1]:
                ctx.buy(ctx.close, 1) 
            elif ctx.pos() > 0 and ctx.ma100[2] > ctx.ma200[2] and \
                 ctx.ma100[1] < ctx.ma200[1]:
                ctx.sell(ctx.close, ctx.pos()) 

        boll['upper'].append(ctx.boll['upper'][0])
        boll['middler'].append(ctx.boll['middler'][0])
        boll['lower'].append(ctx.boll['lower'][0])
        return

    def on_exit(self, ctx):
        return


class DemoStrategy2(Strategy):
    """ 策略A2 """
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma50 = MA(ctx.close, 50, 'ma50', 'y', 2) #, 'ma200', 'b', '1')
        ctx.ma100 = MA(ctx.close, 100, 'ma100', 'black', 2) #, 'ma200', 'b', '1')

    def on_symbol(self, ctx):
        pass

    def on_bar(self, ctx):
        if ctx.curbar > 100:
            if ctx.pos() == 0 and ctx.ma50[2] < ctx.ma100[2] and ctx.ma50[1] > ctx.ma100[1]:
                ctx.buy(ctx.close, 1) 
            elif ctx.pos() > 0 and ctx.ma50[2] > ctx.ma100[2] and \
                 ctx.ma50[1] < ctx.ma100[1]:
                ctx.sell(ctx.close, ctx.pos()) 
        return

    def on_exit(self, ctx):
        return

if __name__ == '__main__':
    import timeit
    ConfigUtil.set({
        'source': 'mongodb',
        'dbname': 'quantdigger'
    })
    start = timeit.default_timer()
    set_symbols(['BB.SHFE-1.Minute']) 
    #set_symbols(['BB.SHFE']) 
    #set_symbols(['BB'])
    profile = add_strategy([DemoStrategy('A1'), DemoStrategy2('A2')],
                            { 'capital': 50000.0, 'ratio': [0.5, 0.5] })

    run()
    stop = timeit.default_timer()
    six.print_("运行耗时: %d秒" % ((stop - start )))

    # 绘制k线，交易信号线
    from quantdigger.digger import finance, plotting
    s = 0
    # 绘制策略A1, 策略A2, 组合的资金曲线
    curve0 = finance.create_equity_curve(profile.all_holdings(0))
    curve1 = finance.create_equity_curve(profile.all_holdings(1))
    curve = finance.create_equity_curve(profile.all_holdings())
    plotting.plot_strategy(profile.data(0), profile.technicals(0),
                            profile.deals(0), curve.equity)
    plotting.plot_curves([curve0.equity, curve1.equity, curve.equity],
                        colors=['r', 'g', 'b'],
                        names=[profile.name(0), profile.name(1), 'A0'])
    # 绘制净值曲线
    plotting.plot_curves([curve.networth])
    # 打印统计信息
    six.print_(finance.summary_stats(curve, 252*4*60))