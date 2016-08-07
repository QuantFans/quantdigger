# -*- coding: utf-8 -*-

settings = {
    'source': 'csv',
    #'source': 'mongodb',
    'data_path': './data',
    'stock_commission': 3 / 10000.0,
    'future_commission': 1 / 10000.0,
    'tick_test': False,
}

class ConfigInteraction(object):
    backend_server_for_ui = 'backend4ui' 
    backend_server_for_shell = "backend4shell" 
    ui_server_for_shell = "ui4shell" 
    

__all__ = ['settings', 'ConfigInteraction' ]
