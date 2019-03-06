# -*- coding: utf-8 -*-
##
# @file profile.py
# @brief
# @author wondereamer
# @version 0.4
# @date 2016-12-18

from six.moves import range
import copy
import pandas as pd

from quantdigger.datastruct import (
    OneDeal,
    PositionKey,
    TradeSide,
)


class Profile(object):
    """ 组合结果 """
    def __init__(self, marks, blotter, data_ref):
        """
        """
        self._marks = marks
        self._blotter = blotter
        self._data_ref = data_ref

    def name(self):
        return self._blotter.name

    def transactions(self) -> "[Transaction]":
        """ 策略的所有成交明细
        """
        return self._blotter.transactions

    def deals(self):
        """ 策略的每笔交易(一开一平)。

        Returns:
            list. [OneDeal, ..]
        """
        positions = {}
        deals = []
        for trans in self.transactions():
            self._update_positions(positions, deals, trans)
        return deals

    def all_holdings(self):
        """ 策略账号资金的历史。

        Returns:
            list. [{'cash', 'commission', 'equity', 'datetime'}, ..]
        """
        return self._blotter.all_holdings

    @staticmethod
    def all_holdings_sum(profiles):
        """
        Returns:
            list. [{'cash', 'commission', 'equity', 'datetime'}, ..]
        """
        all_holdings = copy.deepcopy(profiles[0].all_holdings())
        for i, hd in enumerate(all_holdings):
            for profile in profiles[1:]:
                try:
                    rhd = profile.all_holdings()[i]
                except IndexError:
                    rhd = rhd[-2]  # 是否强平导致长度不一
                hd['cash'] += rhd['cash']
                hd['commission'] += rhd['commission']
                hd['equity'] += rhd['equity']
        return all_holdings


    def holding(self):
        """ 当前账号情况
        Returns:
            dict. {'cash', 'commission', 'history_profit', 'equity' }
        """
        return self._blotter.holding

    def marks(self):
        return self._marks

    def technicals(self, strpcon=None):
        if not strpcon:
            strpcon = self._data_ref.default_pcontract
        strpcon = strpcon.upper()
        return self._data_ref.get_technicals(strpcon)

    def data(self, strpcon=None):
        """ 周期合约数据, 只有向量运行才有意义。

        Args:
            strpcon (str): 周期合约，如'BB.SHFE-1.Minute'

        Returns:
            pd.DataFrame. 数据
        """
        if not strpcon:
            strpcon = self._data_ref.default_pcontract
        strpcon = strpcon.upper()
        original = self._data_ref.get_data(strpcon).original
        df = pd.DataFrame({
            'open': original.open.data,
            'close': original.close.data,
            'high': original.high.data,
            'low': original.low.data,
            'volume': original.volume.data
        }, index=original.datetime.data)
        return df

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
        if trans.side == TradeSide.OPEN:
            # 开仓
            p.positions.append(trans)
            p.total += trans.quantity

        elif trans.side == TradeSide.CLOSE:
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
