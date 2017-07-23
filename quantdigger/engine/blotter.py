# -*- coding: utf-8 -*-
import six
import copy
from abc import ABCMeta, abstractmethod

from quantdigger.util import elogger as logger
from quantdigger.errors import TradingError
from quantdigger.engine.api import SimulateTraderAPI
from quantdigger.event import Event
from quantdigger.datastruct import (
    Direction,
    Order,
    Position,
    PositionKey,
    PriceType,
    TradeSide,
    Transaction,
)




class Blotter(object):
    """
    订单管理。
    """
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def update_signal(self, event):
        """
        处理策略函数产生的下单事件。
        """
        raise NotImplementedError("Should implement update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        处理委托单成交事件。
        """
        raise NotImplementedError("Should implement update_fill()")


class SimpleBlotter(Blotter):
    """
    简单的订单管理系统，直接给 :class:`quantdigger.engine.exchange.Exchange`
    对象发订单，没有风控。
    """
    def __init__(self, name, events_pool, settings={}):
        super(SimpleBlotter, self).__init__(name)
        self.open_orders = set()
        self.positions = {}  # Contract: Position
        self.holding = {}  # 当前的资金 dict
        self.api = SimulateTraderAPI(self, events_pool)  # 模拟交易接口
        self._all_orders = []
        self._pre_settlement = 0     # 昨日结算价
        self._datetime = None  # 当前时间
        self._all_holdings = []   # 所有时间点上的资金 list of dict
        self._all_transactions = []
        self._capital = settings['capital']

    @property
    def all_holdings(self):
        """ 账号历史情况，最后一根k线处平所有仓位。"""
        if self.positions:
            self._force_close()
        return self._all_holdings

    @property
    def transactions(self):
        """ 成交明细，最后一根k线处平所有仓位。"""
        if self.positions:
            self._force_close()
        return self._all_transactions

    def update_data(self, ticks, bars):
        """ 当前价格数据更新。 """
        # self._ticks = ticks
        self._bars = bars

    def update_datetime(self, dt):
        """ 在新的价格数据来的时候触发。 """
        if self._datetime is None:
            self._datetime = dt
            self._start_date = dt
            self._init_state()
        elif self._datetime.date() != dt.date():
            for order in self.open_orders:
                if order.side == TradeSide.PING:
                    pos = self.positions[PositionKey(
                        order.contract, order.direction)]
                    pos.closable += order.quantity
            self.open_orders.clear()
            for key, pos in six.iteritems(self.positions):
                pos.closable += pos.today
                pos.today = 0
        self._datetime = dt

    def update_status(self, dt, at_baropen):
        """ 更新历史持仓，当前权益。"""
        # @TODO open_orders 和 postion_margin分开，valid_order调用前再统计？
        # 更新资金历史。
        dh = {}
        dh['datetime'] = dt
        dh['commission'] = self.holding['commission']
        pos_profit = 0.0
        margin = 0.0
        order_margin = 0.0
        # 计算当前持仓历史盈亏。
        # 以close价格替代市场价格。
        for key, pos in six.iteritems(self.positions):
            bar = self._bars[key.contract]
            new_price = bar.open if at_baropen else bar.close
            pos_profit += pos.profit(new_price)
            # @TODO 用昨日结算价计算保证金
            margin += pos.position_margin(new_price)
        # 计算未成交开仓报单的保证金占用
        for order in self.open_orders:
            assert(order.price_type == PriceType.LMT)
            bar = self._bars[order.contract]
            new_price = bar.open if at_baropen else bar.close
            if order.side == TradeSide.KAI:
                order_margin += order.order_margin(new_price)
        # 当前权益 = 初始资金 + 累积平仓盈亏 + 当前持仓盈亏 - 历史佣金总额
        dh['equity'] = self._capital + self.holding['history_profit'] + \
            pos_profit - self.holding['commission']
        # @TODO
        # 对于股票，Bar的开盘和收盘点资金验证是一致的。
        # 如果期货不一致，成交撮合时候也无法确定确切的时间点，
        # ，就无法确定精确的可用资金，可能因此导致cash<0, 就得加
        # 强平功能，使交易继续下去。
        dh['cash'] = dh['equity'] - margin - order_margin
        if dh['cash'] < 0:
            for key in six.iterkeys(self.positions):
                if not key.contract.is_stock:
                    # @NOTE  只要有一个是期货，在资金不足的时候就得追加保证金
                    raise Exception('需要追加保证金!')
        self.holding['cash'] = dh['cash']
        self.holding['equity'] = dh['equity']
        self.holding['position_profit'] = pos_profit
        if at_baropen:
            self._all_holdings.append(dh)
        else:
            self._all_holdings[-1] = dh

    def update_signal(self, event):
        """ 处理策略函数产生的下单事件。

        可能产生一系列order事件，在bar的开盘时间交易。
        """
        assert event.route == Event.SIGNAL
        new_orders = []
        for order in event.orders:
            errmsg = self._valid_order(order)
            if errmsg == '':
                order.datetime = self._datetime
                new_orders.append(order)
                if order.side == TradeSide.KAI:
                    self.holding['cash'] -= \
                        order.order_margin(self._bars[order.contract].open)
            else:
                logger.warn(errmsg)
                # six.print_(len(event.orders), len(new_orders))
                continue
        self.open_orders.update(new_orders)  # 改变对象的值，不改变对象地址。
        self._all_orders.extend(new_orders)
        for order in new_orders:
            self.api.order(copy.deepcopy(order))
        for order in new_orders:
            if order.side == TradeSide.PING:
                pos = self.positions[
                    PositionKey(order.contract, order.direction)]
                pos.closable -= order.quantity

    def update_fill(self, event):
        """ 处理委托单成交事件。 """
        # @TODO 订单编号和成交编号区分开
        assert event.route == Event.FILL
        trans = event.transaction
        try:
            self.open_orders.remove(trans.order)
        except KeyError:
            if trans.order.side == TradeSide.CANCEL:
                raise TradingError(err='重复撤单')
            else:
                assert(False and '重复成交')
        self._update_holding(trans)
        self._update_positions(trans)

    def _update_positions(self, trans):
        """ 更新持仓 """
        poskey = PositionKey(trans.contract, trans.direction)
        if trans.side == TradeSide.CANCEL:
            pos = self.positions.get(poskey, None)
            if pos:
                pos.closable += trans.quantity
            return
        pos = self.positions.setdefault(poskey, Position(trans))
        if trans.side == TradeSide.KAI:
            pos.cost = (pos.cost*pos.quantity + trans.price*trans.quantity) / \
                        (pos.quantity+trans.quantity)
            pos.quantity += trans.quantity
            if trans.contract.is_stock:
                pos.today += trans.quantity
            else:
                pos.closable += trans.quantity
            assert(pos.quantity == pos.today + pos.closable)
        elif trans.side == TradeSide.PING:
            pos.quantity -= trans.quantity
            if pos.quantity == 0:
                del self.positions[poskey]

    def _update_holding(self, trans):
        """ 更新佣金和平仓盈亏。 """
        if trans.side == TradeSide.CANCEL:
            return
        self.holding['commission'] += trans.commission
        # 平仓，更新历史持仓盈亏。
        if trans.side == TradeSide.PING:
            poskey = PositionKey(trans.contract, trans.direction)
            flag = 1 if trans.direction == Direction.LONG else -1
            profit = (trans.price-self.positions[poskey].cost) * \
                trans.quantity * flag * trans.volume_multiple
            self.holding['history_profit'] += profit
        self._all_transactions.append(trans)

    def _valid_order(self, order):
        """ 判断订单是否合法。 """
        if order.quantity <= 0:
            return "交易数量要大于0"
        # 撤单
        if order.side == TradeSide.CANCEL:
            if order not in self.open_orders:
                return '撤销失败： 不存在该订单！'
        if order.side == TradeSide.PING:
            try:
                poskey = PositionKey(order.contract, order.direction)
                pos = self.positions[poskey]
                if pos.closable < order.quantity:
                    return '可平仓位不足'
            except KeyError:
                # 没有持有该合约
                # logger.warn("不存在合约[%s]" % order.contract)
                return "不存在合约[%s]" % order.contract
        elif order.side == TradeSide.KAI:
            new_price = self._bars[order.contract].open
            if self.holding['cash'] < order.order_margin(new_price):
                # six.print_(self.holding['cash'], new_price * order.quantity)
                return '没有足够的资金开仓'
        return ''

    def _force_close(self):
        """ 在回测的最后一根k线以close价格强平持仓位。 """
        force_trans = []
        if self._all_transactions:
            price_type = self._all_transactions[-1].price_type
        else:
            price_type = PriceType.LMT
        for pos in six.itervalues(self.positions):
            order = Order(
                self._datetime,
                pos.contract,
                price_type,
                TradeSide.PING,
                pos.direction,
                self._bars[pos.contract].close,
                pos.quantity
            )
            force_trans.append(Transaction(order))
        for trans in force_trans:
            self._update_holding(trans)
            self._update_positions(trans)
        if force_trans:
            self.update_status(trans.datetime, False)
        self.positions = {}
        return

    def _init_state(self):
        self.holding = {
            'cash': self._capital,
            'commission':  0.0,
            'history_profit':  0.0,
            'position_profit': 0.0,
            'equity': self._capital
        }


# kai = 0
# ping = 0
