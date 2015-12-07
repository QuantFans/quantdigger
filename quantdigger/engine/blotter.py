# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from quantdigger.engine.event import OrderEvent, Event
from quantdigger.datastruct import Position, TradeSide, Direction, PriceType
from quantdigger.util import engine_logger as logger
from api import SimulateTraderAPI



class Blotter(object):
    """
    订单管理。
    """
    __metaclass__ = ABCMeta

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
    def __init__(self, timeseries, events_pool, initial_capital=5000.0):
        self._timeseries = timeseries
        self._open_orders = list()
        self._pre_settlement = 0     # 昨日结算价
        self._datetime = None # 当前时间
        self._init_captial = initial_capital
        self.api = SimulateTraderAPI(self, events_pool) # 模拟交易接口

        # 用于分析策略性能数据
        self.all_orders = []
        self.initial_capital = initial_capital    # 初始权益

        self.current_positions = {}  # 当前持仓 dict of list, 包含细节。
        self.current_holdings = {}  # 当前的资金 dict
        self.all_holdings = []   # 所有时间点上的资金 list of dict
        self.transactions = []
        self.pp = []

    def _init_state(self):
        self.current_holdings = {
                'cash': self.initial_capital,
                'commission':  0.0,
                'history_profit':  0.0,
                'equity': self.initial_capital
        }
        self.all_holdings = [{
            'datetime': self._start_date,
            'cash': self.initial_capital,
            'commission':  0.0,
            'equity': self.initial_capital
        }]

    def update_ticks(self, ticks):
        """ 当前bar数据更新。 """ 
        self._ticks = ticks

    def update_datetime(self, dt):
        """
        在新的价格数据来的时候触发。
        """
        # 
        if self._datetime == None:
            self._start_date = dt
            self._init_state()
        self._datetime = dt
        self._update_status(dt)

    def _update_status(self, dt):
        """ 更新历史持仓，当前权益。"""

        # 更新资金历史。
        ## @todo  由持仓历史推断资金历史。
        dh = { }
        dh['datetime'] = dt
        dh['commission'] = self.current_holdings['commission']
        profit = 0
        margin = 0
        order_margin = 0;

        # 计算当前持仓历史盈亏。
        # 以close价格替代市场价格。
        is_stock = True  # 默认是股票回测
        for contract, pos in self.current_positions.iteritems():
            new_price = self._ticks[contract]
            profit += pos.profit(new_price)
            ## @todo 用昨日结算价计算保证金
            margin += pos.position_margin(new_price)
            if not contract.is_stock:
                is_stock =  False   # 

        # 计算限价报单的保证金占用
        for order in self._open_orders:
            assert(order.price_type == PriceType.LMT)
            order_margin +=  order.order_margin()

        # 当前权益 = 初始资金 + 历史平仓盈亏 + 当前持仓盈亏 - 历史佣金总额 
        dh['equity'] = self._init_captial + self.current_holdings['history_profit'] + profit - \
                       self.current_holdings['commission'] 
        dh['cash'] = dh['equity'] - margin - order_margin
        if dh['cash'] < 0:
            if not is_stock:
                # 如果是期货需要追加保证金
                ## @bug 如果同时交易期货和股票，就有问题。
                raise Exception('需要追加保证金!')

        self.current_holdings['cash'] = dh['cash']
        self.current_holdings['equity'] = dh['equity']
        self.all_holdings.append(dh)

    def update_signal(self, event):
        """
        处理策略函数产生的下单事件。
        """
        assert event.type == Event.SIGNAL
        valid_orders = []
        for order in event.orders:
            if self._valid_order(order):
                self.api.order(order)
                valid_orders.append(order)
            else:
                continue
        self._open_orders.extend(valid_orders)
        self.all_orders.extend(valid_orders)
        #print "Receive %d signals!" % len(event.orders)
        #self.generate_naive_order(event.orders)

    def update_fill(self, event):
        """
        处理委托单成交事件。
        """
        assert event.type == Event.FILL
        t_order = None
        for i, order in enumerate(self._open_orders):
            if order.id == event.transaction.id:
                t_order = self._open_orders.pop(i)
                break
        assert(t_order)
        self._update_positions(t_order, event.transaction)
        self._update_holdings(event.transaction)


    def _update_positions(self, order, trans):
        """ 更新持仓 """
        ## @todo 区分多空
        pos = self.current_positions.setdefault(trans.contract, Position(trans))
        if trans.side == TradeSide.KAI:
            # 开仓
            pos.cost = (pos.cost*pos.quantity + trans.price*trans.quantity) / (pos.quantity+trans.quantity)
            pos.quantity += trans.quantity
        elif trans.side == TradeSide.PING:
            # 平仓
            pos.quantity -= trans.quantity


    def _update_holdings(self, trans):
        """
        更新资金
        """
        # 每笔佣金，和数目无关！
        self.current_holdings['commission'] += trans.commission
        # 平仓，更新历史持仓盈亏。
        if trans.side == TradeSide.PING:
            multi = 1 if trans.direction == Direction.LONG else -1
            profit = (trans.price-self.current_positions[trans.contract].cost) * trans.quantity * multi
            self.current_holdings['history_profit'] += profit
            self.pp.append(profit)

        self.transactions.append(trans)

    def _valid_order(self, order):
        """ 判断订单是否合法。 """ 
        if order.side == TradeSide.PING:
            try:
                pos = self.current_positions[order.contract]
                if pos.quantity >= order.quantity:
                    return True 
            except KeyError:
                # 没有持有该合约
                logger.warn("不存在合约[%s]" % order.contract)
                #assert False
                return False
            logger.warn("下单仓位问题")
            return False
        elif order.side == TradeSide.KAI:
            if self.current_holdings['cash'] < order.price * order.quantity:
                raise Exception('没有足够的资金开仓') 
        return True

