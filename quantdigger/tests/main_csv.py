# -*- coding: utf-8 -*-
from test_data import *
from test_engine import *
from test_engine_vector import *
from test_future import *
from test_stock import *
from quantdigger import locd

if __name__ == '__main__':
    # 默认为csv
    assert(locd.source == 'csv')
    unittest.main()
    assert locd.source == 'csv' 
    # 这里的代码不会被运行
    # code
