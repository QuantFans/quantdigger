# -*- coding: utf-8 -*-
from quantdigger.engine.execute_unit import ExecuteUnit
import datetime
from quantdigger.engine.series import NumberSeries, DateTimeSeries
from quantdigger.indicators.common import *
from quantdigger.datastruct import PContract

# 系统角色
g_simulator = None
def set_symbols(pcons, window_size,
                    dt_start=datetime.datetime(1980,1,1),
                    dt_end=datetime.datetime(2100,1,1)):
    """ 添加数据

    Args:
        pcons ([str,]): 周期合约数组

        dt_start (str): 开始时间

        dt_end (str): 结束

        window_size (int): 序列数据的窗口大小
    
    """
    global g_simulator
    new_pcons = []
    for pcon in pcons:
        new_pcons.append(PContract.from_string(pcon))
    g_simulator = ExecuteUnit(new_pcons, window_size, dt_start, dt_end)
    return g_simulator

def add_strategy(algos, settings = { }):
    """ 一个组合中的策略
    
    Args:
        algos (list): 一个策略组合
    
    Returns:
        Profile. 组合结果
    """
    return g_simulator.add_comb(algos, settings)

def run():
    g_simulator.run()

def buy(direction, price, quantity, price_type='LMT', contract=None):
    """ 开仓    
    
    Args:
        direction (str/int): 下单方向。多头 - 'long' / 1 ；空头 - 'short'  / 2

        price (float): 价格。

        quantity (int): 数量。

        price_type (str/int): 下单价格类型。限价单 - 'lmt' / 1；市价单 - 'mkt' / 2
    """
    g_simulator.context.buy(direction, price, quantity, price_type, contract)
    #print g_simulator._context.trading_context.name

def sell(direction, price, quantity, price_type='MKT', contract=None):
    """ 平仓。
    
    Args:
       direction (str/int): 下单方向。多头 - 'long' / 1 ；空头 - 'short'  / 2

       price (float): 价格。

       quantity (int): 数量。

       price_type (str/int): 下单价格类型。限价单 - 'lmt' / 1；市价单 - 'mkt' / 2
    """
    g_simulator.context.sell(direction, price, quantity, price_type, contract)

def position(contract=None):
    """ 当前仓位。
   
    Args:
        contract (str): 字符串合约，默认为None表示主合约。
    
    Returns:
        int. 该合约的持仓数目。
    """
    pass

def cash():
    """ 现金。 """
    pass

def equity():
    """ 当前权益 """
    pass

def profit(contract=None):
    """ 当前持仓的历史盈亏 """ 
    pass

def day_profit(contract=None):
    """ 当前持仓的浮动盈亏 """ 
    pass

class Strategy(object):
    """ 策略基类"""
    def __init__(self, name):
        self.name = name
    
    def on_init(self, ctx):
        """初始化数据""" 
        return

    def on_bar(self, ctx):
        return

    def on_final(self, ctx):
        # 停在最后一个合约处
        return

    def on_exit(self, ctx):
        # 停在最后一根bar
        return

#__all__ = ['set_symbols', 'add_strategy', 'run', 'buy', 'sell',
        #'position', 'cash', 'equity', 'profit', 'day_profit', 'Strategy']
