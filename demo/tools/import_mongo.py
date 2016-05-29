#!/usr/bin/env python

import quantdigger.datasource as qdd


ms = qdd.source.MongoSource()
qdd.datautil.import_data([
    './work/BB.SHFE-1.Minute.csv',
    './work/AA.SHFE-1.Minute.csv'
], ms)
