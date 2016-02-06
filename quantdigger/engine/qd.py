# -*- coding: utf-8 -*-
from quantdigger.engine.execute_unit import ExecuteUnit

# 系统角色
_simulator = None
def set_symbols(pcontracts, dt_start="1980-1-1",
                       dt_end="2100-1-1",
                       n=None,
                       spec_date = { }): # 'symbol':[,]
    """ 
    Args:
        pcontracts (list): list of pcontracts(string)
        dt_start (datetime/str): start time of all pcontracts
        dt_end (datetime/str): end time of all pcontracts
        n (int): last n bars
        spec_date (dict): time range for specific pcontracts
    """
    global _simulator
    _simulator = ExecuteUnit(pcontracts, dt_start, dt_end, n, spec_date)
    return _simulator

def add_strategy(algos, settings = { }):
    """ 一个组合中的策略
    
    Args:
        algos (list): 一个策略组合
    
    Returns:
        Profile. 组合结果
    """
    rst = _simulator.add_comb(algos, settings)
    ## @TODO 为什么去掉测试test_engine_vector.py无法通过 
    settings.clear()
    return rst

def run():
    _simulator.run()

class Strategy(object):
    """ 策略基类"""
    def __init__(self, name):
        self.name = name
    
    def on_init(self, ctx):
        """初始化数据""" 
        return

    def on_symbol(self, ctx):
        """ 逐合约逐根k线运行 """
        return

    def on_bar(self, ctx):
        """ 逐根k线运行 """
        # 停在最后一个合约处
        return

    def on_exit(self, ctx):
        """ 策略结束前运行 """
        # 停在最后一根bar
        return

__all__ = ['set_symbols', 'add_strategy', 'run', 'Strategy']
