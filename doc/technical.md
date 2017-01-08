# 技术指标


QuantDigger中技术指标的使用方法是在策略函数 ``on_init`` 中初始化，然后在其它策略函数中使用它。技术指标有两种运行方式，
逐步执行和向量执行。逐步执行是针对实盘数据的，只对最新的数据运行，由于目前无法实盘，不展开讨论。向量运行用在回测中，特点是一次计算所有的
值，然后逐步引用它，优点是效率高。技术指标分为两类： `单值指标` ，如移动平均线； `多值指标` ，如布林带。所有的技术指标都继承 ``TechnicalBase`` 类。

    注意：无论是逐步还是向量方式运行, 针对的都是指标，策略函数都是逐步运行的，因为很难以向量运行的方式写策略。

## 单指指标定义

一个移动平均线指标为例子。

``` python

    class MA(TechnicalBase):
        """ 移动平均线指标。 """
        @tech_init
        def __init__(self, data, n, name='MA',
                     color='y', lw=1, style="line"):
            super(MA, self).__init__(data, n, name)
            # 必须的函数参数
            self._args = [data, n]

        def _rolling_algo(self, data, n, i):
            """ 逐步运行函数。""" 
            return (talib.SMA(data, n)[i], )

        def _vector_algo(self, data, n):
            """向量化运行, 必须对self.values赋值。""" 
            self.values = talib.SMA(data, n)

        def plot(self, widget):
            """ 绘图，参数可由UI调整。 """
            self.widget = widget
            self.plot_line(self.values, self.color, self.lw, self.style)
```

``@tech_init`` 函数修饰器会把传递给类实例构造函数 ``__init__`` 的参数构建为类的成员变量, 并触发向量计算，从而简化代码。所以以下代码会为类构建成员变量： ``self.data``, ``self.n``, ``self.name``, ``self.color``, ``self.lw``, ``self.style`` 。
参数 ``data`` 是类型为 ``np.ndarray`` 的数据， ``n`` 表计算窗口的长度， ``name`` 表指标的名称。 其它是指标的绘图参数。
``self._args`` 是传递给指标的逐步函数和向量函数的参数, 是必须有的。

```python

    @tech_init
    def __init__(self, data, n, name='MA',
                 color='y', lw=1, style="line"):
        super(MA, self).__init__(data, n, name)
        # 必须的函数参数
        self._args = [data, n]
```

``_rolling_algo`` 是指标的逐步计算函数， ``_vector_algo`` 是指标的向量计算函数。它们都会被指标父类 ``TechnicalBase`` 调用，参数对用于
``self._args`` ，其中逐步函数多了一个 ``i``,  表示当前所在步数，即在数组中的索引，虽然是逐步运行，但是参数 ``data`` 的大小也是预分配好的, 这样可以提示效率。 ``self.values`` 存放向量计算的结果，也是必须有的。


```python

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。""" 
        return (talib.SMA(data, n)[i], )

    def _vector_algo(self, data, n):
        """向量化运行, 必须对self.values赋值。""" 
        self.values = talib.SMA(data, n)
```
## 多值指标定义


布林带指标例子。多值指标和单指指标的定义大同小异，主要的不同是多值指标的计算结果有多个返回值。因此，多值指标的逐步计算
返回一个元组，它的向量计算放回一个字典，对应于不同的返回值。

```python

    class BOLL(TechnicalBase):
        """ 布林带指标。 """
        @tech_init
        def __init__(self, data, n, name='BOLL', colors=('y', 'b', 'g'), lw=1, style="line"):
            super(BOLL, self).__init__(name)
            self._args = [data, n, 2, 2]

        def _rolling_algo(self, data, n, a1, a2, i):
            """ 逐步运行函数。""" 
            upper, middle, lower =  talib.BBANDS(data, n, a1, a2)
            return (upper[i], middle[i], lower[i])

        def _vector_algo(self, data, n, a1, a2):
            """向量化运行""" 
            u, m, l = talib.BBANDS(data, n, a1, a2)
            self.values = {
                    'upper': u,
                    'middler': m,
                    'lower': l
                    }

        def plot(self, widget):
            """ 绘图，参数可由UI调整。 """
            self.widget = widget
            self.plot_line(self.values['upper'], self.colors[0], self.lw, self.style)
            self.plot_line(self.values['middler'], self.colors[1], self.lw, self.style)
            self.plot_line(self.values['lower'], self.colors[2], self.lw, self.style)

```
## 指标的创建和使用


单值指标变量和时序变量类似，都可通过索引取到前面的值。如 ``ctx.ma10[1]`` 表示前面一根bar上 ``ctx.ma10`` 的值。
多值指标返回的是字典， ``key`` 是指标名称， ``value`` 是时序变量。因此字典的值也可回溯引用。

```python

    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma10 = MA(ctx.close, 10)
        ctx.boll = BOLL(ctx.close, 10)

    def on_symbol(self, ctx):
        print ctx.ma10
        print ctx.ma10[1]
        print boll['upper'], boll['middler'], boll['lower']
        print boll['upper'][1], boll['middler'][1], boll['lower'][1]
```

## 技术指标绘制


技术指标的绘制是基本需求。指标父类 ``TechnicalBase`` 继承了绘图类 ``PlotInterface``, ``PlotInterface`` 定义了很多绘图函数，比如 ``plot_line``, 并负责和QuantDigger的UI框架互动。其中 ``plot`` 函数是绘图的入口, ``self.widget = widget`` 是必须的。如果用户不关心移动平均线的绘制，那么无需定义 ``plot`` 函数。
关于界面的详情见 [UI 。

```python

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        self.plot_line(self.values, self.color, self.lw, self.style)
```
指标类的使用和绘制并不是必须与QuantDigger的其它模块强耦合，用户可以根据自己的风格使用和绘制指标，就像如下代码，脱离QuantDigger的UI,
绘制两条移动平均线。详细代码见demo/plot_ma.py

```python

    # 创建画布
    fig, ax = plt.subplots()
    # 加载数据
    price_data = pd.read_csv("./work/IF000.SHFE-10.Minute.csv", 
                            index_col=0, parse_dates=True)
    # 创建平均线
    ma10 = MA(price_data.close, 10, 'MA10', 'y', 2)
    ma20 = MA(price_data.close, 60, 'MA10', 'b', 2)
    # 绘制指标
    ma10.plot(ax)
    ma20.plot(ax)
    plt.show()
```
## 绘图指标


绘图指标和技术指标类似，只不过它不存在逐步和向量计算之分，绘制所需的数据直接在构造函数赋值，并且只能做绘图，无法被
策略函数使用。比如下面的资金曲线绘制, 它能很好的和系统的UI结合, 见demo/plot_strategy.py

```python

    class EquityCurve(PlotInterface):
        """ 资金曲线 """
        @plot_init
        def __init__(self, data, name='EquityCurve', color='black', lw=1, style='line'):
            super(EquityCurve, self).__init__(name, None)
            self.values = data

        def plot(self, widget):
            self.widget = widget
            self.plot_line(self.values, self.color, self.lw, self.style)
```

## _上一节_&nbsp;[时序变量](series.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   _下一节_&nbsp;[绘图指标](paint.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_返回_&nbsp;[首页](wiki.md)
