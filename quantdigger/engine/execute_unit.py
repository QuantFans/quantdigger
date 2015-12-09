# -*- coding: utf-8 -*-
from datetime import datetime
from quantdigger.datasource.data import data_manager
from quantdigger.engine.context import Context, DataContext, StrategyContext
from quantdigger.engine import series, blotter
from quantdigger.util import elogger as logger

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
        self.all_data = { }     # PContract -> DataWrapper
        self.ticks = { }
        self.pcontracts = pcontracts
        self._combs = []
        self._window_size = window_size
        for pcon in pcontracts:
            self.load_data(pcon, dt_start, dt_end)
            self.ticks[pcon.contract] = 0
        self.context = Context(self.all_data, self.ticks)

    def _init_strategies(self):
        for pcon, dcontext in self.all_data.iteritems():
            # switch context
            self.context.switch_to_contract(pcon)
            for i, combination in enumerate(self._combs):
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    s.on_init(self.context)

    def add_comb(self, comb, settings = { }):
        """ 添加策略组合组合
        
        Args:
            comb (list): 一个策略组合
        """
        self._combs.append(comb)
        if settings:
            num_strategy = len(comb) 
            assert (settings['captial'] > 0)
            assert len(settings['ratio']) == num_strategy
            assert(sum(settings['ratio']) == 1)
        ctxs = []
        for i, s in enumerate(comb):
            iset = { }
            if settings:
                iset = { 'captial': settings['captial'] * settings['ratio'][i] }
                logger.debug(iset)
            ctxs.append(StrategyContext(s.name, iset))
        self.context.add_strategy_context(ctxs)
        blotters = [ ctx.blotter for ctx in  ctxs]
        return blotter.Profile(blotters, self.all_data, self.pcontracts[0], len(self._combs)-1)

    def run(self):
        # 初始化策略自定义时间序列变量
        print 'runing strategies..' 
        self._init_strategies()
        print 'on_bars..' 
        # todo 对单策略优化
        has_next = True
        # 遍历每个数据轮, 次数为数据的最大长度
        while True:
            for pcon, data in self.all_data.iteritems():
                ## @todo 时间对齐
                self.context.switch_to_contract(pcon)
                has_next = self.context.rolling_foward()
                if not has_next:
                    # 策略退出后的处理
                    for i, combination in enumerate(self._combs):
                        for j, s in enumerate(combination):
                            self.context.switch_to_strategy(i, j)
                            s.on_exit(self.context)
                    return
            # 组合遍历
            for i, combination in enumerate(self._combs):
                # 遍历数据轮的所有合约
                for pcon, data in self.all_data.iteritems():
                    self.context.switch_to_contract(pcon)
                    # 原子策略遍历
                    for j, s in enumerate(combination):
                        self.context.switch_to_strategy(i, j)
                        self.context.update_strategy_context(i, j)
                        self.context.update_user_vars()
                        s.on_bar(self.context)
                # 每轮数据的最后处理
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    s.on_final(self.context)
                    self.context.process_signals()
                    
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
            return self.all_data[str(pcontract)]
        except KeyError:
            ## @todo 时间对齐，长度确认
            data = data_manager.load_bars(pcontract, dt_start, self.dt_end, self._window_size)
            self.all_data[pcontract] = DataContext(data, self._window_size)
            self._data_length = len(data)
            return data

