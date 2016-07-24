# -*- coding: utf-8 -*-
from quantdigger.event.rpc import EventRPCServer, EventRPCClient
from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.util import mlogger as log
from interface import BackendInterface

    

class Backend(BackendInterface):
    def __init__(self):
        log.info("Init Backend")
        self._engine = ZMQEventEngine('Backend')
        self._engine.start()

        self._ipy_srv = EventRPCServer(self._engine, 'backend4ipython')
        self._ui_srv = EventRPCServer(self._engine, 'backend4ui')
        self.register_functions(self._ipy_srv)
        self.register_functions(self._ui_srv)

    def register_functions(self, server):
        server.register('get_all_contracts', self.get_all_contracts)
        server.register('get_pcontract', self.get_pcontract)
        server.register('get_strategies', self.get_strategies)
        server.register('run_strategy', self.run_strategy)
        server.register('run_technical', self.run_technical)

    def stop(self):
        log.info('Backend stopped.')
        self._engine.stop()

    def get_all_contracts(self):
        return "get_all_contracts from backend" 

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

gate = Backend()

def test_backend():
    """""" 
    import time, sys
    client = EventRPCClient(gate._engine, 'backend4ui')
    ipy_client = EventRPCClient(gate._engine, 'backend4ipython')
    for i in xrange(0, 5):
        print "sync_call: print_hello "
        print "ui_client return: ", client.sync_call("get_all_contracts")
        print "ipy_client return: ", ipy_client.sync_call("get_strategies")
        time.sleep(1)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gate.stop()
        sys.exit(0)

#if __name__ == '__main__':
    #test_backend()

if __name__ == '__main__':
    import time, sys
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gate.stop()
        sys.exit(0)
