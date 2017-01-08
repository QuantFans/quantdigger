QuantDigger 支持多个策略组合同时做回测，且每个组合回测可使用多个周期合约的数据。多个策略组合对应系统的多个交易上下文，
多个数据组合对应系统的多个数据上下文。系统在实现上只有一个上下文 ``Context`` 实例，它负责交易上下文间的切换，及数据上下文间的切换, 并且以参数 ``ctx`` 暴露给策略函数。策略函数通过上下文获取当前合约的数据，用户在 ``on_init`` 函数中创建的变量，以及进行下单等交易行为。

## 跨周期合约数据引用


每个策略都可能通过 ``set_symbols`` 指定它要使用的周期合约数据。其中列表参数的第一个周期合约为策略的默认周期合约数据。
`上下文系统变量` 如 ``open``，``close``，``high``，``low``，``volume``， ``datetime`` 等， 引用的都是
默认周期合约的数据，如果想获取特定周期合约的数据，比如 'ru.shfe-1.minute'，就得通过如下形式获取：


    ctx['ru.shfe-1.minute'].datetime
    ctx['ru.shfe-1.minute'].open


## 上下文时间和跨周期时间对齐

假设策略使用了两个周期合约：ru.shfe-1.minute和ru.shfe-2.minute，因为合约的周期不一样，所以存在时间对齐的问题。为简化说明，假设
两合约的时间范围都是[1, 10], 且A和B分别表示两个不同时间周期的合约，A的周期为B的1/2，即A的时间步长1，B的时间步长为2。则系统运行时
，数据(A, B)的时间对齐方式为：(1, 2), (2, 2), (3, 2), (4, 4), (5, 4), (6, 6), (7, 6), (8, 8), (9, 8), (10, 10)。上下文时间 ``ctx.ctx_datetime`` 分别是1, 2, 3, 4, 5, 6, 7, 8, 9, 10。
两合约的当前时间可以不一样，这符合实际。比如股指期货的数据是500ms一个tick，而股票的数据是几秒一个tick，必定会出现最新时间不一致。时间对齐(1, 2)是无效的，因为此时的上下文时间为1，而B合约的时间为2，即用到了B合约的未来数据。所以在编写策略的时候要注意无效对齐的过滤。 ``ctx[A].curbar>0 and ctx[B].curbar>0`` 可做为时间对齐有效点的过滤条件。

再考虑一种更复杂的对齐方式，假设A， B的步长分别为2，3。则对齐方式为(2, 3), (4, 3), (6, 6), (8, 6), (8, 9), (10, 9)。上下文时间分别是
2, 4, 6, 8, 9, 10。时间点9是B合约产生的，其它非对齐时间点是A合约产生的，因为A, B的周期无法整除，所以会出现时间点的交替领先。



## Context类接口

   交易环境上下文，提供数据接口和交易接口。
### 属性：

* strategy: 当前策略的名称
* pcontract: 当前周期合约的名称。
* symbol: 当前合约的名称。
* curbar:  默认周期合约当前是在第几根bar。
* datetime: 默认周期合约当前bar时间。
* open:  默认周期合约当前bar的开盘价格。
* close: 默认周期合约当前bar的收盘价格。
* high:  默认周期合约当前bar的最高价格。
* low: 默认周期合约当前bar的最低价格。
* volume:  默认周期合约当前bar的成交量。
* open_orders: 所有未成交订单。

### __方法__：
#### buy(price, quantity, symbol=None)   多头开仓。

    price (float): 价格。
    quantity (int): 数量。
    symbol (str): 形如'ru.shfe'的合约编码，对大小写不敏感。 默认为 ``set_symbols`` 函数的合约参数中的第一个合约。
      
#### sell(price, quantity, symbol=None)  多头平仓。

    price (float): 价格。
    quantity (int): 数量。
    symbol (str): 形如'ru.shfe'的合约编码，对大小写不敏感。 默认为 ``set_symbols`` 函数的合约参数中的第一个合约。

#### short(price, quantity, symbol=None)   空头开仓。

    price (float): 价格。
    quantity (int): 数量。
    symbol (str): 形如'ru.shfe'的合约编码，对大小写不敏感。 默认为 ``set_symbols`` 函数的合约参数中的第一个合约。

#### cover(price, quantity, symbol=None)   空头平仓。

    price (float): 价格。
    quantity (int): 数量。
    symbol (str): 形如'ru.shfe'的合约编码，对大小写不敏感。 默认为 ``set_symbols`` 函数的合约参数中的第一个合约。

#### position(direction=‘long', symbol=None)  合约持仓信息查询。

    direction (str/int):  持仓方向。多头 - 'long' / 1 ；空头 - 'short'  / 2, 默认为多头。
    symbol (str):  形如'ru.shfe'的合约编码，对大小写不敏感。 默认为 ``set_symbols`` 函数的合约参数中的第一个合约。
    返回 (Position):  合约持仓信息。

#### pos(direction=‘long', symbol=None)   合约可平仓位查询。

    direction (str/int): 持仓方向。多头 - 'long' / 1 ；空头 - 'short'  / 2, 默认为多头。
    symbol (str): 形如'ru.shfe'的合约编码，对大小写不敏感。 默认为 ``set_symbols`` 函数的合约参数中的第一个合约。
    return (float): 合约的可平仓位。

#### all_positions()  返回所有持仓列表[Position]。

#### cancel(orders)  撤单。

    orders (Order/list): 订单或订单集。

#### cash()  返回当前策略的可用资金。

#### equity()  返回当前策略的权益。

## _上一节_&nbsp;[更多策略](more_strategy.md)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   _下一节_&nbsp;[撮合机制](match.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_返回_&nbsp;[首页](wiki.md)
