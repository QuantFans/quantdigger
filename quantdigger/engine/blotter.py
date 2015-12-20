# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from datetime import datetime
from quantdigger.engine import series
from quantdigger.util import elogger as logger
from quantdigger.errors import TradingError
from quantdigger.engine.api import SimulateTraderAPI
from quantdigger.engine.event import Event
from quantdigger.datastruct import (
    Direction, 
    OneDeal,
    Order,
    PContract,
    Position, 
    PositionKey,
    PriceType, 
    TradeSide,
    Transaction,
)


class Profile(object):
    """ 组合结果 """
    def __init__(self, blotters, dcontexts, strpcon, i):
        self._blts = blotters # 组合内所有策略的blotter
        self._dcontexts = { }
        for key, value in dcontexts.iteritems():
            self._dcontexts[key] = value
        self.i = i   # 对应于第几个组合
        self._main_pcontract = strpcon

    def name(self, j):
        return self._blts[j].name

    def transactions(self, j=None):
        """ 第j个策略的所有成交明细, 默认返回组合的成交明细。
        
        Args:
            j (int): 第j个策略
        
        Returns:
            list. [Transaction, ..]
        """
        if j != None:
            return self._blts[j].transactions
        trans = []
        for blt in self._blts:
            trans.append(blt.transactions)
        ## @TODO 时间排序
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
        if j != None:
            for trans in self.transactions(j):
                _update_positions(positions, deals, trans)
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
        if j != None:
            return self._blts[j].all_holdings
        if len(self._blts) == 1:
            return self._blts[0].all_holdings
        import copy
        holdings = copy.deepcopy(self._blts[0].all_holdings)
        #print self._blts[0].all_holdings
        #print self._blts[1].all_holdings
        for i, hd in enumerate(holdings):
            for blt in self._blts[1:]:
                rhd = blt.all_holdings[i]
                hd['cash'] += rhd['cash']
                hd['commission'] += rhd['commission']
                hd['equity'] += rhd['equity']
        return holdings
                

    #def current_positions(self, j):
        #""" 当前持仓
        
        #Args:
            #j (int): 第j个策略
        
        #Returns:
            #dict. { Contract: Position }
        #"""
        #return self._blts[j].current_positions.values()

    def holding(self, j=None):
        """ 当前账号情况
        
        Args:
            j (int): 第j个策略
        
        Returns:
            dict. {'cash', 'commission', 'history_profit', 'equity' }
        """
        if j != None:
            return self._blts[j].holding
        if len(self._blts) == 1:
            return self._blts[0].holding
        import copy
        holdings = copy.deepcopy(self._blts[0].holding)
        for blt in self._blts[1:]:
            rhd = blt.holding
            holdings['cash'] += rhd['cash']
            holdings['commission'] += rhd['commission']
            holdings['equity'] += rhd['equity']
            holdings['history_profit'] += rhd['history_profit']
        return holdings

    def indicators(self, j=None, strpcon=None):
        """ 返回第j个策略的指标, 默认返回组合的所有指标。
        
        Args:
            j (int): 第j个策略

            strpcon (str): 周期合约
        
        Returns:
            dict. {指标名:指标}
        """
        pcon = strpcon if strpcon else self._main_pcontract
        if j != None:
            return self._dcontexts[pcon].indicators[self.i][j]
        rst = { }
        for j in range(0, len(self._blts)):
            rst.update(self._dcontexts[pcon].indicators[self.i][j])
        return rst
            

    def data(self, strpcon=None):
        """ 周期合约数据, 只有向量运行才有意义。
        
        Args:
            strpcon (str): 周期合约，如'BB.SHFE-1.Minute' 
        
        Returns:
            pd.DataFrame. 数据
        """
        if series.g_rolling:
            assert(False and '只有向量运行才存在数据') 
        pcon = self._main_pcontract
        if strpcon:
            pcon = PContract.from_string(strpcon) 
        return self._dcontexts[pcon].raw_data
    


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
    def __init__(self, name, events_pool, settings={ }):
        super(SimpleBlotter, self).__init__(name)
        self._open_orders = list()
        self._all_orders = []
        self._pre_settlement = 0     # 昨日结算价
        self._datetime = None # 当前时间
        self.positions = {}  # Contract: Position
        self.holding = {}  # 当前的资金 dict
        self._all_holdings = []   # 所有时间点上的资金 list of dict
        self._all_transactions = []
        self.api = SimulateTraderAPI(self, events_pool) # 模拟交易接口
        if settings:
            self._captial =  settings['captial'] # 初始权益
        else:
            self._captial = 5000.0

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


    def _force_close(self):
        """ 在回测的最后一根k线以close价格强平持仓位。""" 
        force_trans = []
        price_type = self._all_transactions[-1].price_type if self._all_transactions else PriceType.LMT 
        for pos in self.positions.values():
            order = Order(
                    self._datetime,
                    pos.contract,
                    price_type,
                    TradeSide.PING,
                    pos.direction,
                    self._ticks[pos.contract],
                    pos.quantity
            )
            force_trans.append(Transaction(order))
        for trans in force_trans:
            self._update_holding(trans)
            self._update_positions(trans)
        if force_trans:
            self.update_status(trans.datetime, False)
        self.positions = { }
        return


    def _init_state(self):
        self.holding = {
                'cash': self._captial,
                'commission':  0.0,
                'history_profit':  0.0,
                'equity': self._captial
        }

    def update_data(self, ticks, bars):
        """ 当前价格数据更新。 """ 
        self._ticks = ticks
        self._bars = bars

    def update_datetime(self, dt):
        """
        在新的价格数据来的时候触发。
        """
        # 
        if self._datetime == None:
            self._datetime = dt
            self._start_date = dt
            self._init_state()
        elif self._datetime.date() != dt.date():
            self._open_orders = []
        self._datetime = dt

    def update_status(self, dt, append=True):
        """ 更新历史持仓，当前权益。"""

        # 更新资金历史。
        dh = { }
        dh['datetime'] = dt
        dh['commission'] = self.holding['commission']
        profit = 0
        margin = 0
        order_margin = 0;

        # 计算当前持仓历史盈亏。
        # 以close价格替代市场价格。
        is_stock = True  # 默认是股票回测
        for key, pos in self.positions.iteritems():
            new_price = self._ticks[key.contract]
            profit += pos.profit(new_price)
            ## @TODO 用昨日结算价计算保证金
            margin += pos.position_margin(new_price)
            if not key.contract.is_stock:
                is_stock =  False   # 

        # 计算限价报单的保证金占用
        for order in self._open_orders:
            assert(order.price_type == PriceType.LMT)
            new_price = self._ticks[order.contract]
            order_margin +=  order.order_margin(new_price)

        # 当前权益 = 初始资金 + 累积平仓盈亏 + 当前持仓盈亏 - 历史佣金总额 
        dh['equity'] = self._captial + self.holding['history_profit'] + profit - \
                       self.holding['commission'] 
        dh['cash'] = dh['equity'] - margin - order_margin
        if dh['cash'] < 0:
            if not is_stock:
                # 如果是期货需要追加保证金
                ## @bug 如果同时交易期货和股票，就有问题。
                raise Exception('需要追加保证金!')

        self.holding['cash'] = dh['cash']
        self.holding['equity'] = dh['equity']
        if append:
            self._all_holdings.append(dh)
        else:
            self._all_holdings[-1] = dh

    def update_signal(self, event):
        """
        处理策略函数产生的下单事件。
        """
        assert event.type == Event.SIGNAL
        valid_orders = []
        for order in event.orders:
            if self._valid_order(order):
                order.datetime = self._datetime
                self.api.order(order)
                valid_orders.append(order)
            else:
                continue
        self._open_orders.extend(valid_orders)
        self._all_orders.extend(valid_orders)
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
        self._update_holding(event.transaction)
        self._update_positions(event.transaction)


    def _update_positions(self, trans):
        """ 更新持仓 """
        poskey = PositionKey(trans.contract, trans.direction)
        pos = self.positions.setdefault(poskey, Position(trans))
        #print len(self.positions)
        #print pos.contract, pos.quantity
        if trans.side == TradeSide.KAI:
            # 开仓
            pos.cost = (pos.cost*pos.quantity + trans.price*trans.quantity) / (pos.quantity+trans.quantity)
            pos.quantity += trans.quantity
        elif trans.side == TradeSide.PING:
            # 平仓
            pos.quantity -= trans.quantity
            if pos.quantity == 0:
                del self.positions[poskey] 

    def _update_holding(self, trans):
        """
        更新佣金和平仓盈亏。
        """
        # 每笔佣金，和数目无关！
        self.holding['commission'] += trans.commission
        # 平仓，更新历史持仓盈亏。
        if trans.side == TradeSide.PING:
            poskey = PositionKey(trans.contract, trans.direction)
            multi = 1 if trans.direction == Direction.LONG else -1
            profit = (trans.price-self.positions[poskey].cost) * trans.quantity * multi
            self.holding['history_profit'] += profit
        self._all_transactions.append(trans)

    def _valid_order(self, order):
        """ 判断订单是否合法。 """ 
        if order.side == TradeSide.PING:
            try:
                poskey = PositionKey(order.contract, order.direction)
                pos = self.positions[poskey]
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
            if self.holding['cash'] < order.price * order.quantity:
                raise TradingError(err='没有足够的资金开仓') 
        return True

kai = 0
ping = 0
def _update_positions(current_positions, deal_positions, trans):
    """ 更新持仓 
        current_positions: 当前持仓
        deal_positions: 开平仓对
    """
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
    assert trans.quantity>0
    poskey = PositionKey(trans.contract, trans.direction)
    p = current_positions.setdefault(poskey, PositionsDetail())
    if trans.side == TradeSide.KAI:
        # 开仓
        p.positions.append(trans)
        p.total += trans.quantity 

    elif trans.side == TradeSide.PING:
        # 平仓
        assert(len(p.positions)>0 and '所平合约没有持仓')
        left_vol = trans.quantity
        last_index = 0
        p.total -= trans.quantity
        for position in reversed(p.positions):
            print position.quantity, p.total
            if position.quantity < left_vol:
                # 还需从之前的仓位中平。
                left_vol -= position.quantity
                last_index -= 1
                deal_positions.append(OneDeal(position, trans, position.quantity))

            elif position.quantity == left_vol:
                left_vol -= position.quantity
                last_index -= 1
                deal_positions.append(OneDeal(position, trans, position.quantity))
                break 

            else:
                position.quantity -= left_vol
                left_vol = 0
                deal_positions.append(OneDeal(position, trans, left_vol))
                break
        if last_index != 0:
            p.positions = p.positions[0 : last_index]
        assert(left_vol == 0) # 会被catch捕获 AssertError
        #if mark:
            #print '------------' 
            #print len(p.positions)
            #assert False



