# 策略接口实例



以下是一个在两 `周期合约(合约编码.交易所编码-数量.时间单位)`  `AA.SHFE-1.Minute`  ,  `BB.SHFE-1.Minute` 上运行的简单的均线策略例子。

``` python
    from quantdigger import *
    class DemoStrategy(Strategy):
        """ 策略A1 """
    
        def on_init(self, ctx):
            """初始化数据""" 
            ctx.ma10 = MA(ctx.close, 10, 'ma10', 'y', 2)
            ctx.ma20 = MA(ctx.close, 20, 'ma20', 'b', 2)
            ctx.ma2 = NumberSeries()

        def on_symbol(self, ctx):
            return

        def on_bar(self, ctx):
            if ctx.curbar > 1:
                ctx.ma2.update((ctx.close[1]+ctx.close)/2)
            if ctx.curbar > 20:
                if ctx.ma10[2] < ctx.ma20[2] and ctx.ma10[1] > ctx.ma20[1]:
                    ctx.buy(ctx.close, 1) 
                elif ctx.position() > 0 and ctx.ma10[2] > ctx.ma20[2] and ctx.ma10[1] < ctx.ma20[1]:
                    ctx.sell(ctx.close, ctx.position()) 

        def on_exit(self, ctx):
            return

    if __name__ == '__main__':
        set_config({
            'source': 'sqlite',
            'data_path': 'd:\data' 
        })
        set_symbols(['AA.SHFE-1.Minute', 'BB.SHFE-1.Minute'])
        profile = add_strategy([DemoStrategy('A1')])
        run()
```

## 数据源

`set_config` 是配置函数，通过它设置系统参数，这里设置了系统使用的数据源是
参数 `data_path`所设目录下的sqlite数据库。你也可以不用做设置，系统默认数据目录
为当前目录下的data子目录，默认数据源是csv文件。

  
    set_config({
        'source': 'sqlite',
        'data_path': 'd:\data' 
    })

`set_symbols` 指定策略执行要用到的合约, 并且你也可以给它指定时间范围。


   set_symbols(['AA.SHFE-1.Minute', 'BB.SHFE-1.Minute'])

## 策略接口

所有的用户策略都继承于策略基类 `Strategy` ，它包含四个主要策略函数: `on_init`, `on_symbol`, `on_bar`, `on_exit` 。

还是以上面的策略做位例子，它运行在两个品种的数据上, 为简单起见，假设数据的时间范围是[1, 1000], 时间步长为1, 即每个数据合约的k线根数都为1000。

* `on_init` 只会被执行一次，它做的是初始化的工作，给 `上下文` `ctx` 添加属性变量，以便其它策略API引用。

* `on_symbol` 是逐合约逐时间点(逐bar)运行，在每个对齐的时间点上会被执行n次，n为策略使用的数据品种的数量，这里n=2。所以它被执行的总次数为1000*2=2000。 不能在 `on_symbol` 函数中引用跨周期合约的数据，也不能做交易相关的操作，比如下单和持仓查询，它主要用于选股。 

* `on_bar` 是逐时间点运行, 不管策略在多少个合约上执行, 在每个对齐的时间点上只会被执行1次。所以它被执行的总次数为1000。
可以在 `on_bar` 中引用跨周期合约的数据, 做交易。

* `on_exit` 只在策略运行结束前运行一次。

## 策略含义

下面的代码表示10分钟均线上叉20分钟均线的时候，在下一根bar买入。可平仓位大于0时，10分钟均线下叉20分钟均线的时候在下一根bar卖出。

```python
    if ctx.curbar > 20:
        if ctx.ma10[2] < ctx.ma20[2] and ctx.ma10[1] > ctx.ma20[1]:
            ctx.buy(ctx.close, 1) 
        elif ctx.position() > 0 and ctx.ma10[2] > ctx.ma20[2] and ctx.ma10[1] < ctx.ma20[1]:
            ctx.sell(ctx.close, ctx.position()) 
```

`ctx.ma10`, `ctx.ma20` 都是 [[指标变量][] , `ctx.close` 为 [[时序变量]] ，
它们都是上下文 `ctx` 的属性值, 策略API可通过上下文引用这些变量。 

时序变量_ 可看作是一个数组，长度为当前数据上下文的长度，这里为1000。时序变量的索引i引用表示自当前
往前倒数的第i个值， i=0的索引引用表示当前值。 比如， `ctx.close[1]` 表示前面一根bar的收盘价， `ctx.close[0]` 和 `ctx.close` 都表示当前bar的收盘价。 [[指标变量]] 和[[时序变量]]类似。`ctx.curbar` 表示策略API运行到上下文的第几根k线，它在此例中的取值范围是[1, 1000]。


下面的代码做为时序变量使用的演示，直接在策略API里面直接用当前bar的收盘价和前面一根bar的收盘价计算二根bar均值。 `ctx.ma2` 是数字时序变量, 它的长度会自动 随着策略的逐时间（逐bar）运行而变长，如果不调用成员函数 `update` 更新最新值，系统默认会给它赋0值。

```python
    if ctx.curbar > 1:
        ctx.ma2.update((ctx.close[1]+ctx.close)/2)
```

如果你不喜欢时序变量自动追加数值的功能，可以用普通的 `list` 变量，比如 `ctx.xxx = []`


## 上下文

`ctx` 表示数据、策略上下文。本例中策略是运行在两个品种的数据上，所以在 `on_init` 中初始化的属性值有两份，分别对应于两个数据品种的上下文。本例只有一个策略，所以只有一个策略上下文。 系统在运行的时候会自动切换数据和策略上下文，具体细节见章节 [[交易上下文]] 。

## profile

待续。。

## _上一节_&nbsp;__[安装](install.md)__   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   _下一节_&nbsp;[更多策略](more_strategy.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_返回_&nbsp;[首页](wiki.md)
