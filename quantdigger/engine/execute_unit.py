# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import datetime
from quantdigger.config import settings
from quantdigger.datasource.data import DataManager
from quantdigger.engine.context import Context, DataContext, StrategyContext
from quantdigger.engine import blotter
from quantdigger.util import elogger as logger

class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个组合同时运行。
    """
    def __init__(self, pcontracts,
                       dt_start="1980-1-1",
                       dt_end="2100-1-1",
                       spec_date = { }): # 'symbol':[,]
        """ 
        Args:
            pcontracts (list): list of pcontracts(string)
            dt_start (datetime/str): start time of all pcontracts
            dt_end (datetime/str): end time of all pcontracts
            spec_date (dict): time range for specific pcontracts
        """
        self.finished_data = []
        pcontracts = map(lambda x: x.upper(), pcontracts)
        self.pcontracts = pcontracts
        self._combs = []
        # str(PContract): DataWrapper
        self._all_data, self._max_window = self._load_data(self.pcontracts, dt_start, dt_end, spec_date)
        self.context = Context(self._all_data, self._max_window)

    def _init_strategies(self):
        for pcon, dcontext in self._all_data.iteritems():
            # switch context
            self.context.switch_to_contract(pcon)
            for i, combination in enumerate(self._combs):
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    s.on_init(self.context)

    def add_comb(self, comb, settings):
        """ 添加策略组合组合
        
        Args:
            comb (list): 一个策略组合
        """
        self._combs.append(comb)
        num_strategy = len(comb) 
        if 'capital' not in settings:
            settings['capital'] = 1000000.0 # 默认资金
        assert (settings['capital'] > 0)
        if num_strategy == 1:
            settings['ratio'] = [1]
        elif num_strategy > 1 and 'ratio' not in settings:
            settings['ratio'] = [1.0/num_strategy] * num_strategy
        assert('ratio' in settings) 
        assert(len(settings['ratio']) == num_strategy)
        assert(sum(settings['ratio']) == 1)
        assert(num_strategy>=1)
        ctxs = []
        for i, s in enumerate(comb):
            iset = { }
            if settings:
                iset = { 'capital': settings['capital'] * settings['ratio'][i] }
                #logger.debug(iset)
            ctxs.append(StrategyContext(s.name, iset))
        self.context.add_strategy_context(ctxs)
        blotters = [ ctx.blotter for ctx in  ctxs]
        return blotter.Profile(blotters, self._all_data, self.pcontracts[0], len(self._combs)-1)

    def run(self):
        ## @TODO max_window 可用来显示回测进度
        # 初始化策略自定义时间序列变量
        print 'runing strategies..' 
        self._init_strategies()
        print 'on_bars..' 
        # todo 对单策略优化
        has_next = True
        tick_test = settings['tick_test']
        # 遍历每个数据轮, 次数为数据的最大长度
        for pcon, data in self._all_data.iteritems():
            self.context.switch_to_contract(pcon)
            self.context.rolling_forward()
        while True:
            self.context.on_bar = False
            # 遍历数据轮的所有合约
            for pcon, data in self._all_data.iteritems():
                self.context.switch_to_contract(pcon)
                if self.context.time_aligned():
                    self.context.update_system_vars()
                    # 组合遍历
                    for i, combination in enumerate(self._combs):
                        # 策略遍历
                        for j, s in enumerate(combination):
                            self.context.switch_to_strategy(i, j)
                            self.context.update_user_vars()
                            s.on_symbol(self.context)
            ## 确保单合约回测的默认值
            self.context.switch_to_contract(self.pcontracts[0])
            self.context.on_bar = True
            # 遍历组合策略每轮数据的最后处理
            for i, combination in enumerate(self._combs):
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j, True)
                    self.context.process_trading_events(append=True)
                    s.on_bar(self.context)
                    if not tick_test:
                        # 保证有可能在当根Bar成交
                        self.context.process_trading_events(append=False)
            #print self.context.ctx_datetime
            self.context.ctx_datetime = datetime(2100,1,1)
            self.context.step += 1
            # 
            toremove = []
            for pcon, data in self._all_data.iteritems():
                self.context.switch_to_contract(pcon)
                has_next = self.context.rolling_forward()
                if not has_next:
                    toremove.append(pcon)
            if toremove:
                for key in toremove:
                    del self._all_data[key]
                if len(self._all_data) == 0:
                    # 策略退出后的处理
                    for i, combination in enumerate(self._combs):
                        for j, s in enumerate(combination):
                            self.context.switch_to_strategy(i, j)
                            s.on_exit(self.context)
                    return
            #print "*********" 

    def _load_data(self, pcontracts, dt_start, dt_end, spec_date):
        all_data = OrderedDict()     
        self._data_manager = DataManager()
        max_window = -1
        for pcon in pcontracts:
            if pcon in spec_date:
                dt_start = spec_date[pcon][0]
                dt_end = spec_date[pcon][1]
            assert(dt_start < dt_end)
            wrapper = self._data_manager.get_bars(pcon, dt_start, dt_end)
            all_data[pcon] = DataContext(wrapper)
            max_window = max(max_window, len(wrapper))
        return all_data, max_window
