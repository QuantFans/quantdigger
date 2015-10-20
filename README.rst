QuantDigger
============

QuantDigger目前是一个基于python的量化回测框架。作者最初是因为对数据处理和机器学习感兴趣而选择了这个行业，
接触了一些主流的期货交易软件，比如TB, 金字塔。他们的特点是语法比较简单，缺点是编程语言太封闭，有很多表达限制。
所以选择自己开发一个交易系统，做为交易和研究的工具，甚至尝试过商业化。最初选择c++做为实现语言，但是后面
发现开发效率太低，重要的是做为研究工具来说，其易用性和和扩展性都比不上基于python的回测框架。相比其它流行的
回测框架比如 zipline_ , pyalgotrade_ ，QuantDigger的策略语法更简单，类似MC，TB这些商业软件，但并不牺牲灵活性，保留了python这门通用语言的
所有功能。QuantDigger目前还是定位于研究工具，但是设计上还是会从实盘交易的角度考虑，将来也会接入交易接口。虽然有很多细节还有待完善， 
但是核心的设计和功能已经实现了。代码也比较简单，大家有兴趣的可以自己拓展。 如果大家有什么问题和建议，欢迎加入我们的QQ交流群--334555399，或者
联系发起者(yellowblue QQ:33830957) 。 在项目的推进过程中得到很多朋友的帮助, 在这表示感谢！
除了开发人员，还要特别感谢北京的 vodkabuaa_ 和国元证券的王林峰给出的意见， ongbe_ 帮忙修复代码bug， tushare_ 库的作者 Jimmy_ 和深大的邓志浩帮忙推荐
这个库，以及所有朋友的支持。


文档
----
http://www.quantfans.com/doc/quantdigger/


安装
----
    
你可以选择pip安装 (推荐)
   
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
    from quantdigger.kernel.engine.strategy import TradingStrategy
    from quantdigger.util import  pcontract
    import plotting

    class DemoStrategy(TradingStrategy):
        """ 策略实例 """
        def __init__(self, exe):
            super(DemoStrategy, self).__init__(exe)
            # 创建平均线指标和布林带指标。其中MA和BOLL表示指标函数类。
            # 它们返回序列变量。
            # 'ma20'：指标名. 'b'画线颜色. ‘1‘: 线宽。如果无需
            # 绘图，则这些参数不需要给出。
            self.ma20 = MA(self, self.close, 20,'ma20', 'b', '1')
            self.ma10 = MA(self, self.close, 10,'ma10', 'y', '1')
            self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')

        def on_bar(self):
            """ 策略函数，对每根Bar运行一次。""" 
            if self.ma10[1] < self.ma20[1] and self.ma10 > self.ma20:
                self.buy('long', self.open, 1, contract = 'IF000.SHFE') 
            elif self.position() > 0 and self.ma10[1] > self.ma20[1] and self.ma10 < self.ma20:
                self.sell('long', self.open, 1) 

            # 输出pcon1的当前K线开盘价格。
            print(self.open)

            # 夸品种数据引用
            # pcon2的前一根K线开盘价格。
            print(self.open_(1)[1])

    if __name__ == '__main__':
        try:
            # 策略的运行对象周期合约
            pcon1 = pcontract('IF000.SHFE', '10.Minute')
            pcon2 = pcontract('IF000.SHFE', '10.Minute')
            # 创建模拟器，这里假设策略要用到两个不同的数据，比如套利。
            simulator = ExecuteUnit([pcon1, pcon2]);
            # 创建策略。
            algo = DemoStrategy(simulator)
            # 运行模拟器，这里会开始事件循环。
            simulator.run()

            # 显示回测结果
            plotting.plot_result(simulator.data[pcon], algo._indicators,
                                algo.blotter.deal_positions, algo.blotter)
    
        except Exception, e:
            print(e)


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
.. _pyalgotrade: https://github.com/gbeced/pyalgotrade
.. _zipline: https://github.com/quantopian/zipline


版本
~~~~

**TODO**

* 清理旧代码和数据文件
* 重新设计数据模块
* 改善UI, 补充UI文档

**0.2.0 版本 2015-08-18**

* 修复股票回测的破产bug
* 修复回测权益计算bug
* 交易信号对的计算从回测代码中分离
* 把回测金融指标移到digger/finace
* 添加部分数据结构，添加部分数据结构字段
* 添加几个mongodb相关的函数
    
**0.15版本 2015-06-16**

* 夸品种的策略回测功能
* 简单的交互
* 指标，k线绘制
