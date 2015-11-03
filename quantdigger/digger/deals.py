# -*- coding: utf8 -*-
from quantdigger.datastruct import TradeSide, Direction
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



class DealPosition(object):
    """ 开仓，平仓对
        
        :ivar open: 开仓价
        :vartype open: float
        :ivar close: 平仓价
        :vartype close: float
    """
    def __init__(self, buy_trans, sell_trans, quantity):
        self.open = buy_trans
        self.close = sell_trans
        self._quantity = quantity;

    def profit(self):
        """ 盈亏额  """
        direction = self.open.direction
        if direction == Direction.LONG:
            return (self.close.price - self.open.price) * self.open.quantity
        else:
            return (self.open.price - self.close.price) * self.open.quantity

    @property
    def quantity(self):
        """ 成交量 """
        return self._quantity

    @property
    def open_datetime(self):
        """ 开仓时间 """
        return self.open.datetime

    @property
    def open_price(self):
        """ 开仓价格 """
        return self.open.price

    @property
    def close_datetime(self):
        """ 平仓时间 """
        return self.close.datetime

    @property
    def close_price(self):
        """ 平仓价格 """
        return self.close.price

    @property
    def direction(self):
        """ 空头还是多头 """
        return self.open.direction


def update_positions(current_positions, deal_positions, trans):
    """ 更新持仓 
        current_positions: 当前持仓
        deal_positions: 开平仓对
    """
    ## @todo 区分多空
    p = current_positions.setdefault(trans.contract, PositionsDetail())
    if trans.side == TradeSide.KAI:
        # 开仓
        p.positions.append(trans)
        p.total += trans.quantity 
    elif trans.side == TradeSide.PING:
        # 平仓
        p.total -= trans.quantity 
        left_vol = trans.quantity
        last_index = -1
        for position in reversed(p.positions):
            if position.quantity < left_vol:
                # 还需从之前的仓位中平。
                left_vol -= position.quantity
                last_index -= 1
                deal_positions.append(DealPosition(position, trans, position.quantity))

            elif position.quantity == left_vol:
                left_vol -= position.quantity
                last_index -= 1
                deal_positions.append(DealPosition(position, trans, position.quantity))
                break 

            else:
                position.quantity -= left_vol
                left_vol = 0
                deal_positions.append(DealPosition(position, trans, left_vol))
                break

        p.positions = p.positions[0 : last_index]
        assert(left_vol == 0)
