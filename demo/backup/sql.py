# -*- coding: utf-8 -*-
import os
import sqlite3
import time
import pandas as pd
from quantdigger.datasource import datautil

import timeit
import datetime

db = sqlite3.connect('digger.db', 
        detect_types = sqlite3.PARSE_COLNAMES)
def adapt_datetime(ts):
    return time.mktime(ts.timetuple())
def convert_datetime(tf):
    return datetime.datetime.fromtimestamp(tf)

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('datetime', convert_datetime)
#db = sqlite3.connect(':memory:',
c = db.cursor()


def read_csv(path):
    """ 导入路径path下所有csv数据文件到sqlite中，每个文件对应数据库中的一周表格。

    DateFrame(index, open, close, low, high, vol)

    >>> csv2sqlite(os.getcwd())
    """
    def df2sqlite(df, tbname):
        c.execute('''CREATE TABLE {tb}
                     (id int primary key,
                      utime timestamp,
                      open real,
                      close real,
                      high real,
                      low real,
                      volume int)'''.format(tb=tbname+'_SHFE'))
        data = []
        for index, row in df.iterrows():
            id, utime = datautil.encode2id('1.Minute', index)
            data.append((id, utime, row['open'], row['close'], row['high'], row['low'], row['vol']))
        sql = "INSERT INTO %s VALUES (?,?,?,?,?,?,?)" % (tbname+'_SHFE')
        c.executemany(sql, data)
        db.commit()

    for path, dirs, files in os.walk(path):
        for file in files:
            filepath = path + os.sep + file
            if filepath.endswith(".CSV"):
                fname =  file.split('-')[0]
                print("import: ", fname)
                df = pd.read_csv(filepath, parse_dates={'datetime': ['date', 'time']},
                                 index_col='datetime')
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


#start = timeit.default_timer()
#read_csv(os.getcwd())
#stop = timeit.default_timer()
#print (stop - start )
#print (stop - start ) * 1000
#print "---------"

start = timeit.default_timer()
open = close = high = low = []
for row in c.execute('SELECT id, utime, open FROM A_SHFE'):
    #print row
    print row
stop = timeit.default_timer()
print (stop - start )

get_tables(c)
db.commit()
db.close()
