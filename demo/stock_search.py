# -*- coding: utf-8 -*-

# @file stock_search.py
# @brief 选股的例子
# @author wondereamer
# @version 0.2
# @date 2015-12-09

from quantdigger import *

class DemoStrategy(Strategy):
    """ 策略A1 """
    def __init__(self, name):
        super(DemoStrategy, self).__init__(name)
        self.candicates = []
        self.to_sell = []
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2)
        ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2)

    def on_symbol(self, ctx):
        if ctx.curbar > 20:
            if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
                self.candicates.append(ctx.symbol)
            elif ctx.ma10[1] < ctx.ma20[1]:
                self.to_sell.append(ctx.symbol)

    def on_bar(self, ctx):
        for symbol in self.to_sell:
            if ctx.pos('long', symbol) > 0:
                ctx.sell(ctx[symbol].close, 1, symbol) 
                print "sell:", symbol

        for symbol in self.candicates:
            if ctx.pos('long', symbol) == 0:
                ctx.buy(ctx[symbol].close, 1, symbol) 
                print "buy:", symbol


        self.candicates = []
        self.to_sell = []
        return

    def on_exit(self, ctx):
        return



if __name__ == '__main__':
    # 
    set_symbols(['BB.SHFE-1.Minute', 'AA.SHFE-1.Minute'])
    algo = DemoStrategy('A1')
    profile = add_strategy([algo])

    # 绘制k线，交易信号线
    from quantdigger.digger import finance, plotting
    # 绘制策略A1, 策略A2, 组合的资金曲线
    run()

    curve = finance.create_equity_curve(profile.all_holdings())
    plotting.plot_strategy(profile.data(0), profile.technicals(0),
                            profile.deals(0), curve.equity.values)
    ## 绘制净值曲线
    plotting.plot_curves([curve.networth])

    print "done!" 
