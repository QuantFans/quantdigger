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
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2)
        ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2)

    def on_symbol(self, ctx):
        if ctx.curbar > 20:
            if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
                self.candicates.append(ctx.symbol)

    def on_bar(self, ctx):
        #if self.candicates:
            #print(ctx.curbar, ctx.curbar, self.candicates)
            # 其它操作, 如买卖相关股票

        self.candicates = []
        return

    def on_exit(self, ctx):
        return



if __name__ == '__main__':
    # 
    set_symbols(['BB.SHFE-1.Minute', 'AA.SHFE-1.Minute'])
    algo = DemoStrategy('A1')
    profile = add_strategy([algo])

    # 绘制k线，交易信号线
    from quantdigger.digger import plotting
    # 绘制策略A1, 策略A2, 组合的资金曲线
    run()
    plotting.plot_strategy(profile.data(0), profile.technicals(0))

    print "done!" 
