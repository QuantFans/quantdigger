
QuantDigger
=======
QuantDigger是一个开源的股票/期货回测框架。

安装
=======
 * 建议安装[Anaconda](http://continuum.io/downloads), 这样可以一次性搞定所有依赖包。
 * 设置PYTHONPATH环境变量。


依赖库
=======
依赖库：
* Python 
* pandas 
* python-dateutil 
* matplotlib 
* numpy
* TA-Lib
* pyqt (可选)
* tushare (可选)

策略DEMO
=======
~~~~{.python}
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.indicators.common import MA, BOLL
from quantdigger.kernel.engine.strategy import TradingStrategy, pcontract, stock
import plotting


class DemoStrategy(TradingStrategy):
    """ 策略类 """
    def __init__(self, pcontracts, exe):
        """ 初始化指标变量 """
        super(DemoStrategy, self).__init__(pcontracts, exe)

        self.ma20 = MA(self, self.close, 20,'ma20', 'b', '1')
        self.ma10 = MA(self, self.close, 10,'ma10', 'y', '1')
        self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')
        #self.ma2 = NumberSeries(self)

    def on_tick(self):
        """ 策略函数，对每根Bar运行一次。""" 
        #self.ma2.update(average(self.open, 10))
        if self.ma10[1] < self.ma20[1] and self.ma10 > self.ma20:
            self.buy('d', self.open, 1) 
        elif self.position() > 0 and self.ma10[1] > self.ma20[1] and self.ma10 < self.ma20:
            self.sell('d', self.open, 1) 

        print self.position(), self.cash()
        print self.datetime, self.b_upper, self.b_middler, self.b_lower


# 运行策略
begin_dt, end_dt = None, None
pcon = pcontract('SHFE', 'IF000', 'Minutes', 10)
#pcon = stock('600848')  利用tushare远程加载股票数据
simulator = ExecuteUnit(begin_dt, end_dt)
algo = DemoStrategy([pcon], simulator)
simulator.run()

# 显示回测结果
plotting.plot_result(simulator.data[pcon],
            algo._indicators,
            algo.blotter.deal_positions,
            algo.blotter)
~~~~
运行结果
=======
* main.py 策略回测结果信号线和资金曲线。
  https://github.com/QuantFans/quantdigger/blob/master/figure_signal.png
  https://github.com/QuantFans/quantdigger/blob/master/figure_money.png
* mplot_demo.py  matplotlib画k线，指标线的demo。
  https://github.com/QuantFans/quantdigger/blob/master/plot.png
* pyquant.py 基于pyqt， 集成了ipython和matplotlib的demo。
  https://github.com/QuantFans/quantdigger/blob/master/pyquant.png
