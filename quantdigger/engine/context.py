# -*- coding: utf8 -*-
##
# @file data.py
# @brief 数据上下文，交易上下文。
# @author wondereamer
# @version 0.2
# @date 2015-12-09

import copy
import datetime
import Queue
from quantdigger.engine.blotter import SimpleBlotter
from quantdigger.engine.exchange import Exchange
from quantdigger.engine.series import SeriesBase, NumberSeries, DateTimeSeries
from quantdigger.engine.event import Event, EventsPool, SignalEvent
from quantdigger.errors import TradingError
from quantdigger.technicals.base import TechnicalBase
from quantdigger.util import elogger as logger
from quantdigger.datastruct import (
    Order,
    TradeSide,
    Direction,
    PriceType,
    PositionKey,
    Contract,
    Bar
)


class DataContext(object):
    def __init__(self, wrapper):
        data = wrapper.data
        self.open = NumberSeries(data.open.values, 'open')
        self.close = NumberSeries(data.close.values, 'close')
        self.high = NumberSeries(data.high.values, 'high')
        self.low = NumberSeries(data.low.values, 'low')
        self.volume = NumberSeries(data.volume.values, 'volume')
        self.datetime = DateTimeSeries(data.index, 'datetime')
        self.i = -1   # 第i个组合
        self.j = -1   # 第j个策略
        self.bar = Bar(None, None, None, None, None, None)
        self.last_row = []
        self.last_date = datetime.datetime(2100,1,1)
        self.indicators = [[{ }]]

        self._curbar = -1
        self._wrapper = wrapper
        self._series = [[{ }]]
        self._variables = [[{ }]]
        self._size = len(data.close)

    @property
    def raw_data(self):
        return self._wrapper.data

    @property
    def curbar(self):
        return self._curbar + 1

    @property
    def pcontract(self):
        return self._wrapper.pcontract

    @property
    def contract(self):
        return self._wrapper.pcontract.contract

    def update_system_vars(self):
        #self.data = np.append(data, tracker.container_day)
        self._curbar = self.last_curbar
        self.open.update_curbar(self._curbar)
        self.close.update_curbar(self._curbar)
        self.high.update_curbar(self._curbar)
        self.low.update_curbar(self._curbar)
        self.volume.update_curbar(self._curbar)
        self.datetime.update_curbar(self._curbar)
        self.bar = Bar(self.datetime[0], self.open[0], self.close[0],
                        self.high[0], self.low[0], self.volume[0])
        self.last_row = []
        return

    def rolling_forward(self):
        """ 滚动读取下一步的数据。 """
        new_row, self.last_curbar = self._wrapper.rolling_forward()
        if not new_row:
            self.last_curbar -= 1
            return False, None
        self.last_row = [1] # mark
        self.last_date = self._wrapper.data.index[self.last_curbar]
        if self.datetime[0] >= self.last_date and self.curbar != 0:
            logger.error('合约[%s] 数据时间逆序或冗余' % self.pcontract)
            assert(False)
        return True, new_row

    def update_user_vars(self):
        """ 更新用户定义的变量。 """
        try:
            siter = self._series[self.i][self.j].iteritems()
        except  IndexError:
            # The strategy doesn't have user defined series. 
            pass 
        else:
            for key, s in siter:
                s.update_curbar(self._curbar)
                s.duplicate_last_element()
        try:
            indic_iter = self.indicators[self.i][self.j].iteritems()
        except  IndexError:
            # The strategy doesn't use indicators.
            pass
        else:
            for key, indic in indic_iter:
                if indic.is_multiple:
                    for key, value in indic.series.iteritems():
                        value.update_curbar(self._curbar)
                else:
                    for s in indic.series:
                        s.update_curbar(self._curbar)

    def add_series(self, attr, s):
        """ 添加on_init中初始化的序列变量    
        
        Args:
            attr (str): 属性名
            s (Series): 序列变量 
        """
        s.reset_data([], self._size)
        if self.i < len(self._series):
            if self.j < len(self._series[self.i]):
                self._series[self.i][self.j][attr] = s
            else:
                self._series[self.i].append({ attr: s })
        else:
            self._series.append([{ attr:s }])
        return

    def add_indicator(self, attr, indic):
        if self.i < len(self.indicators):
            if self.j < len(self.indicators[self.i]):
                self.indicators[self.i][self.j][attr] = indic
            else:
                self.indicators[self.i].append({ attr: indic })
        else:
            self.indicators.append([{ attr: indic }])

    def add_variable(self, attr, var):
        if self.i < len(self._variables):
            if self.j < len(self._variables[self.i]):
                self._variables[self.i][self.j][attr] = var
            else:
                self._variables[self.i].append({ attr: var })
        else:
            self._variables.append([{ attr: var }])

    def __len__(self):
        return len(self._wrapper)

    def get_item(self, name):
        """ 获取用户在策略on_init函数中初始化的变量 """
        try:
            return self.indicators[self.i][self.j][name]
        except KeyError:
            try:
                return self._series[self.i][self.j][name]
            except KeyError:
                return self._variables[self.i][self.j][name]
    
    def add_item(self, name, value):
        """ 添加用户初始化的变量。 """ 
        if isinstance(value, SeriesBase):
            self.add_series(name, value)
        elif isinstance(value, TechnicalBase):
            self.add_indicator(name, value)
        else:
            self.add_variable(name, value)

    def __getattr__(self, name):
        return self.get_item(name)


class StrategyContext(object):
    """ 策略组合

    :ivar name: 策略名
    :ivar blotter: 订单管理
    :ivar exchange: 价格撮合器
    """
    def __init__(self, name, settings={ }):
        self.events_pool = EventsPool()
        ## @TODO merge blotter and exchange
        self.blotter = SimpleBlotter(name, self.events_pool, settings)
        self.exchange = Exchange(name, self.events_pool, strict=True)
        self.name = name
        self._orders = []
        self._datetime = None
        self._cancel_now = False # 是当根bar还是下一根bar撤单成功。

    def update_environment(self, dt, ticks, bars):
        """ 更新模拟交易所和订单管理器的数据，时间,持仓 """ 
        self.blotter.update_datetime(dt)
        self.exchange.update_datetime(dt)
        self.blotter.update_data(ticks, bars)
        self._datetime = dt
        return

    def process_trading_events(self, append):
        """ 提交订单，撮合，更新持仓 """
        if self._orders:
            self.events_pool.put(SignalEvent(self._orders))
        self._orders = []
        new_signal = False 
        event = None
        while True:
           # 事件处理。 
            try:
                event = self.events_pool.get()
            except Queue.Empty:
                assert(False)
            except IndexError:
                if new_signal:
                    break
            else:
                #if event.type == 'MARKET':
                    #strategy.calculate_signals(event)
                    #port.update_timeindex(event)
                if event.type == Event.SIGNAL:
                    try:
                        self.blotter.update_signal(event)
                    except TradingError as e:
                        new_signal = True
                        logger.warn(e)
                        return
                elif event.type == Event.ORDER:
                    self.exchange.insert_order(event)
                elif event.type == Event.FILL:
                    # 模拟交易接口收到报单成交
                    self.blotter.api.on_transaction(event)
            # 价格撮合。note: bar价格撮合要求撮合置于运算后面。
            if event == None or event.type == Event.ORDER:
                self.exchange.make_market(self.blotter._bars)
                new_signal = True
        self.blotter.update_status(self._datetime, append)

    def buy(self, direction, price, quantity, price_type, contract):
        self._orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.KAI,
            direction,
            float(price),
            quantity
        ))

    def sell(self, direction, price, quantity, price_type, contract):
        self._orders.append(Order(
            None,
            contract,
            price_type,
            TradeSide.PING,
            direction,
            float(price),
            quantity
        ))

    def cancel(self, orders):
        """ 撤单
        
        Args:
            orders (list/Order): 撤单，参数为list表示撤多个单。
        """
        orders = orders if isinstance(orders, list) else [orders]
        if not self._cancel_now:
            # 下一根bar处理撤单
            for order in orders:
                norder = copy.deepcopy(order)
                norder.side = TradeSide.CANCEL
                self._orders.append(norder)
            return
        ## 立即处理撤单
        #temp = copy.deepcopy(self._orders)
        #self._orders = []
        #for order in orders:
            #order.side = TradeSide.CANCEL
            #self._orders.append(order)
        #self.process_trading_events(False)
        #self._orders = temp
    
    @property
    def open_orders(self):
        """ 未成交的订单 """ 
        return self.blotter.open_orders

    def position(self, contract, direction):
        try:
            poskey = PositionKey(contract, direction) 
            return self.blotter.positions[poskey]
        except KeyError:
            return None

    def pos(self, contract, direction):
        try:
            poskey = PositionKey(contract, direction) 
            return self.blotter.positions[poskey].closable
        except KeyError:
            return 0

    def cash(self):
        return self.blotter.holding['cash']

    def equity(self):
        return self.blotter.holding['equity']

    def profit(self, contract):
        pass

    def day_profit(self, contract):
        """ 当前持仓的浮动盈亏 """ 
        pass


class Context(object):
    """ 上下文"""
    def __init__(self, data, max_window):
        self.ctx_dt_series = DateTimeSeries([datetime.datetime(2100,1,1)]*max_window,
                            'universal_time')
        self.ctx_datetime = datetime.datetime(2100,1,1)
        self.on_bar = False
        self.step = 0
        self._data_contexts = { }       # str(PContract): DataContext
        for key, value in data.iteritems():
            self._data_contexts[key] = value
        self._cur_data_context = None
        self._strategy_contexts = []
        self._cur_strategy_context = None
        self._ticks = { } # Contract: float
        self._bars = { }  # Contract: Bar

    def add_strategy_context(self, ctxs):
        self._strategy_contexts.append(ctxs)

    def switch_to_contract(self, pcon):
        self._cur_data_context = self._data_contexts[pcon]

    def time_aligned(self):
        return  (self._cur_data_context.datetime[0] <= self.ctx_datetime  and
                self._cur_data_context.last_date <= self.ctx_datetime)
        ## 第一根是必须运行
        #return  (self._cur_data_context.datetime[0] <= self.ctx_dt_series and
                #self._cur_data_context.ctx_dt_series <= self.ctx_dt_series) or \
                #self._cur_data_context.curbar == 0 

    def switch_to_strategy(self, i, j, trading=False):
        self._trading = trading
        self._cur_data_context.i, self._cur_data_context.j  = i, j
        self._cur_strategy_context = self._strategy_contexts[i][j]

    def switch_to_data(self, i, j):
        self._cur_data_context.i, self._cur_data_context.j  = i, j

    def process_trading_events(self, append):
        self._cur_strategy_context.update_environment(self.ctx_datetime, self._ticks, self._bars)
        self._cur_strategy_context.process_trading_events(append)

    def rolling_forward(self):
        """ 更新最新tick价格，最新bar价格, 环境时间。 """
        if self._cur_data_context.last_row:
            self.ctx_dt_series.curbar = self.step
            self.ctx_dt_series.data[self.step]=(min(self._cur_data_context.last_date,
                                    self.ctx_datetime))
            self.ctx_datetime = min(self._cur_data_context.last_date, self.ctx_datetime)
            try:
                self.ctx_dt_series.data[self.step]=min(self._cur_data_context.last_date,
                                                        self.ctx_datetime)
            except IndexError:
                self.ctx_dt_series.data.append(min(self._cur_data_context.last_date,
                                                self.ctx_datetime))
            return True
        hasnext, data = self._cur_data_context.rolling_forward()
        if not hasnext:
            return False 
        self.ctx_dt_series.curbar = self.step
        try:
            self.ctx_dt_series.data[self.step]=min(self._cur_data_context.last_date, self.ctx_datetime)
        except IndexError:
            self.ctx_dt_series.data.append(min(self._cur_data_context.last_date, self.ctx_datetime))
        self.ctx_datetime = min(self._cur_data_context.last_date, self.ctx_datetime)
        return True

    def update_user_vars(self):
        """ 更新用户在策略中定义的变量, 如指标等。 """
        self._cur_data_context.update_user_vars()

    def update_system_vars(self):
        """ 更新用户在策略中定义的变量, 如指标等。 """
        self._cur_data_context.update_system_vars()
        self._ticks[self._cur_data_context.contract] = self._cur_data_context.close[0]
        self._bars[self._cur_data_context.contract] = self._cur_data_context.bar
        oldbar = self._bars.setdefault(self._cur_data_context.contract, self._cur_data_context.bar)
        if self._cur_data_context.bar.datetime > oldbar.datetime:
             # 处理不同周期时间滞后
            self._bars[self._cur_data_context.contract] = self._cur_data_context.bar

    @property
    def strategy(self):
        """ 当前策略名 """
        return self._cur_strategy_context.name

    @property
    def pcontract(self):
        """ 当前周期合约 """
        return self._cur_data_context.pcontract

    @property
    def symbol(self):
        """ 当前合约 """
        return str(self._cur_data_context.pcontract.contract)

    @property
    def curbar(self):
        """ 当前是第几根k线, 从0开始 """
        return self._cur_data_context.curbar

    @property
    def open(self):
        """ k线开盘价序列 """
        return self._cur_data_context.open

    @property
    def close(self):
        """ k线收盘价序列 """
        return self._cur_data_context.close

    @property
    def high(self):
        """ k线最高价序列 """
        return self._cur_data_context.high

    @property
    def low(self):
        """ k线最低价序列 """
        return self._cur_data_context.low

    @property
    def volume(self):
        """ k线成交量序列 """
        return self._cur_data_context.volume
    
    @property
    def datetime(self):
        """ k线时间序列 """
        if self.on_bar:
            return self.ctx_dt_series
            #return self._cur_data_context.datetime
        else:
            return self._cur_data_context.datetime

    @property
    def open_orders(self):
        """ 未成交的订单 """ 
        return list(self._cur_strategy_context.open_orders)

    def __getitem__(self, strpcon):
        """ 获取跨品种合约 """
        ## @TODO 字典，数字做key表序号
        strpcon = strpcon.upper()
        return self._data_contexts[strpcon]

    def __getattr__(self, name):
        return self._cur_data_context.get_item(name)

    def __setattr__(self, name, value):
        if name in ['_data_contexts', '_cur_data_context', '_cur_strategy_context',
                    '_strategy_contexts', 'ctx_dt_series', '_ticks', '_bars',
                    '_trading', 'on_bar', 'step', 'ctx_datetime']:
            super(Context, self).__setattr__(name, value)
        else:
            self._cur_data_context.add_item(name, value)

    def buy(self, price, quantity, symbol=None):
        """ 开多仓    
        
        Args:
            price (float): 价格, 0表市价。
            quantity (int): 数量。
            symbol (str): 合约
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能下单！')
        contract = Contract(symbol) if symbol else self._cur_data_context.contract 
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.buy(Direction.LONG, price,
                                        quantity, price_type,
                                        contract)

    def sell(self, price, quantity, symbol=None):
        """ 平多仓。
        
        Args:
           price (float): 价格, 0表市价。
           quantity (int): 数量。
           symbol (str): 合约
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能下单！')
        contract = Contract(symbol) if symbol else self._cur_data_context.contract 
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.sell(Direction.LONG, price,
                                        quantity, price_type,
                                        contract)

    def short(self, price, quantity, symbol=None):
        """ 开空仓    
        
        Args:
            price (float): 价格, 0表市价。
            quantity (int): 数量。
            symbol (str): 合约
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能下单！')
        contract = Contract(symbol) if symbol else self._cur_data_context.contract 
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.buy(Direction.SHORT, price,
                                        quantity, price_type,
                                        contract)

    def cover(self, price, quantity, symbol=None):
        """ 平空仓。
        
        Args:
           price (float): 价格, 0表市价。
           quantity (int): 数量。
           symbol (str): 合约
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能下单！')
        contract = Contract(symbol) if symbol else copy.deepcopy(self._cur_data_context.contract)
        price_type = PriceType.MKT if price == 0 else PriceType.LMT
        self._cur_strategy_context.sell(Direction.SHORT, price,
                                        quantity, price_type,
                                        contract)

    def position(self, direction='long', symbol=None):
        """ 当前仓位。
       
        Args:
            direction (str/int): 持仓方向。多头 - 'long' / 1 ；空头 - 'short'  / 2
            , 默认为多头。

            symbol (str): 字符串合约，默认为None表示主合约。
        
        Returns:
            Position. 该合约的持仓
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询当前持仓！')
        direction = Direction.arg_to_type(direction)
        contract = Contract(symbol) if symbol else self._cur_data_context.contract 
        ## @TODO assert direction
        return self._cur_strategy_context.position(contract, direction)

    def pos(self, direction='long', symbol=None):
        """  合约的当前可平仓位。
       
        Args:
            direction (str/int): 持仓方向。多头 - 'long' / 1 ；空头 - 'short'  / 2
            , 默认为多头。

            symbol (str): 字符串合约，默认为None表示主合约。
        
        Returns:
            int. 该合约的持仓数目。
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询当前持仓！')
        direction = Direction.arg_to_type(direction)
        contract = Contract(symbol) if symbol else self._cur_data_context.contract 
        ## @TODO assert direction
        return self._cur_strategy_context.pos(contract, direction)

    def cancel(self, orders):
        """ 撤单 """
        self._cur_strategy_context.cancel(orders)

    def cash(self):
        """ 现金。 """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询可用资金！')
        return self._cur_strategy_context.cash()

    def equity(self):
        """ 当前权益 """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询当前权益！')
        return self._cur_strategy_context.equity()

    def profit(self, contract=None):
        """ 当前持仓的历史盈亏 """ 
        #if not self._trading:
            #logger.warn('只有on_bar函数内能查询总盈亏！')
            #return 
        pass

    def day_profit(self, contract=None):
        """ 当前持仓的浮动盈亏 """ 
        #if not self._trading:
            #logger.warn('只有on_bar函数内能查询浮动盈亏！')
            #return 
        pass

    def test_cash(self):
        """  当根bar时间终点撮合后的可用资金，用于测试。 """
        self.process_trading_events(append=False)
        return self.cash()

