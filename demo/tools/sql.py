# -*- coding: utf-8 -*-
import six
import os
import sqlite3
import time
import pandas as pd
from quantdigger.datasource import datautil

import timeit
import datetime

db = sqlite3.connect('digger.db', 
        detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )

def convert_datetime(tf):
    # 取
    return datetime.datetime.fromtimestamp(float(tf)/1000)

sqlite3.register_converter('timestamp', convert_datetime)
#db = sqlite3.connect(':memory:',
c = db.cursor()


def read_csv(path):
    """ 导入路径path下所有csv数据文件到sqlite中，每个文件对应数据库中的一周表格。

    DateFrame(index, open, close, low, high, vol)

    >>> csv2sqlite(os.getcwd())
    """
    def df2sqlite(df, tbname):
        sql = '''CREATE TABLE {tb}
                     (id int primary key,
                      datetime timestamp,
                      open real,
                      close real,
                      high real,
                      low real,
                      volume int)'''.format(tb=tbname)
        c.execute(sql)
        data = []
        for index, row in df.iterrows():
            id, utime = datautil.encode2id('1.Minute', index)
            data.append((id, utime, row['open'], row['close'], row['high'], row['low'], row['volume']))
        sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % (tbname)
        c.executemany(sql, data)
        db.commit()

    for path, dirs, files in os.walk(path):
        for file in files:
            filepath = path + os.sep + file
            if filepath.endswith(".csv"):
                fname =  file.split('-')[0]
                six.print_("import: ", fname)
                #df = pd.read_csv(filepath, parse_dates={'datetime': ['date', 'time']},
                df = pd.read_csv(filepath, parse_dates='datetime',
                                 index_col='datetime')
                fname = fname.replace('.', '_')
                df2sqlite(df, fname)



def get_tables(c):
    """ 返回数据库所有的表格""" 
    c.execute("select name from sqlite_master where type='table'")
    return  c.fetchall()

def table_field(c, tb):
    """ 返回表格的字段""" 
    c.execute("select * from %s LIMIT 1" % tb)
    field_names = [r[0] for r in c.description]
    return field_names

def sql2csv(db, cursor):
    """
        导出sqlite中的所有表格数据。
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = get_tables(cursor)
    for table_name in tables:
        table_name = table_name[0]
        table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        table.to_csv(table_name + '.txt', index_label='index')


start = timeit.default_timer()
read_csv(os.getcwd())
stop = timeit.default_timer()
six.print_((stop - start ) * 1000)
six.print_("---------")
db.commit()

start = timeit.default_timer()
open = close = high = low = []
for row in c.execute('SELECT id, datetime, open FROM AA_SHFE'):
    six.print_(row)
six.print_(get_tables(c))

stop = timeit.default_timer()
six.print_((stop - start ) * 1000)

get_tables(c)
db.commit()
db.close()
