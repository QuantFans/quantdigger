# -*- coding: utf-8 -*-
import pandas as pd
from quantdigger.errors import FileDoesNotExist

class SqlLiteSource(object):
    """
    """
    def __init__(self, fname):
        import sqlite3
        self._conn = sqlite3.connect(fname,
                              detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        #conn = sqlite3.connect(':memory:',
        self._cursor = self._conn.cursor()
    
    def load_bars(self, pcontract, dt_start, dt_end):
        pass


class CsvSource(object):
    """"""
    def __init__(self, root):
        self._root = root
    
    def load_bars(self, pcontract, dt_start, dt_end):
        fname = ''.join([self._root, str(pcontract), ".csv"])
        try:
            data = pd.read_csv(fname, index_col=0, parse_dates=True)
            data = data[(dt_start <= data.index) & (data.index <= dt_end)]
            assert data.index.is_unique
        except IOError:
            #print u"**Warning: File \"%s\" doesn't exist!"%fname
            raise FileDoesNotExist(file=fname)
        else:
            return data
