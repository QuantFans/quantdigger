# QuantDigger文档

## 介绍

QuantDigger是一个基于python的量化回测框架。它借鉴了主流商业软件（比如TB, 金字塔）简洁的策略语法，同时 避免了它们内置编程语言的局限性，使用通用语言python做为策略开发工具。和 [zipline][zipline] , [pyalgotrade][2] 相比， QuantDigger的策略语法更接近策略开发人员的习惯。目前的功能包括：股票回测，期货回测。 支持选股，套利，择时, 组合策略。自带了一个基于matplotlib编写的简单的策略和k线显示界面，能满足广大量化爱好者 基本的回测需求。设计上也兼顾了实盘交易，未来如果有时间，也会加入交易接口。开发人员都是量化爱好者，也欢迎感兴趣的新朋友加入开发, 我们的QQ交流群：334555399。

## 目录

* [安装](install.md)
* [策略接口实例](strategy_demo1.md)
* [数据源配置](datasource.md)
* [更多策略](more_strategy.md)
* [交易上下文](context.md)
* [撮合机制](match.md)
* [时序变量](series.md)
* [技术指标](technical.md)
* [绘图指标](paint.md)
* [系统交互](interaction.md)
* [界面](ui.md)
* [数据结构](datstruct.md)


[zipline]: https://github.com/quantopian/zipline "zipline"
[2]: https://github.com/gbeced/pyalgotrade "pyalgotrade"
