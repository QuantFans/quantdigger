# -*- coding: utf8 -*-
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.indicators.common import MA
from quantdigger.kernel.engine.strategy import TradingStrategy, pcontract
#from quantdigger.kernel.engine.series import NumberSeries

def average(series, n):
    """ 一个可选的平均线函数 """ 
    ## @todo plot element
    sum_ = 0
    for i in range(0, n):
        sum_ += series[i]
    return sum_ / n


class DemoStrategy(TradingStrategy):
    """ 策略实例 """
    def __init__(self, pcontracts, exe):
        super(DemoStrategy, self).__init__(pcontracts, exe)

        self.ma20 = MA(self, self.open, 20,'ma20', 'b', '1')
        self.ma10 = MA(self, self.open, 10,'ma10', 'y', '1')
        #self.ma2 = NumberSeries(self)

    def on_tick(self):
        """ 策略函数，对每根Bar运行一次。""" 
        #self.ma2.update(average(self.open, 10))
        if self.ma10[1] < self.ma20[1] and self.ma10 > self.ma20:
            self.buy('d', self.open, 1) 
        elif self.ma10[1] > self.ma20[1] and self.ma10 < self.ma20:
            self.sell('d', self.open, 1) 


def plot_result(price_data, indicators, signals, blotter):
    """ 
        显示回测结果。
    """

    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from quantdigger.plugin.mplotwidgets import techmplot
    from quantdigger.plugin.mplotwidgets import widgets
    from quantdigger.kernel.indicators.common import *

    blotter.create_equity_curve_dataframe()
    print blotter.output_summary_stats()

    fig = plt.figure()
    frame = techmplot.TechMPlot(fig,
                                price_data,
                                50          # 窗口显示k线数量。
                                )

    # 添加k线
    kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
    frame.add_widget(0, kwindow, True)
    # 交易信号。
    signal = TradingSignalPos(None, price_data, signals, lw=2)
    frame.add_indicator(0, signal)

    # 添加指标
    k_axes, = frame
    for indic in indicators:
        indic.plot(k_axes)
    frame.draw_window()

    fig2 = plt.figure()
    ax = fig2.add_axes((0.1, 0.1, 0.9, 0.9))
    ax.plot(blotter.equity_curve.total)
    plt.show()


if __name__ == '__main__':
    begin_dt, end_dt = None, None
    pcon = pcontract('SHFE', 'IF000', 'Minutes', 10)
    simulator = ExecuteUnit(begin_dt, end_dt)
    algo = DemoStrategy([pcon], simulator)
    simulator.run()

    # 显示回测结果
    plot_result(simulator.data[pcon],
                algo._indicators,
                algo.blotter.deal_positions,
                algo.blotter)
