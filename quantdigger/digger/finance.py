# -*- coding: utf-8 -*-
##
# @file finance.py
# @brief 常见的金融工具函数
# @author wondereamer
# @version 0.2
# @date 2015-12-09

from six.moves import range
import pandas as pd
import numpy as np


def sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a
    benchmark of zero (i.e. no risk-free rate information).

    Args:
        returns (list, Series) - A pandas Series representing
                                 period percentage returns.

        periods (int.) Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.

    Returns:
        float. The result
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def max_drawdown(networth):
    """ 统计最大回测和相应的回测周期。

    networth: 历史净值
    """
    hwm = [0]  # 历史最大值序列变量
    eq_idx = networth.index
    drawdown = pd.Series(index=eq_idx)
    duration = pd.Series(index=eq_idx)

    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], networth[t])
        hwm.append(cur_hwm)
        drawdown[t] = hwm[t] - networth[t]
        # <=0 新高，计数0
        duration[t] = 0 if drawdown[t] <= 0 else duration[t-1] + 1
    return drawdown.max(), duration.max()


def create_equity_curve(all_holdings):
    """ 创建资金曲线, 历史回报率对象。

    Args:
        all_holdings (list): 账号资金历史。

    Returns:
        pd.DataFrame 数据列 { 'cash', 'commission',
                              'equity', 'returns', 'networth' }
    """
    curve = pd.DataFrame(all_holdings)
    curve.set_index('datetime', inplace=True)
    curve['returns'] = curve['equity'].pct_change()
    curve.iloc[0, 3] = 0  # reset first value as 0 instead nan
    curve['networth'] = (1.0+curve['returns']).cumprod()
    return curve


def summary_stats(curve, periods):
    """
    策略统计。
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    total_return = curve['networth'][-1]
    returns = curve['returns']
    pnl = curve['networth']

    sharpe = sharpe_ratio(returns, periods)
    max_dd, dd_duration = max_drawdown(pnl)

    stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
             ("Sharpe Ratio", "%0.2f" % sharpe),
             ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
             ("Drawdown Duration", "%d" % dd_duration)]
    return stats
