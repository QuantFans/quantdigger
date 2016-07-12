# -*- coding: utf-8 -*-
import os
import pandas as pd
import sqlite3
import pymongo
from pymongo import MongoClient
from quantdigger.errors import FileDoesNotExist, DataFieldError
from quantdigger.datasource import datautil
from quantdigger.util import int2time
# from quantdigger.config import settings


class SourceWrapper(object):
    """ 数据源包装器，使相关数据源支持逐步读取操作 """
    def __init__(self, pcontract, data,  max_length):
        self.data = data
        self._max_length = max_length
        self.curbar = -1
        self.pcontract = pcontract

    def __len__(self):
        return self._max_length

    def rolling_forward(self):
        """ 读取下一个数据"""
        raise NotImplementedError


class SqliteSourceWrapper(SourceWrapper):
    def __init__(self, pcontract, data, max_length):
        super(SqliteSourceWrapper, self).__init__(pcontract, data, max_length)

    def rolling_forward(self):
        self.curbar += 1
        if self.curbar == self._max_length:
            return False, self.curbar
        else:
            return True, self.curbar


class MongoSourceWrapper(SourceWrapper):
    def __init__(self, pcontract, data, max_length):
        super(MongoSourceWrapper, self).__init__(pcontract, data, max_length)

    def rolling_forward(self):
        self.curbar += 1
        if self.curbar == self._max_length:
            return False, self.curbar
        else:
            return True, self.curbar


class CsvSourceWrapper(SourceWrapper):
    def __init__(self, pcontract, data, max_length):
        super(CsvSourceWrapper, self).__init__(pcontract, data, max_length)

    def rolling_forward(self):
        self.curbar += 1
        if self.curbar == self._max_length:
            return False, self.curbar
        else:
            return True, self.curbar


class SqlLiteSource(object):
    """
    Sqlite数据源。
    """
    def __init__(self, fname):
        self.db = sqlite3.connect(fname, detect_types=sqlite3.PARSE_DECLTYPES)
        sqlite3.register_converter('timestamp', int2time)
        self.cursor = self.db.cursor()

    def get_code2strpcon(self):
        raise NotImplementedError

    def get_bars(self, pcontract, dt_start, dt_end):
        id_start, u = datautil.encode2id(pcontract.period, dt_start)
        id_end, u = datautil.encode2id(pcontract.period, dt_end)
        table = '_'.join([pcontract.contract.exchange,
                          pcontract.contract.code])
        # sql = "SELECT COUNT(*) FROM {tb} \
                # WHERE {start}<=id AND id<={end}".format(tb=table, start=id_start, end=id_end)
        # max_length = cursor.execute(sql).fetchone()[0]
        #
        sql = "SELECT datetime, open, close, high, low, volume FROM {tb} \
                WHERE {start}<=id AND id<={end}".format(
                    tb=table, start=id_start, end=id_end)
        data = pd.read_sql_query(sql, self.db, index_col='datetime')
        return SqliteSourceWrapper(pcontract, data, len(data))

    def get_last_bars(self, pcontract, n):
        raise NotImplementedError

    def get_tables(self):
        """ 返回数据库所有的表格"""
        self.cursor.execute(
            "select name from sqlite_master where type='table'")
        return self.cursor.fetchall()

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
         }, index=data[0])
        return df

    def get_exchanges(self):
        """ 获取所有交易所的编码"""
        exch = set()
        for row in self.cursor.execute('SELECT * FROM contract'):
            exch.add(row[2])
        return list(exch)

    def import_bars(self, tbdata, pcontract):
        """ 导入交易数据

        Args:
            tbdata (dict): {'datetime', 'open', 'close',
                            'high', 'low', 'volume'}
            pcontract (PContract): 周期合约
        """
        strpcon = str(pcontract).upper()
        data = []
        ids, utimes = [], []
        strdt = strpcon.split('-')[1].upper()
        tbname = strpcon.split('-')[0].split('.')
        tbname = "_".join([tbname[1], tbname[0]])
        for dt in tbdata['datetime']:
            id, utime = datautil.encode2id(strdt, dt)
            ids.append(id)
            utimes.append(utime)
        data = zip(ids, utimes, tbdata['open'],
                   tbdata['close'], tbdata['high'],
                   tbdata['low'], tbdata['volume'])
        try:
            self.cursor.execute('''CREATE TABLE {tb}
                         (id int primary key,
                          datetime timestamp,
                          open real,
                          close real,
                          high real,
                          low real,
                          volume int)'''.format(tb=tbname))
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
                   data['spell'], data['long_margin_ratio'],
                   data['short_margin_ratio'],
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
        # @TODO
        tables = self.get_tables()
        for table_name in tables:
            table_name = table_name[0]
            table = pd.read_sql_query("SELECT * from %s" % table_name, self.db)
            #table['datetime'] = map(lambda x : datetime.fromtimestamp(x / 1000), table['datetime'])
            table.to_csv(table_name+'.csv', index=index,
                         index_label=index_label,
                         columns=['datetime', 'open',
                                  'close', 'high',
                                  'low', 'volume'])

    def clear_db(self):
        """ 清空数据库"""
        # @TODO
        pass


class CsvSource(object):
    """
    Csv数据源。
    (datetime, open, close, high, low, volume)
    """
    def __init__(self, root):
        self._root = root

    def get_code2strpcon(self):
        symbols = {}  # code -> string pcontracts
        period_exchange2strpcon = {}  # exchange.period -> string pcontracts
        for parent, dirs, files in os.walk(self._root):
            if dirs == []:
                t = parent.split(os.sep)
                period, exch = t[-2], t[-1]
                for i, a in enumerate(period):
                    if not a.isdigit():
                        sepi = i
                        break
                count = period[0:sepi]
                unit = period[sepi:]
                period = '.'.join([count, unit])
                strpcons = period_exchange2strpcon.setdefault(
                    ''.join([exch, '-', period]), [])
                for file_ in files:
                    if file_.endswith('csv'):
                        code = file_.split('.')[0]
                        t = symbols.setdefault(code, [])
                        rst = ''.join([code, '.', exch, '-', period])
                        t.append(rst)
                        strpcons.append(rst)
        return symbols, period_exchange2strpcon

    def get_bars(self, pcontract, dt_start, dt_end):
        # @TODO test dt_start, dt_end works
        data = self._load_bars(pcontract)
        dt_start = pd.to_datetime(dt_start)
        dt_end = pd.to_datetime(dt_end)
        data = data[(dt_start <= data.index) & (data.index <= dt_end)]
        assert data.index.is_unique
        return CsvSourceWrapper(pcontract, data, len(data))

    def get_last_bars(self, pcontract, n):
        data = self._load_bars(pcontract)
        data = data[-n:]
        assert data.index.is_unique
        return CsvSourceWrapper(pcontract, data, len(data))

    def _load_bars(self, pcontract):
        strpcon = str(pcontract).upper()
        contract, period = tuple(strpcon.split('-'))
        code, exch = tuple(contract.split('.'))
        period = period.replace('.', '')
        fname = os.path.join(self._root, period, exch, code + ".csv")
        try:
            data = pd.read_csv(fname, index_col=0, parse_dates=True)
        except IOError:
            raise FileDoesNotExist(file=fname)
        else:
            return data

    def import_contracts(self, data):
        """ 导入合约的基本信息。

        Args:
            data (dict): {key, code, exchange, name, spell,
            long_margin_ratio, short_margin_ratio, price_tick, volume_multiple}

        """
        fname = os.path.join(self._root, "contracts.csv")
        df = pd.DataFrame(data)
        df.to_csv(fname, columns=[
            'code', 'exchange', 'name', 'spell',
            'long_margin_ratio', 'short_margin_ratio', 'price_tick',
            'volume_multiple'
        ], index=False)

    #def get_exchanges(self):
        #""" 获取所有交易所的编码""" 
        #df = self.get_contracts()
        #exch = set()
        #for row in df['exchange']
            ##exch.add(row[2])
        ##return list(exch)
        #pass

    def import_bars(self, tbdata, pcontract):
        """ 导入交易数据

        Args:
            tbdata (dict): {'datetime', 'open', 'close',
                            'high', 'low', 'volume'}
            pcontract (PContract): 周期合约
        """
        strpcon = str(pcontract).upper()
        contract, period = tuple(strpcon.split('-'))
        code, exch = tuple(contract.split('.'))
        period = period.replace('.', '')
        try:
            os.makedirs(os.path.join(self._root, period, exch))
        except OSError:
            pass
        fname = os.path.join(self._root, period, exch, code+'.csv')
        df = pd.DataFrame(tbdata)
        df.to_csv(fname, columns=[
            'datetime', 'open', 'close', 'high', 'low', 'volume'
        ], index=False)

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


class MongoSource(object):
    """
    MongoDB数据源
    """
    def __init__(self, address='localhost', port='27017',
                 dbname='quantdigger'):
         # TODO: address, port
        self.client = MongoClient()
        self.db = self.client[dbname]

    def __get_collection_name(self, period, exchange, code):
        return '{period}.{exchange}.{code}'.format(
            period=str(period).replace('.', ''),
            exchange=exchange,
            code=code)

    def get_code2strpcon(self):
        from collections import defaultdict
        return defaultdict(lambda: [], {}), defaultdict(lambda: [], {})

    def get_bars(self, pcontract, dt_start, dt_end):
        id_start, _ = datautil.encode2id(pcontract.period, dt_start)
        id_end, _ = datautil.encode2id(pcontract.period, dt_end)
        colname = self.__get_collection_name(
            pcontract.period,
            pcontract.contract.exchange,
            pcontract.contract.code)
        cursor = self.db[colname].find({
            'id': {
                '$gt': id_start,
                '$lt': id_end
            }
        }).sort('id', pymongo.ASCENDING)
        data = pd.DataFrame(list(cursor)).set_index('datetime')
        return MongoSourceWrapper(pcontract, data, len(data))

    def get_last_bars(self):
        raise NotImplementedError

    def get_tables(self): pass

    def get_table_fields(self): pass

    def get_contracts(self):
        colname = 'contract'
        cursor = self.db[colname].find()
        return pd.DataFrame(list(cursor))

    def get_exchanges(self): pass

    def import_bars(self, tbdata, pcontract):
        strpcon = str(pcontract).upper()
        code_exchange, strdt = strpcon.split('-')
        code, exchange = code_exchange.split('.')
        colname = self.__get_collection_name(strdt, exchange, code)
        ts = map(lambda dt: datautil.encode2id(strdt, dt), tbdata['datetime'])
        ids, utimes = zip(*ts)
        data = map(lambda (_id, _datetime,
                           _open, _close,
                           _high, _low,
                           _volume): {
            'id': _id, 'datetime': _datetime,
            'open': _open, 'close': _close,
            'high': _high, 'low': _low,
            'volume': _volume
        }, zip(ids, tbdata['datetime'], tbdata['open'], tbdata['close'],
               tbdata['high'], tbdata['low'], tbdata['volume']))
        self.db[colname].insert_many(data)

    def import_contracts(self, data):
        colname = 'contract'
        data['key'] = map(lambda x: x.upper(), data['key'])
        data = map(lambda (_key, _code,
                           _exchange, _name,
                           _spell, _long_margin_ratio,
                           _short_margin_ratio, _price_tick,
                           _volume_multiple): {
            'key': _key, 'code': _code,
            'exchange': _exchange, 'name': _name,
            'spell': _spell, 'long_margin_ratio': _long_margin_ratio,
            'short_margin_ratio': _short_margin_ratio,
            'price_tick': _price_tick,
            'volume_multiple': _volume_multiple
        }, zip(data['key'], data['code'], data['exchange'], data['name'],
               data['spell'], data['long_margin_ratio'],
               data['short_margin_ratio'], data['price_tick'],
               data['volume_multiple']))
        self.db[colname].insert_many(data)

    def export_bars(self): pass

    def clear_db(self): pass
