# -*- coding: utf-8 -*-
import copy
from abc import ABCMeta, abstractmethod
from quantdigger.util import elogger as logger
from quantdigger.errors import TradingError
from quantdigger.engine.api import SimulateTraderAPI
from quantdigger.engine.event import Event
from quantdigger.config import settings
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
        self._ith_comb = i   # 对应于第几个组合
        self._main_pcontract = strpcon
        for key, value in dcontexts.iteritems():
            self._dcontexts[key] = value

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
        if j != None:
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
        holdings = copy.deepcopy(self._blts[0].holding)
        for blt in self._blts[1:]:
            rhd = blt.holding
            holdings['cash'] += rhd['cash']
            holdings['commission'] += rhd['commission']
            holdings['equity'] += rhd['equity']
            holdings['history_profit'] += rhd['history_profit']
        return holdings

    def technicals(self, j=None, strpcon=None):
        ## @TODO test case
        """ 返回第j个策略的指标, 默认返回组合的所有指标。
        
        Args:
            j (int): 第j个策略

            strpcon (str): 周期合约
        
        Returns:
            dict. {指标名:指标}
        """
        pcon = strpcon if strpcon else self._main_pcontract
        if j != None:
            return { v.name: v for v in self._dcontexts[pcon].\
                    indicators[self._ith_comb][j].itervalues() }
        rst = { }
        for j in range(0, len(self._blts)):
            t = { v.name: v for v in self._dcontexts[pcon].\
                indicators[self._ith_comb][j].itervalues() }
            rst.update(t)
        return rst
            
    def data(self, strpcon=None):
        """ 周期合约数据, 只有向量运行才有意义。
        
        Args:
            strpcon (str): 周期合约，如'BB.SHFE-1.Minute' 
        
        Returns:
            pd.DataFrame. 数据
        """
        pcon = self._main_pcontract
        if strpcon:
            pcon = PContract.from_string(strpcon) 
        return self._dcontexts[pcon].raw_data

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
            if last_index != 0 and search_index != 0:
                p.positions = positions[0 : last_index] + left_positions
            elif last_index != 0:
                p.positions = positions[0 : last_index]
            # last_index == 0, 表示没找到可平的的开仓对，最后一根强平
            assert(left_vol == 0 or last_index == 0) # 可以被catch捕获 AssertError
    

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
        self.open_orders = set()
        self.positions = {}  # Contract: Position
        self.holding = {}  # 当前的资金 dict
        self.api = SimulateTraderAPI(self, events_pool) # 模拟交易接口
        self._all_orders = []
        self._pre_settlement = 0     # 昨日结算价
        self._datetime = None # 当前时间
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
        #self._ticks = ticks
        self._bars = bars

    def update_datetime(self, dt):
        """ 在新的价格数据来的时候触发。 """
        if self._datetime == None:
            self._datetime = dt
            self._start_date = dt
            self._init_state()
        elif self._datetime.date() != dt.date():
            for order in self.open_orders:
                if order.side == TradeSide.PING:
                    pos = self.positions[PositionKey(order.contract, order.direction)]
                    pos.closable += order.quantity
            self.open_orders.clear()
            for key, pos in self.positions.iteritems():
                pos.closable += pos.today
                pos.today = 0
        self._datetime = dt

    def update_status(self, dt, at_baropen=True):
        """ 更新历史持仓，当前权益。"""
        # 更新资金历史。
        dh = { }
        dh['datetime'] = dt
        dh['commission'] = self.holding['commission']
        pos_profit = 0
        margin = 0
        order_margin = 0;
        # 计算当前持仓历史盈亏。
        # 以close价格替代市场价格。
        for key, pos in self.positions.iteritems():
            bar = self._bars[key.contract]
            new_price = bar.open if at_baropen else bar.close
            pos_profit += pos.profit(new_price)
            ## @TODO 用昨日结算价计算保证金
            margin += pos.position_margin(new_price)
        # 计算未成交开仓报单的保证金占用
        for order in self.open_orders:
            assert(order.price_type == PriceType.LMT)
            bar = self._bars[order.contract]
            new_price = bar.open if at_baropen else bar.close
            if order.side == TradeSide.KAI:
                order_margin += order.order_margin(new_price)
        # 当前权益 = 初始资金 + 累积平仓盈亏 + 当前持仓盈亏 - 历史佣金总额 
        dh['equity'] = self._capital + self.holding['history_profit'] + pos_profit - \
                       self.holding['commission'] 
        dh['cash'] = dh['equity'] - margin - order_margin
        if dh['cash'] < 0:
            for key in self.positions.iterkeys():
                if not key.contract.is_stock:
                    ## @NOTE  只要有一个是期货，在资金不足的时候就得追加保证金
                    raise Exception('需要追加保证金!')
        self.holding['cash'] = dh['cash']
        self.holding['equity'] = dh['equity']
        self.holding['position_profit'] = pos_profit
        if at_baropen:
            self._all_holdings.append(dh)
        else:
            self._all_holdings[-1] = dh

    def update_signal(self, event):
        """ 处理策略函数产生的下单事件。 """
        assert event.type == Event.SIGNAL
        new_orders = []
        for order in event.orders:
            if self._valid_order(order):
                order.datetime = self._datetime
                self.api.order(copy.deepcopy(order))
                new_orders.append(order)
            else:
                continue
        self.open_orders.update(new_orders) # 改变对象的值，不改变对象地址。
        self._all_orders.extend(new_orders)
        for order in new_orders:
            if order.side == TradeSide.PING:
                pos = self.positions[PositionKey(order.contract, order.direction)]
                pos.closable -= order.quantity
        #print "Receive %d signals!" % len(event.orders)
        #self.generate_naive_order(event.orders)

    def update_fill(self, event):
        """ 处理委托单成交事件。 """
        ## @TODO 订单编号和成交编号区分开
        assert event.type == Event.FILL
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
            profit = (trans.price-self.positions[poskey].cost) * trans.quantity *\
                     flag * trans.volume_multiple
            #if self.name == 'A1': # 平仓调试
                #print "***********" 
                #print self._datetime, profit 
            self.holding['history_profit'] += profit
        self._all_transactions.append(trans)

    def _valid_order(self, order):
        """ 判断订单是否合法。 """ 
        if order.quantity<=0:
            raise TradingError(err="交易数量不能小于0")
        # 撤单
        if order.side == TradeSide.CANCEL:
            if order not in self.open_orders:
                raise TradingError(err='撤销失败： 不存在该订单！') 
        if order.side == TradeSide.PING:
            try:
                poskey = PositionKey(order.contract, order.direction)
                pos = self.positions[poskey]
                if pos.closable < order.quantity:
                    raise TradingError(err='可平仓位不足')
            except KeyError:
                # 没有持有该合约
                #logger.warn("不存在合约[%s]" % order.contract)
                raise TradingError(err="不存在合约[%s]" % order.contract)
        elif order.side == TradeSide.KAI:
            new_price = self._bars[order.contract].close
            if self.holding['cash'] < order.order_margin(new_price):
                raise TradingError(err='没有足够的资金开仓') 
            else:
                self.holding['cash'] -= order.order_margin(new_price)
        return True

    def _force_close(self):
        """ 在回测的最后一根k线以close价格强平持仓位。 """ 
        force_trans = []
        price_type = self._all_transactions[-1].price_type if self._all_transactions else PriceType.LMT 
        for pos in self.positions.values():
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
        self.positions = { }
        return

    def _init_state(self):
        self.holding = {
            'cash': self._capital,
            'commission':  0.0,
            'history_profit':  0.0,
            'position_profit' : 0.0,
            'equity': self._capital
        }


#kai = 0
#ping = 0
