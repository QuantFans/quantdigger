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
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 1) #, 'ma20', 'b', '1')
        ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 1) #, 'ma20', 'b', '1')
        #ctx.boll = BOLL(ctx.close, 20)
        ctx.dt = DateTimeSeries()
        ctx.month_price = NumberSeries()

    #def on_symbol(self, ctx):
        #pass

    def on_bar(self, ctx):
        ctx.dt.update(ctx.datetime)
        #six.print_(ctx.dt[1].isocalendar()[1], ctx.dt[0].isocalendar()[1])
        if ctx.dt[1].month != ctx.dt[0].month:
            ctx.month_price.update(ctx.close)
        if ctx.curbar > 20:
            if ctx.pos() == 0 and ctx.ma10[2] < ctx.ma20[2] and ctx.ma10[1] > ctx.ma20[1]:
                ctx.buy(ctx.close, 1) 
                ctx.plot_text("buy", 1, ctx.curbar, ctx.close, "buy", 'black', 15);
            elif ctx.pos() > 0 and ctx.ma10[2] > ctx.ma20[2] and \
                 ctx.ma10[1] < ctx.ma20[1]:
                ctx.plot_text("sell", 1, ctx.curbar, ctx.close, "sell", 'blue', 15);
                ctx.sell(ctx.close, ctx.pos()) 
        ctx.plot_line("month_price", 1, ctx.curbar, ctx.month_price, 'y--', lw=2)

    #def plot_text(self, name, x, y, text, color='black', size=10, rotation=0):
        #boll['upper'].append(ctx.boll['upper'][0])
        #boll['middler'].append(ctx.boll['middler'][0])
        #boll['lower'].append(ctx.boll['lower'][0])
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
    start = timeit.default_timer()
    #set_symbols(['BB.SHFE-1.Minute']) 
    #set_symbols(['BB.SHFE']) 
    set_config({ 'source': 'csv' })
    set_symbols(['BB.SHFE-1.Day'])
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
    plotting.plot_strategy(profile.data(), profile.technicals(0),
                            profile.deals(0), curve0.equity.values,
                            profile.marks(0))
    #plotting.plot_curves([curve0.equity, curve1.equity, curve.equity],
                        #colors=['r', 'g', 'b'],
                        #names=[profile.name(0), profile.name(1), 'A0'])
    ## 绘制净值曲线
    plotting.plot_curves([curve.networth])
    ## 打印统计信息
    six.print_(finance.summary_stats(curve, 252))
    ## @TODO 直接单击的时候只有数直线
