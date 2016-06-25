from quantdigger.event.rpc import ZMQRPCServer

class KernelGate(object):
    """docstring for KernelGate"""
    def __init__(self, arg):
        self._rpcserver = ZMQRPCServer()

    def get_all_contracts(self):
        """docstring for get_all_contracts""" 
        pass

    def get_data(self, pcontract):
        """docstring for get_data""" 
        pass

    def run_strategy(self, name):
        """""" 
        return

    def run_technical(self, name):
        """docstring for run_technical""" 
        return

    def get_technicals(self):
        """docstring for get_technicals""" 
        return

    def get_strategies(self):
        """docstring for get_strategies""" 
        return
