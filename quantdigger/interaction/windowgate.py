# -*- coding: utf-8 -*-
##
# @file windowgate.py
# @brief
# @author wondereamer
# @version 0.5
# @date 2016-07-10

from quantdigger.datastruct import PContract
from quantdigger.event.rpc import EventRPCClient, EventRPCServer
from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.util import gen_logger as log
from quantdigger.interaction.backend import Backend

from quantdigger.interaction.serialize import (
    deserialize_all_pcontracts,
    deserialize_all_contracts,
    deserialize_pcontract_bars
)


class WindowGate:
    SERVER_FOR_SHELL = "ui4shell"

    def __init__(self, widget):
        log.info("Init WindowGate..")
        self._engine = ZMQEventEngine('WindowGate')
        self._engine.start()
        self._backend = EventRPCClient('WindowGate', self._engine, Backend.SERVER_FOR_UI)
        self._shell_srv = EventRPCServer(self._engine, self.SERVER_FOR_SHELL)
        self._register_functions(self._shell_srv)
        self._period = None
        self._contract = None
        self._widget = widget

    def _register_functions(self, server):
        server.register('get_all_contracts', self.get_all_contracts)
        server.register('get_all_pcontracts', self.get_all_pcontracts)
        server.register('get_pcontract', self.get_pcontract)
        server.register('show_data', self.show_data)

    def add_widget(self, ith, type_):
        self._widget.add_widget

    def add_technical(self, ith, technical):
        """"""
        # @TODO compute technical with backend,
        # display result from backend
        return

    @property
    def pcontract(self):
        return PContract(self._contract, self._period)

    def stop(self):
        self._engine.stop()

    def get_all_contracts(self):
        ret = self._backend.sync_call('get_all_contracts')
        return deserialize_all_contracts(ret)

    def get_all_pcontracts(self):
        ret = self._backend.sync_call('get_all_pcontracts')
        return deserialize_all_pcontracts(ret)

    def get_pcontract(self, str_pcontract):
        ret = self._backend.sync_call('get_pcontract', {
            'str_pcontract': str_pcontract
        })
        return deserialize_pcontract_bars(ret)

    def run_strategy(self, name):
        """"""
        return

    def run_technical(self, name):
        return

    def get_technicals(self):
        """ 获取系统的所有指标。 """
        return

    def get_strategies(self):
        """ 获取系统的所有策略。 """
        return

    def show_data(self, pcontract):
        self._widget.show_data(pcontract)
