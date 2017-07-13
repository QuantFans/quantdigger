#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datasource.test_csv import *
from test_engine import *
from test_future import *
from test_stock import *
from quantdigger import ConfigUtil

if __name__ == '__main__':
    # 默认为csv
    assert(ConfigUtil.get('source') == 'csv')
    unittest.main()
    assert(ConfigUtil.get('source') == 'csv')
    # 这里的代码不会被运行
    # code
