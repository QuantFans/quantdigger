# -*- coding: utf-8 -*-

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
