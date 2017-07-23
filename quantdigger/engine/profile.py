# -*- coding: utf-8 -*-
##
# @file profile.py
# @brief 
# @author wondereamer
# @version 0.4
# @date 2016-12-18

import six
from six.moves import range
import copy
from quantdigger.datastruct import (
    OneDeal,
    PositionKey,
    TradeSide,
)

class Profile(object):
    """ 组合结果 """
    def __init__(self, scontexts, dcontexts, strpcon, i):
        """
        
        Args:
            scontexts (list): 策略上下文集合
            dcontexts (list): 数据上下文集合
            strpcon (str): 主合约
            i (int): 当前profile所对应的组合索引
        """
        self._marks = [ctx.marks for ctx in scontexts]
        self._blts = [ctx.blotter for ctx in scontexts]
        self._dcontexts = {}
        self._ith_comb = i   # 对应于第几个组合
        self._main_pcontract = strpcon
        for key, value in six.iteritems(dcontexts):
            self._dcontexts[key] = value

    def name(self, j=None):
        if j is not None:
            return self._blts[j].name
        return self._blts[0].name

    def transactions(self, j=None):
        """ 第j个策略的所有成交明细, 默认返回组合的成交明细。

        Args:
            j (int): 第j个策略

        Returns:
            list. [Transaction, ..]
        """
        if j is not None:
            return self._blts[j].transactions
        trans = []
        for blt in self._blts:
            trans.append(blt.transactions)
        # @TODO 时间排序
        return trans

    def deals(self, j=None):
        """ 第j个策略的每笔交易(一开一平), 默认返回组合的每笔交易。

        Args:
            j (int): 第j个策略

        Returns:
            list. [OneDeal, ..]
        """
        """ 交易信号对 """
        positions = {}
        deals = []
        if j is not None:
            for trans in self.transactions(j):
                self._update_positions(positions, deals, trans)
        else:
            for i in range(0, len(self._blts)):
                deals += self.deals(i)
        return deals

    def all_holdings(self, j=None):
        """ 第j个策略的账号历史, 默认返回组合的账号历史。

        Args:
            j (int): 第j个策略

        Returns:
            list. [{'cash', 'commission', 'equity', 'datetime'}, ..]
        """
        if j is not None:
            return self._blts[j].all_holdings
        if len(self._blts) == 1:
            return self._blts[0].all_holdings
        holdings = copy.deepcopy(self._blts[0].all_holdings)
        for i, hd in enumerate(holdings):
            for blt in self._blts[1:]:
                rhd = blt.all_holdings[i]
                hd['cash'] += rhd['cash']
                hd['commission'] += rhd['commission']
                hd['equity'] += rhd['equity']
        return holdings

    def holding(self, j=None):
        """ 当前账号情况

        Args:
            j (int): 第j个策略

        Returns:
            dict. {'cash', 'commission', 'history_profit', 'equity' }
        """
        if j is not None:
            return self._blts[j].holding
        if len(self._blts) == 1:
            return self._blts[0].holding
        holdings = copy.deepcopy(self._blts[0].holding)
        for blt in self._blts[1:]:
            rhd = blt.holding
            holdings['cash'] += rhd['cash']
            holdings['commission'] += rhd['commission']
            holdings['equity'] += rhd['equity']
            holdings['history_profit'] += rhd['history_profit']
        return holdings

    def marks(self, j=None):
        """ 返回第j个策略的绘图标志集合 """
        if j is not None:
            return self._marks[j]
        return self._marks[0]

    def technicals(self, j=None, strpcon=None):
        # @TODO test case
        # @TODO 没必要针对不同的strpcon做分析
        """ 返回第j个策略的指标, 默认返回组合的所有指标。

        Args:
            j (int): 第j个策略

            strpcon (str): 周期合约

        Returns:
            dict. {指标名:指标}
        """
        pcon = strpcon if strpcon else self._main_pcontract
        if j is not None:
            return {v.name: v for v in self._dcontexts[pcon].
                    technicals[self._ith_comb][j].values()}
        rst = {}
        for j in range(0, len(self._blts)):
            t = {v.name: v for v in self._dcontexts[pcon].
                 technicals[self._ith_comb][j].values()}
            rst.update(t)
        return rst

    def data(self, strpcon=None):
        # @TODO execute_unit._parse_pcontracts()
        """ 周期合约数据, 只有向量运行才有意义。

        Args:
            strpcon (str): 周期合约，如'BB.SHFE-1.Minute'

        Returns:
            pd.DataFrame. 数据
        """
        if not strpcon:
            strpcon = self._main_pcontract
        strpcon = strpcon.upper()
        return self._dcontexts[strpcon].raw_data

    def _update_positions(self, current_positions, deal_positions, trans):
        """ 根据交易明细计算开平仓对。 """
        class PositionsDetail(object):
            """ 当前相同合约持仓集合(可能不同时间段下单)。

            :ivar cost: 持仓成本。
            :ivar total: 持仓总数。
            :ivar positions: 持仓集合。
            :vartype positions: list
            """
            def __init__(self):
                self.total = 0
                self.positions = []
                self.cost = 0
        assert trans.quantity > 0
        poskey = PositionKey(trans.contract, trans.direction)
        p = current_positions.setdefault(poskey, PositionsDetail())
        if trans.side == TradeSide.KAI:
            # 开仓
            p.positions.append(trans)
            p.total += trans.quantity

        elif trans.side == TradeSide.PING:
            # 平仓
            assert(len(p.positions) > 0 and '所平合约没有持仓')
            left_vol = trans.quantity
            last_index = 0
            search_index = 0
            p.total -= trans.quantity
            if trans.contract.is_stock:
                for position in reversed(p.positions):
                    # 开仓日期小于平仓时间
                    if position.datetime.date() < trans.datetime.date():
                        break
                    search_index -= 1
            if search_index != 0:
                positions = p.positions[:search_index]
                left_positions = p.positions[search_index:]
            else:
                positions = p.positions
            for position in reversed(positions):
                if position.quantity < left_vol:
                    # 还需从之前的仓位中平。
                    left_vol -= position.quantity
                    last_index -= 1
                    deal_positions.append(
                        OneDeal(position, trans, position.quantity))
                elif position.quantity == left_vol:
                    left_vol -= position.quantity
                    last_index -= 1
                    deal_positions.append(
                        OneDeal(position, trans, position.quantity))
                    break
                else:
                    position.quantity -= left_vol
                    left_vol = 0
                    deal_positions.append(OneDeal(position, trans, left_vol))
                    break
            if last_index != 0 and search_index != 0:
                p.positions = positions[0:last_index] + left_positions
            elif last_index != 0:
                p.positions = positions[0:last_index]
            # last_index == 0, 表示没找到可平的的开仓对，最后一根强平
            # 可以被catch捕获 AssertError
            assert(left_vol == 0 or last_index == 0)
