# -*- coding: utf-8 -*-
from test_data import *
#from test_engine import *
from test_engine_vector import *
from test_future import *
from test_stock import *
from quantdigger.config import set_config
from quantdigger import locd

if __name__ == '__main__':
    set_config({ 'source': 'sqlite' })
    unittest.main()
    assert locd.source == 'sqlite' 
    # 这里的代码不会被运行
