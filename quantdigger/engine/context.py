# -*- coding: utf8 -*-
import Queue
from quantdigger.engine import series
from series import NumberSeries, DateTimeSeries
from quantdigger.indicators.base import IndicatorBase
from quantdigger.engine.exchange import Exchange
from quantdigger.engine.event import SignalEvent
#from quantdigger.util import engine_logger as logger
from quantdigger.engine.blotter import SimpleBlotter
from quantdigger.engine.event import EventsPool
from quantdigger.engine.event import Event
from quantdigger.datastruct import (
    Order,
    TradeSide,
    Direction,
    PriceType,
    Bar
)


class DataContext(object):
    def __init__(self, wrapper, window_size):
        """ window_size: 滚动窗口大小 """
        self.wrapper = wrapper
        self.window_size = window_size
        self.series = [[{ }]]
        self.indicators = [[{ }]]
        self.variables = [[{ }]]
        data = self.wrapper.data
        if window_size == 0:
            self.window_size = len(data)
        self.open = NumberSeries(data.open.values, self.window_size, 'open')
        self.close = NumberSeries(data.close.values, self.window_size, 'close')
        self.high = NumberSeries(data.high.values, self.window_size, 'high')
        self.low = NumberSeries(data.low.values, self.window_size, 'low')
        self.volume = NumberSeries(data.volume.values, self.window_size, 'volume')
        self.datetime = DateTimeSeries(data.index, self.window_size, 'datetime')
        self.i = -1   # 第i个组合
        self.j = -1   # 第j个策略
        self.curbar = 0
        self.bar = Bar(None, None, None, None, None, None)

    @property
    def raw_data(self):
        return self.wrapper.data

    @property
    def pcontract(self):
        return self.wrapper.pcontract

    @property
    def contract(self):
        return self.wrapper.pcontract.contract

    def rolling_foward(self):
        ## @todo next
        """ 
        滚动读取下一步的数据。
        """
        new_row, self.curbar  = self.wrapper.rolling_foward()
        if not new_row:
            return False

        # 为当天数据预留空间, 改变g_window或者一次性分配
        #self.data = np.append(data, tracker.container_day)
        self.open.update_curbar(self.curbar)
        self.close.update_curbar(self.curbar)
        self.high.update_curbar(self.curbar)
        self.low.update_curbar(self.curbar)
        self.volume.update_curbar(self.curbar)
        self.datetime.update_curbar(self.curbar)
        # 更新数据源
        if series.g_rolling:
            self.datetime.update(new_row[0])
            self.open.update(new_row[1])
            self.close.update(new_row[2])
            self.high.update(new_row[3])
            self.low.update(new_row[4])
            self.volume.update(new_row[5])

        self.bar.datetime = self.datetime[0]
        self.bar.open = self.open[0]
        self.bar.close = self.close[0]
        self.bar.high = self.high[0]
        self.bar.low = self.low[0]
        self.bar.volume = self.volume[0]
        return True

    def update_user_vars(self):
        """ 更新用户定义的变量。 """
        try:
            siter = self.series[self.i][self.j].iteritems()
        except Exception:
            pass
        else:
            for key, s in siter:
                s.update_curbar(self.curbar)
                s.duplicate_last_element()
        try:
            indic_iter = self.indicators[self.i][self.j].iteritems()
        except Exception:
            pass
        else:
            for key, indic in indic_iter:
                if indic.multi_value:
                    for key, value in indic.series.iteritems():
                        value.update_curbar(self.curbar)
                else:
                    for s in indic.series:
                        s.update_curbar(self.curbar)

    def add_series(self, key, s):
        """ 添加on_init中初始化的序列变量    
        
        Args:
            key (str): 属性名

            s (Series): 序列变量 

        """
        s.reset_data([], self.window_size+series.g_window)
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
    def __init__(self, name, settings=None):
        self.events_pool = EventsPool()
        self.blotter = SimpleBlotter(None, self.events_pool)
        self.exchange = Exchange(self.events_pool, strict=False)
        self.name = name
        self._orders = []
        self._datetime = None

    def update(self, dt, ticks):
        """ 更新模拟交易所和订单管理器的环境。
        
        Args:
            dt (datetime): 时间戳

            ticks (dict): 所有订阅合约的最新价格
        
        """
        self.exchange.update_datetime(dt)
        self.blotter.update_datetime(dt)
        self.blotter.update_ticks(ticks)
        self._datetime = dt
        return

    def process_signals(self, latest_bar):
        # 一次策略循环可能产生多个委托单。
        if self._orders:
            self.events_pool.put(SignalEvent(self._orders))
        self._orders = []
        while True:
           # 事件处理。 
            try:
                event = self.events_pool.get()
            except Queue.Empty:
                break
            except IndexError:
                break
            else:
                if event is not None:
                    #if event.type == 'MARKET':
                        #strategy.calculate_signals(event)
                        #port.update_timeindex(event)
                    if event.type == Event.SIGNAL:
                        self.blotter.update_signal(event)

                    elif event.type == Event.ORDER:
                        self.exchange.insert_order(event)

                    elif event.type == Event.FILL:
                        # 模拟交易接口收到报单成交
                        self.blotter.api.on_transaction(event)
            # 价格撮合。note: bar价格撮合要求撮合置于运算后面。
            self.exchange.make_market(latest_bar)


    def buy(self, direction, price, quantity, price_type, contract):
        """ 开仓    
        
        Args:
            direction (str/int): 下单方向。多头 - 'long' / 1 ；空头 - 'short'  / 2

            price (float): 价格。

            quantity (int): 数量。

            price_type (str/int): 下单价格类型。限价单 - 'lmt' / 1；市价单 - 'mkt' / 2

            contract (Contract): 合约
        """
        self._orders.append(Order(
                ## @todo 时间放到blotter中设置
                self._datetime,
                contract,
                PriceType.arg_to_type(price_type),
                TradeSide.KAI,
                Direction.arg_to_type(direction),
                float(price),
                quantity
        ))

    def sell(self, direction, price, quantity, price_type, contract):
        """ 平仓。
        
        Args:
           direction (str/int): 下单方向。多头 - 'long' / 1 ；空头 - 'short'  / 2

           price (float): 价格。

           quantity (int): 数量。

           price_type (str/int): 下单价格类型。限价单 - 'lmt' / 1；市价单 - 'mkt' / 2

           contract (Contract): 合约
        """
        self._orders.append(Order(
                self._datetime,
                contract,
                PriceType.arg_to_type(price_type),
                TradeSide.PING,
                Direction.arg_to_type(direction),
                float(price),
                quantity
        ))

    def position(self, contract):
        """ 当前仓位。
       
        Args:
            contract (Contract): 字符串合约，默认为None表示主合约。
        
        Returns:
            int. 该合约的持仓数目。
        """
        try:
            return self.blotter.current_positions[contract].quantity
        except KeyError:
            return 0

    def cash(self):
        """ 现金。 """
        return self.blotter.current_holdings['cash']

    def equity(self):
        """ 当前权益 """
        return self.blotter.current_holdings['equity']

    def profit(self, contract):
        """ 当前持仓的历史盈亏 """ 
        pass

    def day_profit(self, contract):
        """ 当前持仓的浮动盈亏 """ 
        pass


class Context(object):
    """ 上下文"""
    def __init__(self, bars, ticks):
        self._bars = bars     # str(PContract) -> DataWrapper
        self._bar_context = None
        self._strategy_context = None
        self._all_strategy_context = []
        self._datetime = None  # 全局时间
        self._ticks = ticks

    def add_strategy_context(self, ctxs):
        self._all_strategy_context.append(ctxs)

    def switch_to_contract(self, pcon):
        self._bar_context = self._bars[pcon]

    def switch_to_strategy(self, i, j):
        self._bar_context.i, self._bar_context.j  = i, j
        self._strategy_context = self._all_strategy_context[i][j]

    def update_strategy_context(self, i, j):
        self._strategy_context.update(self._datetime, self._ticks)

    def process_signals(self):
        self._strategy_context.process_signals(self._bar_context.bar)

    def rolling_foward(self):
        """
        更新当前bar上下文，最新tick价格，环境时间。
        """
        # 为当天数据预留空间, 改变g_window或者一次性分配
        #self.data = np.append(data, tracker.container_day)
        data = self._bar_context.rolling_foward()
        ## @todo 时间格式优化
        self._datetime = self._bar_context.datetime[0] 
        self._ticks[self._bar_context.contract] = self._bar_context.close[0]
        return data
        
    def update_user_vars(self):
        """
        更新用户在策略中定义的变量, 如指标等。
        """
        self._bar_context.update_user_vars()

    @property
    def curbar(self):
        return self._bar_context.curbar + 1

    @property
    def open(self):
        return self._bar_context.open

    @property
    def close(self):
        return self._bar_context.close

    @property
    def high(self):
        return self._bar_context.high

    @property
    def low(self):
        return self._bar_context.low

    @property
    def volume(self):
        return self._bar_context.volume
    
    @property
    def datetime(self):
        return self._bar_context.datetime

    def __getitem__(self, strpcon):
        """ 获取跨品种合约 """
        return self._bars[strpcon]

    def __getattr__(self, name):
        return self._bar_context.get_item(name)

    def __setattr__(self, name, value):
        if name in ['_bars', '_bar_context', '_strategy_context',
                    '_all_strategy_context', '_datetime', '_ticks']:
            super(Context, self).__setattr__(name, value)
        else:
            self._bar_context.add_item(name, value)

    def buy(self, direction, price, quantity, price_type='LMT', contract=None):
        ## @todo 判断是否在on_final中运行，是的话不允许默认值。
        contract = contract if contract else self._bar_context.contract 
        self._strategy_context.buy(direction, price, quantity, price_type, contract)

    def sell(self, direction, price, quantity, price_type='MKT', contract=None):
        contract = contract if contract else self._bar_context.contract 
        self._strategy_context.sell(direction, price, quantity, price_type, contract)

    def position(self, contract=None):
        contract = contract if contract else self._bar_context.contract 
        return self._strategy_context.position(contract)

    def cash(self):
        return self._strategy_context.cash()

    def equity(self):
        return self._strategy_context.equity()

    def profit(self, contract=None):
        pass

    def day_profit(self, contract=None):
        pass
