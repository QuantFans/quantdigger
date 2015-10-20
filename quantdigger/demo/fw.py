# -*- coding: utf-8 -*-
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.util import stock
from quantdigger.digger import deals
import plotting

#import ds163
#_default_datasource = ds163.CachedStock163Source('163cache')
import dstushare
_default_datasource = dstushare.CachedStockTsSource('tscache')

def run(TheStrategy, code, datasource=_default_datasource):
    print 'code: ' + code
    pcon = stock(code)
    dt_start = '20130101'
    #dt_end = '20150819'
    #dt_start = None
    dt_end = None
    simulator = ExecuteUnit([pcon], dt_start, dt_end, datasource=datasource)
    algo = TheStrategy(simulator)
    simulator.run()
    a = {}
    b = []
    try:
        for trans in algo.blotter.transactions:
            deals.update_positions(a, b, trans);
    except Exception, e:
        print e
    plotting.plot_result(simulator.data[pcon], algo._indicators, b, algo.blotter)
