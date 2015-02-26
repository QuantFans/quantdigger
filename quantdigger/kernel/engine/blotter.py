# -*- coding: utf8 -*-
import pandas as pd
from abc import ABCMeta, abstractmethod

from quantdigger.kernel.engine.event import OrderEvent, Event
from quantdigger.kernel.datastruct import Position
from performance import create_sharpe_ratio, create_drawdowns

class Positions(object):
    """docstring for Positions"""
    def __init__(self):
        self.total = 0
        self.positions = set()


class DealPosition(object):
    """ 开仓，平仓对"""
    def __init__(self, buy_trans, sell_trans):
        self.open = buy_trans
        self.close = sell_trans

    def profit(self):
        """""" 
        direction = self.open.order.direction
        if direction == 'd':
            return self.close.price - self.open.price
        else:
            return self.open.price - self.close.price

    @property
    def open_datetime(self):
        return self.open.datetime

    @property
    def open_price(self):
        return self.open.price

    @property
    def close_datetime(self):
        return self.close.datetime

    @property
    def close_price(self):
        return self.close.price


class Blotter(object):
    """
    订单管理
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        raise NotImplementedError("Should implement update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        raise NotImplementedError("Should implement update_fill()")


class SimpleBlotter(Blotter):
    """
    The SimpleBlotter object is designed to send orders to
    a brokerage object with a constant quantity size blindly,
    i.e. without any risk management or position sizing. It is
    used to test simpler strategies such as BuyAndHoldStrategy.
    """
    def __init__(self, timeseries, events_pool, initial_capital=5000.0):
        """docstring for __init__""" 
        self._timeseries = timeseries
        self.events = events_pool
        self._open_orders = list()
        self._pre_settlement = 0     # 昨日结算价
        self._datetime = None # 当前时间

        # 用于分析策略性能数据
        self.all_orders = []
        self.initial_capital = initial_capital    # 初始资金
        self.current_positions = {}  # 当前持仓 dict of list, 包含细节。
        self.current_holdings = {}  # 当前的资金 dict
        self.all_positions = []    # 在所有时间点上的持仓 list of dict
        self.all_holdings = []   # 所有时间点上的资金 list of dict
        self.deals = [] # 每笔交易
        self.deal_positions = []   # 开平仓对

    def _init_state(self):
        """docstring for _init_state""" 
        self.all_positions = [{'datetime' : self._start_date }]
        self.current_holdings = {
                'cash': self.initial_capital,
                'commission':  0.0,
                'total': self.initial_capital
        }
        self.all_holdings = [{
            'datetime': self._start_date,
            'cash': self.initial_capital,
            'commission':  0.0,
            'total': self.initial_capital
        }]

    def update_bar(self, bars):
        """docstring for update_bar""" 
        self._bars = bars

    def update_datetime(self, dt):
        """
        在新的价格数据来的时候触发。
        """
        # 初始化
        if self._datetime == None:
            self._start_date = dt
            self._init_state()

        self._datetime = dt

        # 更新持仓历史。
        dp = { }
        dp['datetime'] = dt
        for key, value in self.current_positions.iteritems():
            dp[key] = value.total
        self.all_positions.append(dp)

        # 更新资金历史。
        dh = { }

        #dh['datetime'] = dt
        #dh['commission'] = self.current_holdings['commission']
        #dh['total'] = 0
        #pre_assure = self.current_holdings['assure']
        #self.current_holdings['assure'] = 0
        #for contract, pos_info in self.current_positions.iteritems():
            ## 以close价格替代市场价格。
            #market_value = self._bars[contract].close * pos_info.total
            #dh[contract] = market_value
            #dh['total'] += 该品种的保证金 / 该品种的保证金比例
            #assure_ratio = pos_info.positions[0].assure_ratio
            #self.current_holdings['assure'] += market_value * assure_ratio
            #dh['assure'] = self.current_holdings['assure']

        #self.current_holdings['cash'] -= (self.current_holdings['assure'] - pre_assure)
        #dh['cash'] = self.current_holdings['cash']
        #dh['total'] += self.current_holdings['cash']
        #if self.current_holdings['cash'] < 0:
            #raise Exception('你已经破产!')


        dh['datetime'] = dt
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = 0
        for contract, pos_info in self.current_positions.iteritems():
            # 以close价格替代市场价格。
            market_value = self._bars[contract].close * pos_info.total
            dh[contract] = market_value
            dh['total'] += market_value

        dh['cash'] = self.current_holdings['cash']
        dh['total'] += self.current_holdings['cash']
        self.all_holdings.append(dh)

    def _update_positions(self, order, trans):
        ## @todo 把复杂统计单独出来。
        """ 更新持仓 """
        p = self.current_positions.setdefault(trans.contract, Positions())
        new_pos = Position(order, trans)

        #if order.order_bar_index == 445:
            #print order.kpp
            #print order.direction
            #assert False

        if trans.kpp == 'k':
            # 开仓
            p.positions.add(new_pos)
            if trans.direction == 'd':
                p.total += trans.quantity 
            else:
                p.total -= trans.quantity 
        elif trans.kpp == 'p':
            if trans.direction == 'd':
                p.total -= trans.quantity 
            else:
                p.total += trans.quantity 
            # 平仓
            to_delete = set()
            left_vol = trans.quantity
            for position in reversed(list(p.positions)):
                # 原地改变结果。
                #position.quantity -= left_vol
                #for p in p.positions:
                    #if id(p) == id(position):
                        #assert False 
                self.deal_positions.append(DealPosition(position, new_pos))
                if position.quantity < left_vol:
                    # 还需从之前的仓位中平。
                    left_vol -= position.quantity
                    to_delete.add(position)

                elif position.quantity == left_vol:
                    left_vol -= position.quantity
                    to_delete.add(position)
                    break 

                else:
                    assert False
                    position.quantity -= left_vol
                    left_vol = 0
                    break
            p.positions -= to_delete
            #if trans.kpp == 'p':
                #print "order:",  to_delete.pop().order.order_bar_index, "   ", "ping:", order.order_bar_index
            assert(left_vol == 0)

    def _update_holdings(self, trans):
        """
        更新资金
        """
        trans_kpp = 1 if trans.kpp == 'k' else -1
        trans_cost = self._bars[trans.contract].close  # Close price
        cost = trans_kpp * trans_cost * trans.quantity
        actual_cost = trans.assure_ratio * cost if trans.kpp == 'k' else cost
        #self.current_holdings['assure'] += actual_cost
        self.current_holdings['commission'] += trans.commission     # 每笔佣金，和数目无关！
        self.current_holdings['cash'] -= (actual_cost + trans.commission)  # 现金
        # 正确的值会在下一个时间点update_datetime中补回来，但不影响本轮的使用。
        # total = cash + market_value
        self.current_holdings['total'] -= (actual_cost + trans.commission)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        print "on_fill_event" 
        assert event.type == Event.FILL
        t_order = None
        for i, order in enumerate(self._open_orders):
            if order.id == event.transaction.id:
                t_order = self._open_orders.pop(i)
                break
        assert(t_order)
        self._update_positions(t_order, event.transaction)
        self._update_holdings(event.transaction)

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        assert event.type == Event.SIGNAL
        valid_orders = []
        for order in event.orders:
            if self.valid_order(order):
                self.events.put(OrderEvent(order)) 
                valid_orders.append(order)
        self._open_orders.extend(valid_orders)
        self.all_orders.extend(valid_orders)
        #print "Receive %d signals!" % len(event.orders)
        #self.generate_naive_order(event.orders)

    def valid_order(self, order):
        """docstring for valid_order""" 
        if order.kpp == 'p':
            try:
                pos = self.current_positions[order.contract]
                if order.direction == 'd':
                    ## @todo 自动改变合法仓位。
                    if pos.total > 0:
                        return True 
                elif order.direction == 'k':
                    ## @todo 自动改变合法仓位。
                    if pos.total < 0:
                        return True 
            except KeyError:
                return False
            return False
        return True

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio such
        as Sharpe Ratio and drawdown information.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]
        return stats
