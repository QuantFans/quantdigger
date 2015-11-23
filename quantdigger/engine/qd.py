# -*- coding: utf-8 -*-
from quantdigger.engine.execute_unit import ExecuteUnit

# 系统角色
g_simulator = None
def set_pcontracts(pcons, dt_start, dt_end, window_size=0):
    """ 添加数据

    Args:
        pcons ([PContract,]): 周期合约数组

        dt_start (str): 开始时间

        dt_end (str): 结束

        window_size (int): 序列数据的窗口大小
    
    """
    global g_simulator
    g_simulator = ExecuteUnit(pcons, '2013-12-12', '2013-12-25', window_size)

def add_strategy(algos):
    """ 一个组合中的策略
    
    Args:
        algos (list): 一个策略组合
    
    """
    global g_simulator
    g_simulator.add_strategy(algos)

def run():
    g_simulator.run()


# blotter角色


# context角色


