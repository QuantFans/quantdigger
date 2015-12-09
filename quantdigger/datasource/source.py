# -*- coding: utf-8 -*-
import csv
import datetime
import os
import pandas as pd
import string
import time
from quantdigger.errors import FileDoesNotExist, DataFieldError
from quantdigger.datasource import datautil


class SourceWrapper(object):
    """ 数据源包装器，使相关数据源支持逐步读取操作 """
    def __init__(self, pcontract, data, cursor, max_length=0):
        """
        max_length=0，表示逐步模式
        """
        self.data = data
        self.cursor = cursor
        self._max_length = max_length
        self.curbar = -1 
        self.pcontract = pcontract

    def __len__(self):
        return self._max_length

    def  rolling_foward(self):
        """ 读取下一个数据""" 
        raise NotImplementedError


class SqliteSourceWrapper(SourceWrapper):
    """ sqlite数据源包装器，使其支持逐步操作 """
    def __init__(self, pcontract, data, cursor, max_length=0):
        super(SqliteSourceWrapper, self).__init__(pcontract, data, cursor, max_length)

    def rolling_foward(self):
        self.curbar += 1
        # self.cursor为None说明是向量运算
        if self.cursor:
            return self.cursor.fetchone(), self.curbar
        # 超过向量的最大长度。
        if self.curbar == self._max_length:
            return None, self.curbar
        else:
            return True, self.curbar


class CsvSourceWrapper(SourceWrapper):
    """ Csv数据源包装器，使其支持逐步操作 """
    def __init__(self, pcontract, data, cursor, max_length=0):
        super(CsvSourceWrapper, self).__init__(pcontract, data, cursor, max_length)

    def rolling_foward(self):
        self.curbar += 1
        # self.cursor为None说明是向量运算
        if self.cursor:
            try:
                row = self.cursor.next()
            except StopIteration:
                return None, self.curbar
            else:
                dt =  datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                row[0] =  dt
                return row, self.curbar
        if self.curbar ==  self._max_length:
            return None, self.curbar
        else:
            return True, self.curbar


def convert_datetime(tf):
    return datetime.datetime.fromtimestamp(float(tf)/1000)

class SqlLiteSource(object):
    """
    Sqlite数据源。
    """
    def __init__(self, fname):
        import sqlite3
        self.db = sqlite3.connect(fname,
                    detect_types = sqlite3.PARSE_DECLTYPES)
        sqlite3.register_converter('timestamp', convert_datetime)
        ## @todo remove self.cursor
        self.cursor = self.db.cursor()
    
    def load_bars(self, pcontract, dt_start, dt_end, window_size):
        cursor = self.db.cursor()
        id_start, u = datautil.encode2id(pcontract.period, dt_start)
        id_end, u = datautil.encode2id(pcontract.period, dt_end)
        table = string.replace(str(pcontract.contract), '.', '_')
        #sql = "SELECT COUNT(*) FROM {tb} \
                #WHERE {start}<=id AND id<={end}".format(tb=table, start=id_start, end=id_end)
        #max_length = cursor.execute(sql).fetchone()[0]
        #
        sql = "SELECT datetime, open, close, high, low, volume FROM {tb} \
                WHERE {start}<=id AND id<={end}".format(tb=table, start=id_start, end=id_end)
                
        data = pd.read_sql_query(sql, self.db, index_col='datetime')
        if window_size == 0:
            data = pd.read_sql_query(sql, self.db, index_col='datetime')
            ## @todo
            return SqliteSourceWrapper(pcontract, data, None, len(data))
        else:
            cursor.execute(sql)
            data = pd.DataFrame({
                'open': [],
                'close': [],
                'high': [],
                'low': [],
                'volume': []
                })
            data.index = []
            return SqliteSourceWrapper(pcontract, data, cursor, window_size)

    def read_csv(self, path):
        """ 导入路径path下所有csv数据文件到sqlite中，每个文件对应数据库中的一周表格。

        DateFrame(index, open, close, low, high, vol)

        >>> sql.read_csv(os.getcwd())
        """

        for path, dirs, files in os.walk(path):
            for file in files:
                filepath = path + os.sep + file
                if filepath.endswith(".CSV"):
                    fname =  file.split('-')[0]
                    print("import: ", fname)
                    df = pd.read_csv(filepath, parse_dates={'datetime': ['date', 'time']},
                                     index_col='datetime')
                    self._df2sqlite(df, fname)

    def to_csv(self, index=True, index_label='index'):
        """
            导出sqlite中的所有表格数据。
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.get_tables()
        for table_name in tables:
            table_name = table_name[0]
            table = pd.read_sql_query("SELECT * from %s" % table_name, self.db)
            #table['datetime'] = map(lambda x : datetime.fromtimestamp(x / 1000), table['datetime'])
            table.to_csv(table_name + '.csv', index=index, index_label=index_label,
                         columns = ['datetime', 'open', 'close', 'high', 'low', 'volume'])

    def get_tables(self):
        """ 返回数据库所有的表格""" 
        self.cursor.execute("select name from sqlite_master where type='table'")
        return  self.cursor.fetchall()

    def get_table_fields(self, tb):
        """ 返回表格的字段""" 
        self.cursor.execute("select * from %s LIMIT 1" % tb)
        field_names = [r[0] for r in self.cursor.description]
        return field_names

    def _df2sqlite(self, df, tbname):
        self.cursor.execute('''CREATE TABLE {tb}
                     (id int primary key,
                      datetime timestamp,
                      open real,
                      close real,
                      high real,
                      low real,
                      volume int)'''.format(tb = tbname))
        data = []
        for index, row in df.iterrows():
            id, datetime = datautil.encode2id('1.Minute', index)
            data.append((id, datetime, row['open'], row['close'], row['high'], row['low'], row['vol']))
        sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % tbname
        self.cursor.executemany(sql, data)
        self.db.commit()


class CsvSource(object):
    """
    Csv数据源。
    (datetime, open, close, high, low, volume)
    """
    def __init__(self, root):
        self._root = root
    
    def load_bars(self, pcontract, dt_start, dt_end, window_size):
        fname = os.path.join(self._root, str(pcontract) + ".csv")
        if window_size == 0:
            try:
                data = pd.read_csv(fname, index_col=0, parse_dates=True)
            except IOError:
                raise FileDoesNotExist(file=fname)
            else:
                dt_start = pd.to_datetime(dt_start)
                dt_end = pd.to_datetime(dt_end)
                data = data[(dt_start <= data.index) & (data.index <= dt_end)]
                #data.index = map(lambda x : int(time.mktime(x.timetuple())*1000), data.index)
                assert data.index.is_unique
                return CsvSourceWrapper(pcontract, data, None, len(data))
        else:
            data = pd.DataFrame({
                'open': [],
                'close': [],
                'high': [],
                'low': [],
                'volume': []
                })
            data.index = []
            cursor = csv.reader(open(fname, 'rb'))
            fmt = ['datetime', 'open', 'close', 'high', 'low', 'volume']
            header = cursor.next()
            if header != fmt:
                raise DataFieldError(error_fields=header, right_fields=fmt)
            return CsvSourceWrapper(pcontract, data, cursor, window_size)
