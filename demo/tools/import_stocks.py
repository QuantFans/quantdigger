# -*- coding: utf-8 -*-
from quantdigger import locd, set_config
from quantdigger.datasource import import_tdx_stock
set_config({ 'data_path': '../data' })
import_tdx_stock('../work/stock', locd)
