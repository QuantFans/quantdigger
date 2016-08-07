# -*- coding: utf-8 -*-
from interface import BackendInterface, UIInterface
print "import shell" 

class IpyGate(BackendInterface, UIInterface):
    """ 终端接口类，可通过它在python终端上操作界面和后台代码。 """
    def __init__(self):
        pass

    def get_all_contracts(self, pcontract):
        pass
        #"""docstring for get_all_contracts""" 
        #print "------------------" 
        #print "get-all-contracts" 
        #print pcontract
        #print "------------------" 
        #return "world" 

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
        print "plot" 


gate = IpyGate()
