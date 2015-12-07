# -*- coding: utf-8 -*-
from datetime import datetime
from quantdigger.datasource.data import data_manager
#from quantdigger.errors import DataAlignError
from quantdigger.engine.context import Context, DataContext, StrategyContext
from quantdigger.engine import series

class Profile(object):
    """ 组合结果 """
    def __init__(self, blotters, dcontexts, pcon, i):
        self._blts = blotters # 组合内所有策略的blotter
        self._dcontextss = dcontexts   # 所有数据上下文
        self.i = i   # 对应于第几个组合
        self._main_pcontract = pcon

    def transactions(self, j):
        return self._blts[j].transactions

    def all_holdings(self, j):
        return self._blts[j].all_holdings

    def positions(self, j):
        return self._blts[j].current_positions

    def holdings(self, j):
        return self._blts[j].current_holdings

    def indicators(self, j, pcon=None):
        """ 返回当前组合中某个策略的指标
        
        Args:
            j (int): 第j个策略

            pcon (PContract): 周期合约
        
        Returns:
            dict. 指标名和指标
        Raises:
        """
        pcon = pcon if pcon else self._main_pcontract
        return self._dcontextss[pcon].indicators[self.i][j]

    def data(self, pcon=None):
        pcon = pcon if pcon else self._main_pcontract
        return self._dcontextss[pcon].raw_data

    def signals(self, j):
        """ 交易信号对 """ 
        from quantdigger.digger import deals
        positions = {}
        signals = [] 
        for trans in self.transactions(j):
            deals.update_positions(positions, signals, trans);
        return signals
    

class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个策略同时运行。
        每个执行单元都可能跟踪多个数据(策略用到的周期合约数据集合)。
        其中第一个合约为"主合约" 。 每个执行器可加载多个策略,只要数据需求不超过pcontracts。

        :ivar dt_begin: 策略执行的时间起点。
        :ivar dt_end: 策略执行的时间终点。
        :ivar pcontracts: 策略用到的周期合约数据集合。
        :ivar _strategies: 策略集合。
        :ivar datasource: 数据源。

    """
    def __init__(self, pcontracts, window_size=0, dt_start=datetime(1980,1,1),
                 dt_end=datetime(2100,1,1)):
        series.g_rolling = False if window_size == 0 else True
        series.g_window = window_size
        self.dt_start = dt_start
        self.dt_end = dt_end
        self._window_size = window_size
        self.bars = { }     # PContract -> DataWrapper
        self.ticks = { }
        self.pcontracts = pcontracts
        self._combs = []
        for pcon in pcontracts:
            self.load_data(pcon, dt_start, dt_end)
            self.ticks[pcon.contract] = 0
        self.context = Context(self.bars, self.ticks)

    def _init_strategies(self):
        for pcon, dcontext in self.bars.iteritems():
            # switch context
            self.context.switch_to_contract(pcon)
            for i, combination in enumerate(self._combs):
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    s.on_init(self.context)

    def add_comb(self, comb):
        """ 添加策略组合组合
        
        Args:
            comb (list): 一个策略组合
        """
        self._combs.append(comb)
        ctxs = [StrategyContext(s.name, None) for s in comb]
        self.context.add_strategy_context(ctxs)
        blotters = [ ctx.blotter for ctx in  ctxs]
        return Profile(blotters, self.bars, self.pcontracts[0], len(self._combs)-1)

    def run(self):
        # 初始化策略自定义时间序列变量
        print 'runing strategies..' 
        self._init_strategies()
        print 'on_bars..' 
        # todo 对单策略优化
        has_next = True
        while True:
            for pcon, data in self.bars.iteritems():
                ## @todo 时间对齐
                self.context.switch_to_contract(pcon)
                has_next = self.context.rolling_foward()
                if not has_next:
                    return
            #print "-------------" 
            # 组合遍历
            for i, combination in enumerate(self._combs):
                # 合约遍历
                for pcon, data in self.bars.iteritems():
                    self.context.switch_to_contract(pcon)
                    # 原子策略遍历
                    for j, s in enumerate(combination):
                        self.context.switch_to_strategy(i, j)
                        self.context.update_strategy_context(i, j)
                        self.context.update_user_vars()
                        s.on_bar(self.context)
                # 原子策略遍历
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    s.on_final(self.context)
                    self.context.process_signals()
                    
                # 
            for s in self._combs:
                # on_cycle
                pass

    def run2(self):
        """""" 
        print 'running...'
        bar_index = 0
        while bar_index < self._data_length:
            #
            latest_bars = { }
            try:
                # 在回测中无需MARKET事件。
                # 这样可以加速回测速度。
                for algo in self._combs:
                    bar = algo.update_curbar(bar_index)
                    algo.exchange.update_datetime(bar.datetime)
                    algo.blotter.update_datetime(bar.datetime)
                    latest_bars[algo._main_contract] = bar
                    algo.blotter.update_bar(latest_bars)
                    #algo.exchange.make_market(bar)
                    # 对新的价格运行算法。
                    algo.execute_strategy()
                    while True:
                       # 事件处理。 
                        try:
                            event = algo.events_pool.get()
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
                                    algo.blotter.update_signal(event)

                                elif event.type == Event.ORDER:
                                    algo.exchange.insert_order(event)

                                elif event.type == Event.FILL:
                                    # 模拟交易接口收到报单成交
                                    algo.blotter.api.on_transaction(event)
                        # 价格撮合。note: bar价格撮合要求撮合置于运算后面。
                        algo.exchange.make_market(bar)

            except Exception, e:
                print(e)
                raise
            bar_index += 1

    def load_data(self, pcontract, dt_start=datetime(1980,1,1), dt_end=datetime(2100,1,1)):
        """ 加载周期合约数据
        
        Args:
            pcontract (PContract): 周期合约

            dt_start(datetime): 开始时间

            dt_end(datetime): 结束时间

        Returns:
            pd.DataFrame. k线数据
        """
        try:
            return self.bars[str(pcontract)]
        except KeyError:
            ## @todo 时间对齐，长度确认
            data = data_manager.load_bars(pcontract, dt_start, self.dt_end, self._window_size)
            self.bars[pcontract] = DataContext(data, self._window_size)
            self._data_length = len(data)
            return data

