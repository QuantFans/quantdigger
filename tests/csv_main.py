#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from test_data import *
from test_engine import *
from test_future import *
from test_stock import *
from quantdigger.config import settings

if __name__ == '__main__':
    # 默认为csv
    assert(settings['source'] == 'csv')
    unittest.main()
    assert(settings['source'] == 'csv')
    # 这里的代码不会被运行
    # code
