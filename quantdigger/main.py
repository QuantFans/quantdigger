# -*- coding: utf8 -*-
from quantdigger.kernel.datastruct import PContract, Contract, Period
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.engine.strategy import DemoStrategy

def pcontract(exchange, contract, time_unit, unit_count):
    """ 构建周期合约结构的便捷方式。
    
    Args:
        exchange (str): 交易所
        contract (str): 合约
        time_unit (str): 时间单位
        unit_count (int): 时间数目
    
    Returns:
        int. The result
    Raises:
    """
    """docstring for pco""" 
    return PContract(Contract(exchange, contract),
                     Period(time_unit, unit_count))

def plot_result(price_data, indicators, signals, blotter):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from quantdigger.plugin.mplotwidgets import techmplot
    from quantdigger.plugin.mplotwidgets import widgets
    from quantdigger.kernel.indicators.common import *

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
    algo = DemoStrategy([pcon])
    simulator = ExecuteUnit(begin_dt, end_dt)
    simulator.add_strategy(algo)
    simulator.run()

    blotter = algo.blotter
    blotter.create_equity_curve_dataframe()
    print blotter.output_summary_stats()

    plot_result(simulator.data[pcon], algo._indicators,
            algo.blotter.deal_positions, blotter)
