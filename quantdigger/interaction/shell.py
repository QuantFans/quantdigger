# -*- coding: utf-8 -*-

from quantdigger.event.rpc import EventRPCClient
from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.interaction import (
    Backend,
    WindowGate,
)
from quantdigger.util import mlogger as log


class Shell:
    """ 终端接口类，可通过它在python终端上操作界面和后台代码。 """
    def __init__(self):
        log.info("Init Shell..")
        self._engine = ZMQEventEngine('Shell')
        self._engine.start()
        self.gate = EventRPCClient('Shell',
                                   self._engine,
                                   WindowGate.SERVER_FOR_SHELL)

        self._backend = EventRPCClient('test_shell',
                                       self._engine,
                                       Backend.SERVER_FOR_SHELL)

    def get_all_pcontracts(self):
        pass

    def get_all_contracts(self):
        ret = self._backend.sync_call("get_all_contracts")
        print(ret)

    def show_data(self, strpcontract):
        return self.gate.sync_call("show_data", {
            'pcontract': strpcontract
        })

    def get_pcontract(self, pcontract):
        """docstring for get_data"""
        pass

    def run_strategy(self, name):
        """"""
        return

    def run_technical(self, name):
        return

    def get_technicals(self):
        """ 获取系统的所有指标。 """
        return

    def get_strategies(self):
        return 'hello'

    def plot(self):
        """docstring for plo"""
        print("plot")


shell = Shell()
