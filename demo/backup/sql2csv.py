
# -*- coding: utf-8 -*-
import os
from quantdigger.datasource.source import  SqlLiteSource

s = SqlLiteSource(''.join([os.getcwd(), os.sep, 'data', os.sep, 'digger.db']))
s.to_csv(index = False)
