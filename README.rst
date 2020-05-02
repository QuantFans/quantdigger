QuantDigger 0.6.0
==================
    
QuantDigger是一个基于python的量化回测框架。它借鉴了主流商业软件（比如TB, 金字塔）简洁的策略语法，同时
避免了它们内置编程语言的局限性，使用通用语言python做为策略开发工具。和 zipline_ , pyalgotrade_ 相比，
QuantDigger的策略语法更接近策略开发人员的习惯。目前的功能包括：股票回测，期货回测。 支持选股，套利，择时, 组合策略。自带了一个基于matplotlib编写的简单的策略和k线显示界面，能满足广大量化爱好者 基本的回测需求。设计上也兼顾了实盘交易，未来如果有时间，也会加入交易接口。


**由于个人时间和工作的关系，本项目不再维护。**



文档
-----
wiki文档_


依赖库
-------
* matplotlib 
* numpy
* logbook
* pandas 
* progressbar2
* zmq
* BeautifulSoup4 (tushare需要)
* lxml (tushare需要)
* tushare_ (一个非常强大的股票信息抓取工具)
* python-dateutil(可选)
* IPython
* TA-Lib

* 可以用pip安装依赖库:
    >>> pip install -r requirements/requirements.txt
* 如果出现pypi源超时情况:
    >>> pip install -r requirements/requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

* TA-Lib 通过pip直接安装可能会出错，
    * 到 http://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载相应版本然后通过命令安装，如
        >>> pip install TA_Lib-0.4.10-cp36-cp36m-win_amd64.whl
    * Anaconda用户可以用
        >>> conda install -c quantopian ta-lib

* finance依赖
    * 安装 https://github.com/matplotlib/mpl_finance


策略组合DEMO
-----------

源码
~~~~

.. code:: py


   from quantdigger import (
      Strategy,
      MA,
      DateTimeSeries,
      NumberSeries,
      set_config,
      add_strategies,
      Profile
   )


   class DemoStrategy(Strategy):
      """ 策略A1 """

      def on_init(self, ctx):
         """初始化数据"""
         ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 1)
         ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 1)
         ctx.dt = DateTimeSeries()
         ctx.month_price = NumberSeries()

      def on_bar(self, ctx):
         ctx.dt.update(ctx.datetime)
         if ctx.dt[1].month != ctx.dt[0].month:
               ctx.month_price.update(ctx.close)
         if ctx.curbar > 20:
               if ctx.pos() == 0 and ctx.ma10[2] < ctx.ma20[2] and ctx.ma10[1] > ctx.ma20[1]:
                  ctx.buy(ctx.close, 1)
                  ctx.plot_text("buy", 1, ctx.curbar, ctx.close, "buy", 'black', 15)
               elif ctx.pos() > 0 and ctx.ma10[2] > ctx.ma20[2] and \
                     ctx.ma10[1] < ctx.ma20[1]:
                  ctx.plot_text("sell", 1, ctx.curbar, ctx.close, "sell", 'blue', 15)
                  ctx.sell(ctx.close, ctx.pos())
         ctx.plot_line("month_price", 1, ctx.curbar, ctx.month_price, 'y--', lw=2)
         return

      def on_exit(self, ctx):
         return


   class DemoStrategy2(Strategy):
      """ 策略A2 """

      def on_init(self, ctx):
         """初始化数据"""
         ctx.ma50 = MA(ctx.close, 50, 'ma50', 'y', 2)
         ctx.ma100 = MA(ctx.close, 100, 'ma100', 'black', 2)

      def on_symbol(self, ctx):
         pass

      def on_bar(self, ctx):
         if ctx.curbar > 100:
               if ctx.pos() == 0 and ctx.ma50[2] < ctx.ma100[2] and ctx.ma50[1] > ctx.ma100[1]:
                  ctx.buy(ctx.close, 1)
               elif ctx.pos() > 0 and ctx.ma50[2] > ctx.ma100[2] and \
                     ctx.ma50[1] < ctx.ma100[1]:
                  ctx.sell(ctx.close, ctx.pos())

         return

      def on_exit(self, ctx):
         return


   if __name__ == '__main__':
      import timeit
      start = timeit.default_timer()
      set_config({'source': 'csv'})
      profiles = add_strategies(['BB.SHFE-1.Day'], [
         {
               'strategy': DemoStrategy('A1'),
               'capital': 50000.0 * 0.5,
         },
         {
               'strategy': DemoStrategy2('A2'),
               'capital': 50000.0 * 0.5,
         }
      ])
      stop = timeit.default_timer()
      print("运行耗时: %d秒" % ((stop - start)))

      # 绘制k线，交易信号线
      from quantdigger.digger import finance, plotting
      s = 0
      # 绘制策略A1, 策略A2, 组合的资金曲线
      curve0 = finance.create_equity_curve(profiles[0].all_holdings())
      curve1 = finance.create_equity_curve(profiles[1].all_holdings())
      curve = finance.create_equity_curve(Profile.all_holdings_sum(profiles))
      plotting.plot_strategy(profiles[0].data(), profiles[0].technicals(),
                              profiles[0].deals(), curve0.equity.values,
                              profiles[0].marks())
      # 绘制净值曲线
      plotting.plot_curves([curve.networth])
      # 打印统计信息
      print(finance.summary_stats(curve, 252))


策略结果
~~~~~~~

* k线和信号线

k线显示使用了系统自带的一个联动窗口控件，由蓝色的滑块控制显示区域，可以通过鼠标拖拽改变显示区域。
`上下方向键` 来进行缩放。 

  .. image:: doc/images/plot.png
     :width: 500px

* 2个策略和组合的资金曲线。
  
  .. image:: doc/images/figure_money.png
     :width: 500px

* 组合的历史净值
  
  .. image:: doc/images/figure_networth.png
     :width: 500px

* 统计结果

::
       
    >>> [('Total Return', '-0.99%'), ('Sharpe Ratio', '-5.10'), ('Max Drawdown', '1.72%'), ('Drawdown Duration', '3568')]


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
.. _wiki文档: https://github.com/QuantFans/quantdigger/wiki


版本
~~~~

**0.6.0 版本 2019-05-28**

* 重构回测引擎，使其设计更合理和简洁。

**0.5.1 版本 2017-07-13**

* 在原来0.5.0版的基础上改为支持Python3.6

**0.5.0 版本 2017-01-08**

* 完善文档
* 数据源可配置
* 添加shell, 界面，回测引擎三则间的交互框架

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
    
**0.1.0 版本 2015-06-16**

* 夸品种的策略回测功能
* 简单的交互
* 指标，k线绘制
