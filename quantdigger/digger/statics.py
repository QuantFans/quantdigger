# -*- coding: utf8 -*-
import pandas as pd
import numpy as np

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def create_drawdowns(equity_curve):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve 
    # and set up the High Water Mark
    # Then create the drawdown and duration series
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx)
    duration = pd.Series(index = eq_idx)

    # Loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve[t])
        hwm.append(cur_hwm)
        drawdown[t]= hwm[t] - equity_curve[t]
        duration[t]= 0 if drawdown[t] == 0 else duration[t-1] + 1
    return drawdown.max(), duration.max()

    
def create_equity_curve_dataframe(all_holdings):
    """
    创建资金曲线对象。
    """
    curve = pd.DataFrame(all_holdings)
    curve.set_index('datetime', inplace=True)
    curve['returns'] = curve['equity'].pct_change()
    curve['equity_curve'] = (1.0+curve['returns']).cumprod()
    return curve

def output_summary_stats(curve):
    """
    统计夏普率， 回测等信息。
    """
    total_return = curve['equity_curve'][-1]
    returns = curve['returns']
    pnl = curve['equity_curve']

    sharpe_ratio = create_sharpe_ratio(returns)
    max_dd, dd_duration = create_drawdowns(pnl)

    stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
             ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
             ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
             ("Drawdown Duration", "%d" % dd_duration)]
    return stats
