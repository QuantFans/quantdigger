# -*- coding: utf-8 -*-
##
# @file manytomany.py
# @brief 两个组合, 每个组合有两个包含两个策略。
# @author wondereamer
# @version 0.2
# @date 2015-12-09

import six
from quantdigger import *

class DemoStrategy(Strategy):
    """ 策略A1 """
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2)
        ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2)

    def on_bar(self, ctx):
        if ctx.curbar > 20:
            if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
                ctx.buy(ctx.close, 1) 
                six.print_('策略%s, 买入%s'%(ctx.strategy, ctx.symbol))
            elif ctx.position() is not None and ctx.ma10[1] > ctx.ma20[1] and \
                 ctx.ma10 < ctx.ma20:
                ctx.sell(ctx.close, 1) 
                six.print_('策略%s, 卖出%s'%(ctx.strategy, ctx.symbol))

    def on_symbol(self, ctx):
        return

    def on_exit(self, ctx):
        return


class DemoStrategy2(Strategy):
    """ 策略A2 """
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma5 = MA(ctx.close, 5, 'ma5', 'y', 2)
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'black', 2)

    def on_bar(self, ctx):
        if ctx.curbar > 10:
            if ctx.ma5[1] < ctx.ma10[1] and ctx.ma5 > ctx.ma10:
                ctx.buy(ctx.close, 1) 
                six.print_('策略%s, 买入%s'%(ctx.strategy, ctx.symbol))
            elif ctx.position() is not None and ctx.ma5[1] > ctx.ma10[1] and \
                 ctx.ma5 < ctx.ma10:
                ctx.sell(ctx.close, 1) 
                six.print_('策略%s, 卖出%s'%(ctx.strategy, ctx.symbol))

    def on_symbol(self, ctx):
        return

    def on_exit(self, ctx):
        return

if __name__ == '__main__':
    from quantdigger.digger import finance

    set_symbols(['BB.SHFE-1.Minute'])
    comb1 = add_strategy([DemoStrategy('A1'), DemoStrategy2('A2')],
                            { 'capital': 10000000, 'ratio': [0.5, 0.5] })
    comb2 = add_strategy([DemoStrategy('B1'), DemoStrategy2('B2')],
                            { 'capital': 20000000, 'ratio': [0.4, 0.6] })
    run()
    # 打印组合1的统计信息
    curve1 = finance.create_equity_curve(comb1.all_holdings())
    six.print_('组合A', finance.summary_stats(curve1, 252*4*60))
    # 打印组合2的统计信息
    curve2 = finance.create_equity_curve(comb2.all_holdings())
    six.print_('组合B', finance.summary_stats(curve2, 252*4*60))
