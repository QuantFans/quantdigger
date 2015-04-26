QuantDigger
===========
QuantDigger是一个开源的股票/期货回测框架。

安装
----
    
 * 设置PYTHONPATH环境变量。
 * 将PYTHONPATH下的Scripts目录添加到环境变量PATH中

   - pip安装
   
     ::
       
         python install_pip.py  (如果已经安装了pip,略过这一步。)
         pip install QuantDigger
         python install_dependency.py

   - github安装
   
     ::
       
         git clone https://github.com/QuantFans/quantdigger.git
         python install.py  (会根据情况安装pip, 及依赖包)


依赖库
------
* Python 
* pandas 
* python-dateutil 
* matplotlib 
* numpy
* TA-Lib
* pyqt (可选)
* tushare (可选)

策略DEMO
--------
源码
~~~~
.. code:: py

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


策略结果
~~~~~~~~
main.py 
k线和信号线
.. image:: https://github.com/QuantFans/quantdigger/blob/master/figure_signal.png


资金曲线。
.. image:: https://github.com/QuantFans/quantdigger/blob/master/figure_money.png


* mplot_demo.py  matplotlib画k线，指标线的demo。
  https://github.com/QuantFans/quantdigger/blob/master/plot.png

* pyquant.py 基于pyqt， 集成了ipython和matplotlib的demo。
  https://github.com/QuantFans/quantdigger/blob/master/pyquant.png
