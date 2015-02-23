
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
* pyqt
* TA-Lib

策略DEMO
=======
~~~~{.python}
class DemoStrategy(TradingStrategy):
    """ 策略实例 """
    def __init__(self, pcontracts, exe):
        super(DemoStrategy, self).__init__(pcontracts, exe)

        self.ma20 = MA(self, self.open, 20,'ma20', 'b', '1')
        self.ma10 = MA(self, self.open, 10,'ma10', 'y', '1')
        #self.ma2 = NumberSeries(self)

    def on_tick(self):
        """ 策略函数，对每根Bar运行一次。""" 
        #self.ma2.update(average(self.open, 10))
        if self.ma10[1] < self.ma20[1] and self.ma10 > self.ma20:
            self.buy('d', self.open, 1) 
        elif self.ma10[1] > self.ma20[1] and self.ma10 < self.ma20:
            self.sell('d', self.open, 1) 
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
