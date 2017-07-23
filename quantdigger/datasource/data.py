# -*- coding: utf-8 -*-
##
# @file data.py
# @brief 数据控制模块
# @author skabyy
# @version 0.3
# @date 2016-05-26

from .dsutil import get_setting_datasource
from quantdigger.datastruct import PContract, Contract


class DataManager(object):
    """
    数据代理
    """

    DEFAULT_DT_START = '1980-1-1'
    DEFAULT_DT_END = '2100-1-1'

    def __init__(self):
        self._src = get_setting_datasource()
        Contract.info = self._src.get_contracts()

    def get_bars(self, strpcon,
                 dt_start=DEFAULT_DT_START, dt_end=DEFAULT_DT_END):
        pcontract = PContract.from_string(strpcon)
        return self._src.get_bars(pcontract, dt_start, dt_end)

    def get_last_bars(self, strpcon, n):
        pcontract = PContract.from_string(strpcon)
        return self._src.get_last_bars(pcontract, n)

    def get_code2strpcon(self):
        return self._src.get_code2strpcon()

    def get_contracts(self):
        return self._src.get_contracts()

