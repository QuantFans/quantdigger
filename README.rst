QuantDigger
============
QuantDigger是由一群量化交易爱好者一起开发的开源的股票/期货回测框架
主要用于学习和研究。欢迎大家提供宝贵意见，贡献代码＾＿＾．
或者加入我们的python量化交易群--334555399．

除了开发人员，还要特别感谢 vodkabuaa_ 给出的意见，
ongbe_ 帮忙修复代码bug， tushare库的作者 Jimmy_ ，以及所有朋友的支持．

**主要代码贡献者:**
     deepfish_

     TeaEra_

     wondereamer_

     HonePhy_

安装
----
    
你可以选择pip安装
   
  ::
       
      python install_pip.py  (如果已经安装了pip,略过这一步。)
      pip install QuantDigger
      python install_dependency.py

或者克隆github代码后本地安装
   
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
* logbook
* pyqt (可选)
* tushare_ (可选, 一个非常强大的股票信息抓取工具)

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
**main.py**

* k线和信号线

  .. image:: figure_signal.png
     :width: 500px

* 资金曲线。
  
  .. image:: figure_money.png
     :width: 500px

其它
~~~~~~~~
**mplot_demo.py  matplotlib画k线，指标线的demo。**
  .. image:: plot.png
     :width: 500px

**pyquant.py 基于pyqt， 集成了ipython和matplotlib的demo。**
  .. image:: pyquant.png
     :width: 500px

.. _TeaEra: https://github.com/TeaEra
.. _deepfish: https://github.com/deepfish
.. _wondereamer: https://github.com/wondereamer
.. _HonePhy: https://github.com/HonePhy
.. _tushare: https://github.com/waditu/tushare
.. _Jimmy: https://github.com/jimmysoa
.. _vodkabuaa: https://github.com/vodkabuaa
.. _ongbe: https://github.com/ongbe
