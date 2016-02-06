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
        pass

    def on_symbol(self, ctx):
        if ctx.curbar > 11 and ctx.close[1] > ctx.close[11]:
            self.candicates.append(ctx.symbol)

    def on_bar(self, ctx):
        if self.candicates:
            #print(ctx.curbar, self.candicates)
            pass
            # 其它操作, 如买卖相关股票

        self.candicates = []
        return

    def on_exit(self, ctx):
        return

if __name__ == '__main__':
    import timeit
    start = timeit.default_timer()
    # 
    set_symbols(['*.SH', '*.SZ'])
    algo = DemoStrategy('A1')
    profile = add_strategy([algo])
    run()
    stop = timeit.default_timer()
    print "运行耗时: %d秒" % ((stop - start ))
