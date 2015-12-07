# -*- coding: utf-8 -*-
#from quantdigger.engine.series import NumberSeries
#from quantdigger.indicators.common import MA
#from quantdigger.util import  pcontract
from quantdigger.engine.qd import *

class DemoStrategy(Strategy):
    
    def on_init(self, ctx):
        """初始化数据""" 
        #ctx.ma3 = MA(ctx.close, 3, 'ma3') #, 'ma20', 'b', '1')
        #ctx.ma2 = MA(ctx.close, 2, 'ma2') #, 'ma20', 'b', '1')
        ctx.abc = NumberSeries(name = 'abc')
        ctx.aa = self.name
        ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2) #, 'ma20', 'b', '1')
        ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2) #, 'ma20', 'b', '1')

    def on_bar(self, ctx):
        #print self._name
        #print ctx.close
        #print ctx.curbar, ctx.datetime
        #print ctx.abc.update(1)
        if ctx.curbar > 20:
            pass
            #assert False
            #a2 = (ctx.close+ctx.close[1])/2
            #a3 = (ctx.close+ctx.close[1]+ctx.close[2])/3
            #print ctx.ma2, a2
            #print ctx.ma3, a3
            #print ctx.datetime
            #ctx.ma2[0]
            #ctx.ma3[0]
            #ctx.ma2[0]
            #ctx.ma3[0]

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
        if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
            ctx.buy('long', ctx.close, 1) 
        elif ctx.position() > 0 and ctx.ma10[1] > ctx.ma20[1] and \
             ctx.ma10 < ctx.ma20:
            ctx.sell('long', ctx.close, 1) 

    def on_final(self, ctx):
        #print "final" 
        #print ctx['BB.SHFE-1.Minute'].aa
        return

    def on_exit(self, ctx):
        """""" 
        return


if __name__ == '__main__':
    import timeit
    import plotting

    start = timeit.default_timer()

    set_pcontracts([pcontract('BB.SHFE', '1.Minute')], 0)
    profile = add_strategy([DemoStrategy('A1')])
    #qd.add_strategy([DemoStrategy('B1'), DemoStrategy('B2')])
    run()
    #print profile.transactions(0)
    #print profile.indicators(0)
    #print profile.signals(0)
    ## @todo 回测案例
    # 第n跟卖，第m跟买，很容易计算结果。
    a = [s.profit() for s in profile.signals(0)]
    print sum(a)
    print profile.holdings(0)
    pos = profile.positions(0)
    for key, value in pos.iteritems():
        print value

    stop = timeit.default_timer()
    print (stop - start )

    plotting.plot_result(profile.data(),
                                profile.indicators(0),
                                profile.signals(0),
                                profile.all_holdings(0))
