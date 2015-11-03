# -*- coding: utf-8 -*-
import sqlite3
import os
import pandas as pd

import timeit
from quantdigger.datasource import data

conn = sqlite3.connect('future.db',
#conn = sqlite3.connect(':memory:',
                      detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c = conn.cursor()



def df2sqlite(df, tbname):
    # Create table
    c.execute('''CREATE TABLE {tb}
                 (id int primary key,
                  open real,
                  close real,
                  high real,
                  low real,
                  volume int)'''.format(tb = tbname))
    count = 0
    for index, row in df.iterrows():
        id = data.encode2id('1.Minute', index)
        # Insert a row of data
        sql = "INSERT INTO {tb} VALUES ({id}, {open},{close},{high},{low}, {volume})".format(
                id = id, open = row['open'], close = row['close'],
                high = row['high'], low = row['low'], volume = row['vol'], tb = tbname)
        c.execute(sql)
        if count % 240 == 0:
            print(index)
        count += 1
    conn.commit()

def csv2sqlite(path):
    """ 导入csv数据文件到sqlite中，每个文件对应数据库中的一周表格。

    >>> csv2sqlite(os.getcwd())
    """
    for path, dirs, files in os.walk(path):
        for file in files:
            filepath = path + os.sep + file
            if filepath.endswith(".CSV"):
                df = pd.read_csv(filepath, parse_dates={'datetime': ['date', 'time']}, index_col='datetime')
                df2sqlite(df, file.split('-')[0])
                print file.split('-')[0]

#start = timeit.default_timer()
#open = close = high = low = []
#for row in c.execute('SELECT open FROM A'):
    #open.append(row[0])
#stop = timeit.default_timer()
#print (stop - start )
#print (stop - start ) * 2000 / 60
conn.close()
