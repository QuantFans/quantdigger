# -*- coding: utf-8 -*-
from quantdigger.engine.execute_unit import ExecuteUnit

# 系统角色


def add_strategies(symbols, strategies):
    """ 一个组合中的策略

    Args:
        algos (list): 一个策略组合

    Returns:
        Profile. 组合结果
    """
    simulator = ExecuteUnit(symbols, "1980-1-1", "2100-1-1", None, {})
    profiles = list(simulator.add_strategies(strategies))
    simulator.run()

    return profiles


class Strategy(object):
    """ 策略基类"""
    def __init__(self, name):
        self.name = name

    def on_init(self, ctx):
        """初始化数据"""
        return

    def on_symbol_init(self, ctx):
        """初始化数据"""
        return

    def on_symbol_step(self, ctx):
        """ 逐合约逐根k线运行 """
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

__all__ = ['add_strategies', 'Strategy']
