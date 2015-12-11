# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from quantdigger.engine.event import OrderEvent, Event
from quantdigger.datastruct import Position, TradeSide, Direction, PriceType, OneDeal
from quantdigger.util import elogger as logger
from quantdigger.datastruct import PContract
from api import SimulateTraderAPI

class Profile(object):
    """ 组合结果 """
    def __init__(self, blotters, dcontexts, pcon, i):
        self._blts = blotters # 组合内所有策略的blotter
        self._dcontexts = dcontexts   # 所有数据上下文
        self.i = i   # 对应于第几个组合
        self._main_pcontract = pcon

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
                update_positions(positions, deals, trans)
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
                

    def current_positions(self, j):
        """ 当前持仓
        
        Args:
            j (int): 第j个策略
        
        Returns:
            dict. { Contract: Position }
        """
        ## @TODO 组合持仓
        return self._blts[j].current_positions

    def current_holdings(self, j=None):
        """ 当前账号情况
        
        Args:
            j (int): 第j个策略
        
        Returns:
            dict. {'cash', 'commission', 'history_profit', 'equity' }
        """
        if j != None:
            return self._blts[j].current_holdings
        if len(self._blts) == 1:
            return self._blts[0].current_holdings
        import copy
        holdings = copy.deepcopy(self._blts[0].current_holdings)
        for blt in self._blts[1:]:
            rhd = blt.current_holdings
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
        pcon = PContract.from_string(strpcon) if strpcon else self._main_pcontract
        if j != None:
            return self._dcontexts[pcon].indicators[self.i][j]
        rst = { }
        for j in range(0, len(self._blts)):
            rst.update(self._dcontexts[pcon].indicators[self.i][j])
        return rst
            

    def data(self, strpcon=None):
        """ 周期合约数据
        
        Args:
            strpcon (str): 周期合约，如'BB.SHFE-1.Minute' 
        
        Returns:
            pd.DataFrame. 数据
        """
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
        self._pre_settlement = 0     # 昨日结算价
        self._datetime = None # 当前时间
        self.api = SimulateTraderAPI(self, events_pool) # 模拟交易接口

        # 用于分析策略性能数据
        self.all_orders = []
        if settings:
            self._captial =  settings['captial'] # 初始权益
        else:
            self._captial = 5000.0

        self.current_positions = {}  # Contract -> Position
        self.current_holdings = {}  # 当前的资金 dict
        self.all_holdings = []   # 所有时间点上的资金 list of dict
        self.transactions = []
        self.pp = []

    def _init_state(self):
        self.current_holdings = {
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
        dh['equity'] = self._captial + self.current_holdings['history_profit'] + profit - \
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

def update_positions(current_positions, deal_positions, trans):
    """ 更新持仓 
        current_positions: 当前持仓
        deal_positions: 开平仓对
    """
    ## @todo 区分多空
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

    p = current_positions.setdefault(trans.contract, PositionsDetail())
    if trans.side == TradeSide.KAI:
        # 开仓
        p.positions.append(trans)
        p.total += trans.quantity 

    elif trans.side == TradeSide.PING:
        # 平仓
        p.total -= trans.quantity 
        left_vol = trans.quantity
        last_index = 0
        for position in reversed(p.positions):
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



