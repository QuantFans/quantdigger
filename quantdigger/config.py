# -*- coding: utf-8 -*-

settings = {
    'source': 'csv',
    #'source': 'mongodb',
    'data_path': './data',
    'stock_commission': 3 / 10000.0,
    'future_commission': 1 / 10000.0,
    'tick_test': False,
}


class ConfigLog(object):
    log_level = 'INFO'
    log_to_file = True
    log_to_console = True
    log_path = './log'
    

__all__ = ['settings', 'ConfigLog']
