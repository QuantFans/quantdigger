# -*- coding: utf-8 -*-

# @file plot_strategy.py
# @brief 策略运行和图表展示
# @author wondereamer
# @version 0.2
# @date 2015-12-09

#from quantdigger.engine.series import NumberSeries
#from quantdigger.indicators.common import MA
#from quantdigger.util import  pcontract
from quantdigger.engine.qd import *

boll = {
        'upper': [],
        'middler': [],
        'lower': []
        }

class DemoStrategy(Strategy):
    """ 策略A1 """
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2) #, 'ma20', 'b', '1')
        ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2) #, 'ma20', 'b', '1')
        ctx.boll = BOLL(ctx.close, 2)
        pass

    def on_bar(self, ctx):
        if ctx.curbar > 20:
            if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
                ctx.buy('long', ctx.close, 1) 
            elif ctx.position() > 0 and ctx.ma10[1] > ctx.ma20[1] and \
                 ctx.ma10 < ctx.ma20:
                ctx.sell('long', ctx.close, 1) 

        boll['upper'].append(ctx.boll['upper'][0])
        boll['middler'].append(ctx.boll['middler'][0])
        boll['lower'].append(ctx.boll['lower'][0])
        pass

    def on_final(self, ctx):
        return

    def on_exit(self, ctx):
        return


class DemoStrategy2(Strategy):
    """ 策略A2 """
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma5 = MA(ctx.close, 5, 'ma5', 'y', 2) #, 'ma20', 'b', '1')
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'black', 2) #, 'ma20', 'b', '1')

    def on_bar(self, ctx):
        if ctx.curbar > 10:
            if ctx.ma5[1] < ctx.ma10[1] and ctx.ma5 > ctx.ma10:
                ctx.buy('long', ctx.close, 1) 
            elif ctx.position() > 0 and ctx.ma5[1] > ctx.ma10[1] and \
                 ctx.ma5 < ctx.ma10:
                ctx.sell('long', ctx.close, 1) 

    def on_final(self, ctx):
        return

    def on_exit(self, ctx):
        return

if __name__ == '__main__':
    set_symbols(['BB.SHFE-1.Minute'], 0)
    profile = add_strategy([DemoStrategy('A1'), DemoStrategy2('A2')], { 'captial': 5000,
                              'ratio': [0.2, 0.8] })
    run()

    # 绘制k线，交易信号线
    from quantdigger.digger import finance, plotting
    plotting.plot_strategy(profile.data(0), profile.indicators(1), profile.deals(1))
    # 绘制策略A1, 策略A2, 组合的资金曲线
    curve0 = finance.create_equity_curve(profile.all_holdings(0))
    curve1 = finance.create_equity_curve(profile.all_holdings(1))
    curve = finance.create_equity_curve(profile.all_holdings())
    plotting.plot_curves([curve0.equity, curve1.equity, curve.equity],
                        colors=['r', 'g', 'b'],
                        names=[profile.name(0), profile.name(1), 'A0'])
    # 绘制净值曲线
    plotting.plot_curves([curve.networth])
    # 打印统计信息
    print finance.summary_stats(curve, 252*4*60)
