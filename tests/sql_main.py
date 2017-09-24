# -*- coding: utf-8 -*-
from test_data import *
from test_engine import *
from trading.test_future import *
from trading.test_stock import *
from quantdigger import locd, set_config

if __name__ == '__main__':
    set_config({ 'source': 'sqlite' })
    unittest.main()
    assert locd.source == 'sqlite'
    # 这里的代码不会被运行
