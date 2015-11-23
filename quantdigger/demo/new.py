# -*- coding: utf-8 -*-
from quantdigger.indicators.common import MA
from quantdigger.util import  pcontract
from quantdigger.engine.series import NumberSeries
from quantdigger.engine import qd


class DemoStrategy(object):
    
    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma3 = MA(ctx.close, 3, 'ma3') #, 'ma20', 'b', '1')
        ctx.ma2 = MA(ctx.close, 2, 'ma2') #, 'ma20', 'b', '1')
        ctx.abc = NumberSeries(name = 'abc')
        return

    def on_bar(self, ctx):
        if ctx.curbar > 2:
            a2 = (ctx.close+ctx.close[1])/2
            a3 = (ctx.close+ctx.close[1]+ctx.close[2])/3
            print ctx.ma2, a2
            print ctx.ma3, a3
            #str(ctx.ma2)
            #if a != float(ctx.ma2):
                #print "-", type(a)
                #print "-", type(float(ctx.ma2))
                #assert False 

        #if ctx.curbar == 3:
            #assert False
        #print 'ma3: ', (ctx.close+ctx.close[1]+ctx.close[2])/3, ctx.ma3
        #print ctx.ma3.series[0].data
        #print "********" 
        #print ctx.ma20.data
        #print "*************"
        #print "close:", ctx.close.data
        #print ctx.ma20
        #print ctx.close._index
        #a = str(ctx.open)
        #print ctx.curbar
        #print ctx.ma20, ctx.ma20R
        # 窗口够大的话，指标计算可放这里, 减少数据库的插入操作。
        #print ctx.open
        #if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
            #ctx.buy('long', ctx.open, 1) 
        #elif ctx.position() > 0 and ctx.ma10[1] > ctx.ma20[1] and \
             #ctx.ma10 < ctx.ma20:
            #ctx.sell('long', ctx.open, 1) 
        return

    def on_cycle(self, ctx):
        """docstring for on_cycle""" 
        return

    def on_exit(self, ctx):
        """""" 
        return


if __name__ == '__main__':
    qd.set_pcontracts([pcontract('BB.SHFE', '1.Minute')], '2013-12-12',
            '2013-12-25', 10)
    qd.add_strategy([DemoStrategy()])
    qd.run()
    #qd.add_strategy([DemoStrategy()], [DemoStrategy2()])
