# -*- coding: utf-8 -*-
##
# @file data.py
# @brief 数据控制模块
# @author skabyy
# @version 0.3
# @date 2016-05-26

from dsUtil import get_setting_datasource
from quantdigger.datastruct import PContract, Contract


class DataManager(object):
    """
    数据代理
    """
    def __init__(self):
        self._src = get_setting_datasource()
        Contract.info = self._src.get_contracts()

    def get_bars(self, strpcon, dt_start='1980-1-1', dt_end='2100-1-1'):
        pcontract = PContract.from_string(strpcon)
        return self._src.get_bars(pcontract, dt_start, dt_end)

    def get_last_bars(self, strpcon, n):
        pcontract = PContract.from_string(strpcon)
        return self._src.get_last_bars(pcontract, n)

    def get_code2strpcon(self):
        pass  # TODO: 什么意思？
