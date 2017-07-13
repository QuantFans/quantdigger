#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tests.datasource.test_csv import *
from . import test_engine
from . import test_future
from . import test_stock
from quantdigger import ConfigUtil

if __name__ == '__main__':
    # 默认为csv
    assert(ConfigUtil.get('source') == 'csv')
    unittest.main()
    assert(ConfigUtil.get('source') == 'csv')
    # 这里的代码不会被运行
    # code
