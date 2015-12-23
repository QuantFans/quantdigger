# -*- coding: utf8 -*-
import Queue
import datetime
import copy
from quantdigger.engine import series
from quantdigger.indicators.base import IndicatorBase
from quantdigger.engine.exchange import Exchange
from quantdigger.engine.series import NumberSeries, DateTimeSeries
from quantdigger.engine.blotter import SimpleBlotter
from quantdigger.engine.event import Event, EventsPool, SignalEvent
from quantdigger.util import elogger as logger
from quantdigger.errors import TradingError
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
    def __init__(self, wrapper, window_size):
        """ window_size: 滚动窗口大小 """
        self.wrapper = wrapper
        self.series = [[{ }]]
        self.indicators = [[{ }]]
        self.variables = [[{ }]]
        data = self.wrapper.data
        self.window_size = window_size
        self.open = NumberSeries(data.open.values, self.window_size, 'open')
        self.close = NumberSeries(data.close.values, self.window_size, 'close')
        self.high = NumberSeries(data.high.values, self.window_size, 'high')
        self.low = NumberSeries(data.low.values, self.window_size, 'low')
        self.volume = NumberSeries(data.volume.values, self.window_size, 'volume')
        self.datetime = DateTimeSeries(data.index, self.window_size, 'datetime')
        self.i = -1   # 第i个组合
        self.j = -1   # 第j个策略
        self._curbar = -1
        self.bar = Bar(None, None, None, None, None, None)
        self.last_row = []
        self.last_date = datetime.datetime(2100,1,1)

    @property
    def raw_data(self):
        if series.g_rolling:
            assert(False and '逐步运算不存在历史数据')
        return self.wrapper.data

    @property
    def curbar(self):
        return self._curbar + 1

    @property
    def pcontract(self):
        return self.wrapper.pcontract

    @property
    def contract(self):
        return self.wrapper.pcontract.contract

    def update_system_vars(self):
        # 为当天数据预留空间, 改变g_window或者一次性分配
        #self.data = np.append(data, tracker.container_day)
        self._curbar = self.last_curbar
        self.open.update_curbar(self._curbar)
        self.close.update_curbar(self._curbar)
        self.high.update_curbar(self._curbar)
        self.low.update_curbar(self._curbar)
        self.volume.update_curbar(self._curbar)
        self.datetime.update_curbar(self._curbar)
        # 更新数据源
        if series.g_rolling:
            self.datetime.update(self.last_row[0])
            self.open.update(self.last_row[1])
            self.close.update(self.last_row[2])
            self.high.update(self.last_row[3])
            self.low.update(self.last_row[4])
            self.volume.update(self.last_row[5])

        self.bar = Bar(self.datetime[0], self.open[0], self.close[0],
                        self.high[0], self.low[0], self.volume[0])
        self.last_row = []
        return

    def rolling_foward(self):
        ## @todo next
        """ 
        滚动读取下一步的数据。
        """
        new_row, self.last_curbar = self.wrapper.rolling_foward()
        if not new_row:
            self.last_curbar -= 1
            return False, None
        if series.g_rolling:
            self.last_row = new_row
            self.last_date = self.last_row[0]
        else:
            self.last_row = [1] # mark
            self.last_date = self.wrapper.data.index[self.last_curbar]
        if self.datetime[0] >= self.last_date and self.curbar != 0:
            logger.error('合约[%s] 数据时间逆序或冗余' % self.pcontract)
            assert(False)
        return True, new_row

    def update_user_vars(self):
        """ 更新用户定义的变量。 """
        try:
            siter = self.series[self.i][self.j].iteritems()
        except Exception:
            pass
        else:
            for key, s in siter:
                s.update_curbar(self._curbar)
                s.duplicate_last_element()
        try:
            indic_iter = self.indicators[self.i][self.j].iteritems()
        except Exception:
            pass
        else:
            for key, indic in indic_iter:
                if indic.multi_value:
                    for key, value in indic.series.iteritems():
                        value.update_curbar(self._curbar)
                else:
                    for s in indic.series:
                        s.update_curbar(self._curbar)

    def add_series(self, key, s):
        """ 添加on_init中初始化的序列变量    
        
        Args:
            key (str): 属性名

            s (Series): 序列变量 

        """
        s.reset_data([], self.window_size + 1)
        if self.i < len(self.series):
            if self.j < len(self.series[self.i]):
                self.series[self.i][self.j][key] = s
            else:
                self.series[self.i].append({ key: s })
        else:
            self.series.append([{ key:s }])
        return

    def add_indicator(self, key, indic):
        if self.i < len(self.indicators):
            if self.j < len(self.indicators[self.i]):
                self.indicators[self.i][self.j][key] = indic
            else:
                self.indicators[self.i].append({ key: indic })
        else:
            self.indicators.append([{ key: indic }])

    def add_variable(self, key, var):
        if self.i < len(self.variables):
            if self.j < len(self.variables[self.i]):
                self.variables[self.i][self.j][key] = var
            else:
                self.variables[self.i].append({ key: var })
        else:
            self.variables.append([{ key: var }])

    def __len__(self):
        return len(self.wrapper)

    def get_item(self, name):
        """ 获取用户在策略on_init函数中初始化的变量
        
        Args:
            name (str): 变量名
        """
        try:
            return self.indicators[self.i][self.j][name]
        except KeyError:
            try:
                return self.series[self.i][self.j][name]
            except KeyError:
                return self.variables[self.i][self.j][name]
    
    def add_item(self, name, value):
        """
        添加用户初始化的变量。
        """ 
        if isinstance(value, series.SeriesBase):
            self.add_series(name, value)
        elif isinstance(value, IndicatorBase):
            self.add_indicator(name, value)
        else:
            self.add_variable(name, value)

    def __getattr__(self, name):
        return self.get_item(name)


class StrategyContext(object):
    """ 策略组合"""
    def __init__(self, name, settings={ }):
        self.events_pool = EventsPool()
        self.blotter = SimpleBlotter(name, self.events_pool, settings)
        self.exchange = Exchange(name, self.events_pool, strict=True)
        self.name = name
        self._orders = []
        self._datetime = None

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
        new_signal = False # 保证至少一次价格撮合。
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
                        logger.debug(e)
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

    def position(self, contract, direction):
        try:
            poskey = PositionKey(contract, direction) 
            return self.blotter.positions[poskey].quantity
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
    def __init__(self, data):
        self._data_contexts = { }       # str(PContract): DataContext
        for key, value in data.iteritems():
            self._data_contexts[key] = value
        self._cur_data_context = None
        self._strategy_contexts = []
        self._cur_strategy_context = None
        self.last_date = datetime.datetime(2100,1,1)
        self._ticks = { } # Contract: float
        self._bars = { }  # Contract: Bar

    def add_strategy_context(self, ctxs):
        self._strategy_contexts.append(ctxs)

    def switch_to_contract(self, pcon):
        self._cur_data_context = self._data_contexts[pcon]

    def time_aligned(self):
        return  (self._cur_data_context.datetime[0] < self.last_date or self._cur_data_context.curbar == 0)

    def switch_to_strategy(self, i, j, trading=False):
        self._trading = trading
        self._cur_data_context.i, self._cur_data_context.j  = i, j
        self._cur_strategy_context = self._strategy_contexts[i][j]

    def switch_to_data(self, i, j):
        self._cur_data_context.i, self._cur_data_context.j  = i, j

    def process_trading_events(self, append):
        self._cur_strategy_context.update_environment(self.last_date, self._ticks, self._bars)
        self._cur_strategy_context.process_trading_events(append)

    def rolling_foward(self):
        """
        更新最新tick价格，最新bar价格, 环境时间。
        """
        # 为当天数据预留空间, 改变g_window或者一次性分配
        #self.data = np.append(data, tracker.container_day)
        if self._cur_data_context.last_row:
            # 回测系统时间
            self.last_date = min(self._cur_data_context.last_date, self.last_date)
            return True
        hasnext, data = self._cur_data_context.rolling_foward()
        if not hasnext:
            return False 
        self.last_date = min(self._cur_data_context.last_date, self.last_date) # 回测系统时间
        return True

    def reset(self):
            self.last_date = datetime.datetime(2100,1,1)

    def update_user_vars(self):
        """
        更新用户在策略中定义的变量, 如指标等。
        """
        self._cur_data_context.update_user_vars()

    def update_system_vars(self):
        """
        更新用户在策略中定义的变量, 如指标等。
        """
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
        return self._cur_data_context.datetime

    def __getitem__(self, strpcon):
        """ 获取跨品种合约 """
        ## @TODO 
        #if type(strpcon) == str:
            #pass 
        #self._cur_data_context = self._data_contexts[pcon]

        ## @TODO 字典，str做key
        return self._data_contexts[strpcon]
        #tt = PContract.from_string(strpcon)
        #for key, value in self._data_contexts.iteritems():
            #if str(key) == str(tt):
                #return value

    def __getattr__(self, name):
        return self._cur_data_context.get_item(name)

    def __setattr__(self, name, value):
        if name in ['_data_contexts', '_cur_data_context', '_cur_strategy_context',
                    '_strategy_contexts', 'last_date', '_ticks', '_bars', '_trading']:
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
            return 
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
            return 
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
            return 
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
            return 
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
            int. 该合约的持仓数目。
        """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询当前持仓！')
            return 
        direction = Direction.arg_to_type(direction)
        contract = Contract(symbol) if symbol else self._cur_data_context.contract 
        ## @TODO assert direction
        return self._cur_strategy_context.position(contract, direction)

    def cash(self):
        """ 现金。 """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询可用资金！')
        return self._cur_strategy_context.cash()

    def test_cash(self):
        """  当根bar时间终点撮合后的可用资金，用于测试。 """
        self.process_trading_events(append=False)
        return self.cash()

    def equity(self):
        """ 当前权益 """
        if not self._trading:
            raise Exception('只有on_bar函数内能查询当前权益！')
            return 
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
