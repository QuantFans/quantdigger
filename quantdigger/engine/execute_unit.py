# -*- coding: utf-8 -*-

import six
from collections import OrderedDict
from datetime import datetime
import progressbar
from quantdigger.config import settings
from quantdigger.datasource.data import DataManager
from quantdigger.engine.context import context, data_context, strategy_context
from quantdigger.engine.profile import Profile
from quantdigger.util import elogger as logger
from quantdigger.util import deprecated
from quantdigger.datastruct import PContract


class ExecuteUnit(object):
    """ 策略执行的物理单元，支持多个组合同时运行。
    """
    def __init__(self,
                 pcontracts,
                 dt_start="1980-1-1",
                 dt_end="2100-1-1",
                 n=None,
                 spec_date={}):  # 'symbol':[,]
        """
        Args:
            pcontracts (list): list of pcontracts(string)

            dt_start (datetime/str): start time of all pcontracts

            dt_end (datetime/str): end time of all pcontracts

            n (int): last n bars

            spec_date (dict): time range for specific pcontracts
        """
        self.finished_data = []
        pcontracts = list(map(lambda x: x.upper(), pcontracts))
        self.pcontracts = pcontracts
        self._combs = []
        self._data_manager = DataManager()
        # str(PContract): DataWrapper
        if settings['source'] == 'csv':
            self.pcontracts = self._parse_pcontracts(self.pcontracts)
        self._default_pcontract = self.pcontracts[0]
        self._all_data, self._max_window = self._load_data(self.pcontracts,
                                                           dt_start,
                                                           dt_end,
                                                           n,
                                                           spec_date)
        self.context = context.Context(self._all_data, self._max_window)

    def _init_strategies(self):
        for pcon, dcontext in six.iteritems(self._all_data):
            # switch context
            self.context.switch_to_pcontract(pcon)
            for i, combination in enumerate(self._combs):
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    s.on_init(self.context)

    @deprecated
    def _parse_pcontracts(self, pcontracts):
        # @TODO test
        code2strpcon, exch_period2strpcon = \
            self._data_manager.get_code2strpcon()
        rst = []
        for strpcon in pcontracts:
            strpcon = strpcon.upper()
            code = strpcon.split('.')[0]
            if code == "*":
                if strpcon == "*":  # '*'
                    for key, value in six.iteritems(exch_period2strpcon):
                        rst += value
                else:
                    # "*.xxx"
                    # "*.xxx_period"
                    k = strpcon.split('.')[1]
                    for key, value in six.iteritems(exch_period2strpcon):
                        if '-' in k:
                            if k == key:
                                rst += value
                        elif k == key.split('-')[0]:
                                rst += value
            else:
                try:
                    pcons = code2strpcon[code]
                except IndexError:
                    raise IndexError  # 本地不含该文件
                else:
                    for pcon in pcons:
                        if '-' in strpcon:
                            # "xxx.xxx_xxx.xxx"
                            if strpcon == pcon:
                                rst.append(pcon)
                        elif '.' in strpcon:
                            # "xxx.xxx"
                            if strpcon == pcon.split('-')[0]:
                                rst.append(pcon)
                        elif strpcon == pcon.split('.')[0]:
                            # "xxx"
                            rst.append(pcon)
                        #if strpcon in pcon:
                            #rst.append(strpcon)
        return rst

    def add_comb(self, comb, settings):
        """ 添加策略组合组合

        Args:
            comb (list): 一个策略组合
        """
        self._combs.append(comb)
        num_strategy = len(comb)
        if 'capital' not in settings:
            settings['capital'] = 1000000.0  # 默认资金
            logger.info('BackTesting with default capital 1000000.0.')

        assert (settings['capital'] > 0)
        if num_strategy == 1:
            settings['ratio'] = [1]
        elif num_strategy > 1 and 'ratio' not in settings:
            settings['ratio'] = [1.0/num_strategy] * num_strategy
        assert('ratio' in settings)
        assert(len(settings['ratio']) == num_strategy)
        assert(sum(settings['ratio']) - 1.0 < 0.000001)
        assert(num_strategy >= 1)
        ctxs = []
        for i, s in enumerate(comb):
            iset = {}
            if settings:
                iset = {'capital': settings['capital'] * settings['ratio'][i]}
                # logger.debug(iset)
            ctxs.append(strategy_context.StrategyContext(s.name, iset))
        self.context.add_strategy_context(ctxs)
        return Profile(ctxs,
                       self._all_data,
                       self.pcontracts[0],
                       len(self._combs)-1)

    def run(self):
        # @TODO max_window 可用来显示回测进度
        # 初始化策略自定义时间序列变量
        logger.info("runing strategies...")
        self._init_strategies()
        pbar = progressbar.ProgressBar().start()
        # todo 对单策略优化
        has_next = True
        # 遍历每个数据轮, 次数为数据的最大长度
        for pcon, data in six.iteritems(self._all_data):
            self.context.switch_to_pcontract(pcon)
            self.context.rolling_forward()
        while True:
            self.context.on_bar = False
            # 遍历数据轮的所有合约
            for pcon, data in six.iteritems(self._all_data):
                self.context.switch_to_pcontract(pcon)
                if self.context.time_aligned():
                    self.context.update_system_vars()
                    # 组合遍历
                    for i, combination in enumerate(self._combs):
                        # 策略遍历
                        for j, s in enumerate(combination):
                            self.context.switch_to_strategy(i, j)
                            self.context.update_user_vars()
                            s.on_symbol(self.context)
            # 确保单合约回测的默认值
            self.context.switch_to_pcontract(self._default_pcontract)
            self.context.on_bar = True
            # 遍历组合策略每轮数据的最后处理
            tick_test = settings['tick_test']
            for i, combination in enumerate(self._combs):
                # six.print_(self.context.ctx_datetime, "--")
                for j, s in enumerate(combination):
                    self.context.switch_to_strategy(i, j)
                    # 确保交易状态是基于开盘时间的。
                    self.context.process_trading_events(at_baropen=True)
                    s.on_bar(self.context)
                    if not tick_test:
                        # 保证有可能在当根Bar成交
                        self.context.process_trading_events(at_baropen=False)
            # six.print_(self.context.ctx_datetime)
            self.context.ctx_datetime = datetime(2100, 1, 1)
            self.context.ctx_curbar += 1
            if self.context.ctx_curbar <= self._max_window:
                pbar.update(self.context.ctx_curbar*100.0/self._max_window)
            #
            toremove = []
            for pcon, data in six.iteritems(self._all_data):
                self.context.switch_to_pcontract(pcon)
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
        pbar.finish()

    def _load_data(self, strpcons, dt_start, dt_end, n, spec_date):
        all_data = OrderedDict()
        max_window = -1
        logger.info("loading data...")
        pbar = progressbar.ProgressBar().start()
        pcontracts = [PContract.from_string(s) for s in strpcons]
        pcontracts = sorted(pcontracts, key=PContract.__str__, reverse=True)
        for i, pcon in enumerate(pcontracts):
            strpcon = str(pcon)
            if strpcon in spec_date:
                dt_start = spec_date[strpcon][0]
                dt_end = spec_date[strpcon][1]
            assert(dt_start < dt_end)
            if n:
                wrapper = self._data_manager.get_last_bars(strpcon, n)
            else:
                wrapper = self._data_manager.get_bars(strpcon, dt_start, dt_end)
            if len(wrapper) == 0:
                continue
            all_data[strpcon] = data_context.DataContext(wrapper)
            max_window = max(max_window, len(wrapper))
            pbar.update(i*100.0/len(strpcons))
            # progressbar.log('')
        if n:
            assert(max_window <= n)
        pbar.finish()
        if len(all_data) == 0:
            assert(False)
            # @TODO raise
        return all_data, max_window
