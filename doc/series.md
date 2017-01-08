# 时序变量

主流的量化交易软件如MT4, MultiChart, TradeStation, TB等都带有时序变量，它简化了策略编写的逻辑。时序变量
的长度随着策略的逐Bar运行自行变长。并且可以通过索引回溯前面的值, 如果回溯超过了界限，返回时序变量的默认值。
时序变量的内部实现封装了一个预先分配好的数组实。如果策略函数 ``on_symbol`` 或 ``on_bar`` 运行到某根Bar时，
没有更新时序变量的值，那么时序变量在该Bar的值为前其在前一根Bar的值，即它的最新值拷贝了上一个值。如果从未更新它的值，
那么时序变量在每根Bar上的值都为相应的默认值。以下是一个用时序变量保存3周期均线的例子：

``` python

   def on_init(ctx):
       ctx.ma3 = NumberSeires()

   def on_symbol(ctx):
       if ctx.curbar >= 3 and ctx.curbar <= 5:
           ctx.ma3.update((ctx.close + ctx.close[1] + ctx.close[2]) / 3)
```
在上面的例子中， ``ctx.curbar`` 为1，2的时候, 即策略函数运行在第1根和第2根Bar的时候，时序变量的值没有更新。
所以，在第1根bar的时候，时序变量的值为数字时序变量的默认值0。在第2根bar的时候，时序其值为复制前面一根Bar下该时序变量的值，
这里为0。同理，第5根Bar以后时序变量没有更新，所以该时序变量的值都等于其在第5根Bar下的值。

## 时序变量类型

NumberSeries: 数字时序变量，默认值为0。

DateTimeSeries: 时间时序变量，默认值为 ``datetime(1980,1,1)`` 。


## 时序变量接口

### 属性

* Series.data: 时序变量内部的数组，真正存放数据的地方。用户可以像普通数组一样使用它, 甚至引用未来的数据, 比如:
     ctx.close.data[0: ctx.curbar]

        注意: 由于 ctx.curbar 从1开始索引，Series.data从0开始索引，所以 ctx.close.data[ctx.curbar]实际上就是下一根Bar的收盘价。

### 方法

* Series.update(value) 更新当前Bar下时序变量的值。


## _上一节_&nbsp;[撮合机制](match.md)  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   _下一节_&nbsp;[技术指标](technical.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_返回_&nbsp;[首页](wiki.md)
