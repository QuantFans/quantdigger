# -*- coding: utf-8 -*-

import six
from copy import deepcopy
from collections import OrderedDict
from datetime import datetime
from quantdigger.config import settings
from quantdigger.datasource.data import DataManager
from quantdigger.engine.context import Context
from quantdigger.engine.profile import Profile
from quantdigger.util import log, MAX_DATETIME
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
        self._contexts = []
        self._data_manager = DataManager()
        if settings['source'] == 'csv':
            self.pcontracts = self._parse_pcontracts(self.pcontracts)
        self._all_data, self._max_window = self._load_data(self.pcontracts,
                                                           dt_start,
                                                           dt_end,
                                                           n,
                                                           spec_date)
        self._all_pcontracts = list(self._all_data.keys())

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
        return rst

    def add_strategies(self, settings):
        for setting in settings:
            strategy = setting['strategy']
            ctx = Context(self._all_data, strategy.name,
                          setting,  strategy, self._max_window)
            ctx.data_ref.default_pcontract = self.pcontracts[0]
            self._contexts.append(ctx)
            yield(Profile(ctx.marks, ctx.blotter, ctx.data_ref))

    def _init_strategies(self):
        for s_pcontract in self._all_pcontracts:
            for context in self._contexts:
                context.data_ref.switch_to_pcontract(s_pcontract)
                context.strategy.on_init(context)

    def run(self):
        def run_strategy(ctx, pcontract_symbols):
            for s_pcontract in self._all_pcontracts:
                ctx.data_ref.switch_to_pcontract(s_pcontract)
                ctx.strategy.on_init(ctx)

            while True:
                # Feeding data of latest.
                toremove = set()
                for s_pcontract in pcontract_symbols:
                    ctx.data_ref.switch_to_pcontract(s_pcontract)
                    has_next = ctx.data_ref.rolling_forward(
                        ctx.update_datetime)
                    if not has_next:
                        toremove.add(s_pcontract)
                if toremove:
                    for s_pcontract in toremove:
                        pcontract_symbols.remove(s_pcontract)

                # call `on_exit` of strategies
                if len(pcontract_symbols) == 0:
                    ctx.data_ref.switch_to_default_pcontract()
                    ctx.strategy.on_exit(ctx)
                    return

                for s_pcontract in pcontract_symbols:
                    ctx.data_ref.switch_to_pcontract(s_pcontract)
                    if not ctx.data_ref.datetime_aligned(ctx.aligned_dt):
                        continue
                    # Update original and derived series data
                    ctx.data_ref.update_original_vars()
                    ctx.data_ref.update_derived_vars()
                    ctx.data_ref.original.has_pending_data = False

                    # call `on_symbol` of strategies
                    ctx.on_bar = False
                    ctx.strategy.on_symbol(ctx)

                # call `on_bar` of strategies
                ctx.data_ref.switch_to_default_pcontract()
                ctx.on_bar = True
                # 确保交易状态是基于开盘时间的。
                ctx.process_trading_events(at_baropen=True)
                ctx.strategy.on_bar(ctx)
                if not settings['tick_test']:
                    # 保证有可能在当根Bar成交
                    ctx.process_trading_events(at_baropen=False)
                ctx.aligned_dt = MAX_DATETIME
                ctx.aligned_bar_index += 1

        for ctx in self._contexts:
            log.info("run strategy {0}".format(ctx.strategy_name))
            run_strategy(ctx, deepcopy(self._all_pcontracts))

    def _load_data(self, strpcons, dt_start, dt_end, n, spec_date):
        all_data = OrderedDict()
        max_window = -1
        log.info("loading data...")
        pcontracts = [PContract.from_string(s) for s in strpcons]
        pcontracts = sorted(pcontracts, key=PContract.__str__, reverse=True)
        for i, pcon in enumerate(pcontracts):
            strpcon = str(pcon)
            if strpcon in spec_date:
                dt_start = spec_date[strpcon][0]
                dt_end = spec_date[strpcon][1]
            assert(dt_start < dt_end)
            if n:
                raw_data = self._data_manager.get_last_bars(strpcon, n)
            else:
                raw_data = self._data_manager.get_bars(strpcon, dt_start, dt_end)
            if len(raw_data) == 0:
                continue
            all_data[strpcon] = raw_data
            max_window = max(max_window, len(raw_data))

        if n:
            assert(max_window <= n)
        if len(all_data) == 0:
            assert(False)
            # @TODO raise
        return all_data, max_window
