# -*- coding: utf-8 -*-

# @file profile_strategy.py
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
    """ 策略A2 """

    def on_init(self, ctx):
        """初始化数据"""
        ctx.ma5 = MA(ctx.close, 5, 'ma5', 'y', 2) #, 'ma200', 'b', '1')
        ctx.ma30 = MA(ctx.close, 30, 'ma30', 'black', 2) #, 'ma200', 'b', '1')

    def on_symbol(self, ctx):
        pass

    def on_bar(self, ctx):
        if ctx.curbar > 30:
            if ctx.ma5[2] < ctx.ma30[2] and ctx.ma5[1] > ctx.ma30[1]:
                if ctx.pos('long') == 0:
                    ctx.buy(ctx.close, 1)
                if ctx.pos('short') > 0:
                    ctx.cover(ctx.close, ctx.pos('short'))
            elif ctx.ma5[2] > ctx.ma30[2] and  ctx.ma5[1] < ctx.ma30[1]:
                if ctx.pos('short') == 0:
                    ctx.short(ctx.close, 1)
                if ctx.pos('long') > 0:
                    ctx.sell(ctx.close, ctx.pos('long'))

        return

    def on_exit(self, ctx):
        return


if __name__ == '__main__':
    import timeit
    from quantdigger.digger.analyze import AnalyzeFrame
    import matplotlib.pyplot as plt
    start = timeit.default_timer()
    set_config({ 'source': 'csv' })
    profiles = add_strategies(['BB.SHFE-1.Day'], [
        {
            'strategy': DemoStrategy('A1'),
            'capital': 5000000.0
        }
    ])
    stop = timeit.default_timer()
    six.print_("运行耗时: %d秒" % ((stop - start )))
    AnalyzeFrame(profiles[0])
    plt.show()
