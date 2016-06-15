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

    def run_strategy(self, name, data):
        """docstring for run_strategy""" 
        pass

    def run_technical(self, name, data):
        """docstring for run_technical""" 
        pass
