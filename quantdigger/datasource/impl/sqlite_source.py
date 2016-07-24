# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

from quantdigger.datasource import datautil
from quantdigger.datasource.dsutil import *
from quantdigger.datasource.source import SourceWrapper, DatasourceAbstract
from quantdigger.util import int2time


@register_datasource('sqlite', 'data_path')
class SqliteSource(DatasourceAbstract):
    '''Sqlite数据源'''

    def __init__(self, path):
        self._db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        sqlite3.register_converter('timestamp', int2time)
        self._cursor = self._db.cursor()

    def get_bars(self, pcontract, dt_start, dt_end):
        id_start, u = datautil.encode2id(pcontract.period, dt_start)
        id_end, u = datautil.encode2id(pcontract.period, dt_end)
        table = '_'.join([pcontract.contract.exchange,
                          pcontract.contract.code])
        sql = "SELECT datetime, open, close, high, low, volume FROM {tb} \
                WHERE {start}<=id AND id<={end}".format(
                    tb=table, start=id_start, end=id_end)
        data = pd.read_sql_query(sql, self._db, index_col='datetime')
        return SourceWrapper(pcontract, data, len(data))

    def get_last_bars(self, pcontract, n):
        raise NotImplementedError

    def get_contracts(self):
        """ 获取所有合约的基本信息

        Returns:
            pd.DataFrame.
        """
        self._cursor.execute("select * from contract")
        data = self._cursor.fetchall()
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
            self._cursor.execute('''CREATE TABLE {tb}
                         (id int primary key,
                          datetime timestamp,
                          open real,
                          close real,
                          high real,
                          low real,
                          volume int)'''.format(tb=tbname))
            self._db.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % tbname
            self._cursor.executemany(sql, data)
            self._db.commit()

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
        self._cursor.execute(sql)
        sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?,?,?)" % (tbname)
        self._cursor.executemany(sql, data)
        self._db.commit()

    def get_code2strpcon(self):
        raise NotImplementedError
