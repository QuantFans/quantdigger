# -*- coding: utf-8 -*-
import csv
import datetime
import os
import pandas as pd
import string
import sqlite3
from quantdigger.engine import series
from quantdigger.errors import FileDoesNotExist, DataFieldError
from quantdigger.datasource import datautil
#from quantdigger.config import settings


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
        self.db = sqlite3.connect(fname,
                    detect_types = sqlite3.PARSE_DECLTYPES)
        sqlite3.register_converter('timestamp', convert_datetime)
        ## @todo remove self.cursor
        self.cursor = self.db.cursor()
    
    def get_bars(self, pcontract, dt_start, dt_end, window_size):
        cursor = self.db.cursor()
        id_start, u = datautil.encode2id(pcontract.period, dt_start)
        id_end, u = datautil.encode2id(pcontract.period, dt_end)
        table = '_'.join([pcontract.contract.exchange, pcontract.contract.code])
        #sql = "SELECT COUNT(*) FROM {tb} \
                #WHERE {start}<=id AND id<={end}".format(tb=table, start=id_start, end=id_end)
        #max_length = cursor.execute(sql).fetchone()[0]
        #
        sql = "SELECT datetime, open, close, high, low, volume FROM {tb} \
                WHERE {start}<=id AND id<={end}".format(tb=table, start=id_start, end=id_end)
                
        data = pd.read_sql_query(sql, self.db, index_col='datetime')
        if not series.g_rolling:
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

    def get_tables(self):
        """ 返回数据库所有的表格""" 
        self.cursor.execute("select name from sqlite_master where type='table'")
        return  self.cursor.fetchall()

    def get_table_fields(self, tb):
        """ 返回表格的字段""" 
        self.cursor.execute("select * from %s LIMIT 1" % tb)
        field_names = [r[0] for r in self.cursor.description]
        return field_names

    def get_contracts(self):
        """ 获取所有合约的基本信息
        
        Returns:
            pd.DataFrame. 
        """
        self.cursor.execute("select * from contract")
        data = self.cursor.fetchall()
        data = zip(*data)
        df = pd.DataFrame({
            'code': data[1], 
            'exchange': data[2],
            'name': data[3],
            'spell': data[4],
            'long_margin_ratio': data[5],
            'short_margin_ratio': data[6],
            'price_tick': data[7],
            'volume_multiple': data[8]
            }, index = data[0])
        return df

    def get_exchanges(self):
        """ 获取所有交易所的编码""" 
        exch = set()
        for row in self.cursor.execute('SELECT * FROM contract'):
            exch.add(row[2])
        return list(exch)

    def import_bars(self, tbdata, strpcon):
        """ 导入交易数据
        
        Args:
            tbdata (dict): {'datetime', 'open', 'close', 'high', 'low', 'volume'}

            strpcon (str): 周期合约字符串如, 'AA.SHFE-1.Minute' 

            生成表格: 'SHFE_AA' 
        """
        data = []
        ids, utimes = [], []
        strdt = strpcon.split('-')[1].upper()
        tbname = strpcon.split('-')[0].split('.')
        tbname = "_".join([tbname[1], tbname[0]])
        for dt in tbdata['datetime']:
            id,  utime = datautil.encode2id(strdt, dt)
            ids.append(id)
            utimes.append(utime)
        data = zip(ids, utimes, tbdata['open'], tbdata['close'], tbdata['high'],
                   tbdata['low'], tbdata['volume'])
        try:
            self.cursor.execute('''CREATE TABLE {tb}
                         (id int primary key,
                          datetime timestamp,
                          open real,
                          close real,
                          high real,
                          low real,
                          volume int)'''.format(tb = tbname))
            self.db.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % tbname
            self.cursor.executemany(sql, data)
            self.db.commit()

    def import_contracts(self, data):
        """ 导入合约的基本信息。
        
        Args:
            data (dict): {key, code, exchange, name, spell, 
            long_margin_ratio, short_margin_ratio, price_tick, volume_multiple}
        
        """

        tbname = 'contract'
        data['key'] = map(lambda x: x.upper(), data['key'])
        data = zip(data['key'], data['code'], data['exchange'], data['name'], 
                   data['spell'], data['long_margin_ratio'], data['short_margin_ratio'],
                   data['price_tick'], data['volume_multiple'])
        sql = '''CREATE TABLE {tb}
                     (key text primary key,
                      code text not null,
                      exchange text not null,
                      name text not null,
                      spell text not null,
                      long_margin_ratio real not null,
                      short_margin_ratio real not null,
                      price_tick real not null,
                      volume_multiple real not null
                      )'''.format(tb=tbname)
        self.cursor.execute(sql)
        sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?,?,?)" % (tbname)
        self.cursor.executemany(sql, data)
        self.db.commit()

    def export_bars(self, index=True, index_label='index'):
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


    def clear_db(self):
        """ 清空数据库""" 
        ## @TODO 
        pass



class CsvSource(object):
    """
    Csv数据源。
    (datetime, open, close, high, low, volume)
    """
    def __init__(self, root):
        self._root = root
    
    def get_bars(self, pcontract, dt_start, dt_end, window_size):
        fname = os.path.join(self._root, str(pcontract) + ".csv")
        if not series.g_rolling:
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
            if header[0:6] != fmt:
                raise DataFieldError(error_fields=header, right_fields=fmt)
            return CsvSourceWrapper(pcontract, data, cursor, window_size)

    def import_contracts(self, data):
        """ 导入合约的基本信息。
        
        Args:
            data (dict): {key, code, exchange, name, spell, 
            long_margin_ratio, short_margin_ratio, price_tick, volume_multiple}
        
        """
        fname = os.path.join(self._root, "contracts.csv")
        df = pd.DataFrame(data)
        df.to_csv(fname, columns = ['code', 'exchange', 'name', 'spell',
                  'long_margin_ratio', 'short_margin_ratio', 'price_tick',
                  'volume_multiple'], index=False)

    #def get_exchanges(self):
        #""" 获取所有交易所的编码""" 
        #df = self.get_contracts()
        #exch = set()
        #for row in df['exchange']
            ##exch.add(row[2])
        ##return list(exch)
        #pass

    def import_bars(self, tbdata, strpcon):
        """ 导入交易数据
        
        Args:
            tbdata (dict): {'datetime', 'open', 'close', 'high', 'low', 'volume'}

            strpcon (str): 周期合约字符串如, 'AA.SHFE-1.Minute' 
        """
        fname = os.path.join(self._root, strpcon+'.csv')
        df = pd.DataFrame(tbdata)
        df.to_csv(fname, columns = ['datetime', 'open', 'close', 'high', 'low',
            'volume'], index=False)

    def get_contracts(self):
        """ 获取所有合约的基本信息
        
        Returns:
            pd.DataFrame
        """
        fname = os.path.join(self._root, "contracts.csv")
        df = pd.read_csv(fname)
        df.index = df['code'] + '.' + df['exchange']
        df.index = map(lambda x: x.upper(), df.index)
        return df

    def export_bars(self, index=True, index_label='index'):
        """
            导出csv中的所有表格数据。
        """
        pass

    def get_tables(self):
        """ 返回数据库所有的表格""" 
        pass
