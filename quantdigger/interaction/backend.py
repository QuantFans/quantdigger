# -*- coding: utf-8 -*-
##
# @file backend.py
# @brief 
# @author wondereamer
# @version 0.5
# @date 2016-07-10


from quantdigger.event.rpc import EventRPCServer
from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.interaction.interface import BackendInterface
from quantdigger.util import mlogger as log
from quantdigger.datasource.data import DataManager
from quantdigger.datastruct import Contract, PContract
from quantdigger.interaction.serialize import (
    serialize_pcontract_bars,
    serialize_all_pcontracts,
    serialize_all_contracts,
)


class Backend(BackendInterface):
    ## @TODO singleton
    SERVER_FOR_UI = 'backend4ui' 
    SERVER_FOR_SHELL = "backend4shell" 
    def __init__(self):
        log.info("Init Backend..")
        self._dm = DataManager()
        self._engine = ZMQEventEngine('Backend')
        self._engine.start()

        self._shell_srv = EventRPCServer(self._engine, 
                                self.SERVER_FOR_SHELL)
        self._ui_srv = EventRPCServer(self._engine, 
                                self.SERVER_FOR_UI)
        self.register_functions(self._shell_srv)
        self.register_functions(self._ui_srv)

    def register_functions(self, server):
        server.register('get_all_contracts', self.get_all_contracts)
        server.register('get_all_pcontracts', self.get_all_pcontracts)
        server.register('get_pcontract', self.get_pcontract)
        server.register('get_strategies', self.get_strategies)
        server.register('run_strategy', self.run_strategy)
        server.register('run_technical', self.run_technical)

    def stop(self):
        log.info('Backend stopped.')
        self._engine.stop()

    def get_all_contracts(self):
        def _mk_contract(code, exchage):
            s = '%s.%s' % (code, exchage)
            return Contract(s)
        # 模拟接口
        df = self._dm.get_contracts()
        contracts = [str(_mk_contract(row['code'], row['exchange'])) for _, row in df.iterrows()]
        return serialize_all_contracts(contracts)
        #data = ['CC.SHFE-1.MINUTE', 'BB.SHFE-1.MINUTE']
        #pcons =  [PContract.from_string(d) for d in data]
        #contracts =  [pcon.contract for pcon in pcons]
        #return serialize_all_contracts(contracts)

    def get_all_pcontracts(self):
        # 模拟接口
        data = ['CC.SHFE-1.MINUTE', 'BB.SHFE-1.MINUTE']
        pcontracts =  [PContract.from_string(d) for d in data]
        return serialize_all_pcontracts(pcontracts)

    def get_pcontract(self, str_pcontract):
        da = self._dm.get_bars(str_pcontract)
        return serialize_pcontract_bars(str_pcontract, da.data)

    def run_strategy(self, name):
        """""" 
        return

    def run_technical(self, name):
        return

    def get_technicals(self):
        """ 获取系统的所有指标。 """
        from quantdigger.technicals import get_techs
        return get_techs()

    def get_strategies(self):
        return 'hello' 

#backend.get_all_contracts()
#backend.get_pcontract('BB.TEST-1.MINUTE')


if __name__ == '__main__':
    backend = Backend()
    import time, sys
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend.stop()
        sys.exit(0)
