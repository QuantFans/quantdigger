# -*- coding: utf-8 -*-
import os
import sqlite3
import time
import pandas as pd
from quantdigger.datasource import datautil

import timeit
import datetime

df = pd.read_csv('./TWODAY.SHFE-1.Minute.csv', parse_dates={'datetime': ['date', 'time']})
df['volume'] = df.vol

df.to_csv('temp.csv', index=False,
             columns = ['datetime', 'open', 'close', 'high', 'low', 'volume'])



