QuantDigger 0.3
===============

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
* Python (2.x, **暂不支持3.x**)
* pandas 
* python-dateutil 
* matplotlib 
* numpy
* TA-Lib
* logbook
* pyqt (可选)
* tushare_ (可选, 一个非常强大的股票信息抓取工具)


策略组合DEMO
------------

源码
~~~~
.. code:: py


    #from quantdigger.engine.series import NumberSeries
    #from quantdigger.indicators.common import MA
    #from quantdigger.util import  pcontract
    from quantdigger.engine.qd import *

    class DemoStrategy(Strategy):
        """ 策略A1 """
    
        def on_init(self, ctx):
            """初始化数据""" 
            ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2)
            ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2)

        def on_symbol(self, ctx):
            """ 选股 """ 
            return

        def on_bar(self, ctx):
            if ctx.curbar > 20:
                if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
                    ctx.buy(ctx.close, 1) 
                elif ctx.position() > 0 and ctx.ma10[1] > ctx.ma20[1] and \
                     ctx.ma10 < ctx.ma20:
                    ctx.sell(ctx.close, 1) 

        def on_exit(self, ctx):
            return

    class DemoStrategy2(Strategy):
        """ 策略A2 """
    
        def on_init(self, ctx):
            """初始化数据""" 
            ctx.ma5 = MA(ctx.close, 5, 'ma5', 'y', 2) 
            ctx.ma10 = MA(ctx.close, 10, 'ma10', 'black', 2)

        def on_symbol(self, ctx):
            """  选股 """ 
            return

        def on_bar(self, ctx):
            if ctx.curbar > 10:
                if ctx.ma5[1] < ctx.ma10[1] and ctx.ma5 > ctx.ma10:
                    ctx.buy(ctx.close, 1) 
                elif ctx.position() > 0 and ctx.ma5[1] > ctx.ma10[1] and \
                     ctx.ma5 < ctx.ma10:
                    ctx.sell(ctx.close, 1) 

        def on_exit(self, ctx):
            return

    if __name__ == '__main__':
        set_symbols(['BB.SHFE-1.Minute'], 0)
        # 创建组合策略
        # 初始资金5000， 两个策略的资金配比为0.2:0.8
        profile = add_strategy([DemoStrategy('A1'), DemoStrategy2('A2')], { 'captial': 5000,
                                  'ratio': [0.2, 0.8] })
        run()

        # 绘制k线，交易信号线
        from quantdigger.digger import finance, plotting
        plotting.plot_strategy(profile.data(0), profile.indicators(1), profile.deals(1))
        # 绘制策略A1, 策略A2, 组合的资金曲线
        curve0 = finance.create_equity_curve(profile.all_holdings(0))
        curve1 = finance.create_equity_curve(profile.all_holdings(1))
        curve = finance.create_equity_curve(profile.all_holdings())
        plotting.plot_curves([curve0.equity, curve1.equity, curve.equity],
                            colors=['r', 'g', 'b'],
                            names=[profile.name(0), profile.name(1), 'A0'])
        # 绘制净值曲线
        plotting.plot_curves([curve.networth])
        # 打印统计信息
        print finance.summary_stats(curve, 252*4*60)


策略结果
~~~~~~~~

* k线和信号线

  .. image:: images/figure_signal.png
     :width: 500px

* 2个策略和组合的资金曲线。
  
  .. image:: images/figure_money.png
     :width: 500px

* 组合的历史净值
  
  .. image:: images/figure_networth.png
     :width: 500px

* 统计结果

::
       
    >>> [('Total Return', '-0.99%'), ('Sharpe Ratio', '-5.10'), ('Max Drawdown', '1.72%'), ('Drawdown Duration', '3568')]

界面控制
~~~~~~~~
k线显示使用了系统自带的一个联动窗口控件，由蓝色的滑块控制显示区域，可以通过鼠标拖拽改变显示区域。
`上下方向键` 来进行缩放。 

其它
~~~~~~~~
**mplot_demo.py  matplotlib画k线，指标线的demo。**
  .. image:: images/plot.png
     :width: 500px

**pyquant.py 基于pyqt， 集成了ipython和matplotlib的demo。**
  .. image:: images/pyquant.png
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
* 改善UI, 补充UI文档

**0.3.0 版本 2015-12-09**

* 重新设计回测引擎, 支持组合回测，选股
* 重构数据模块

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
