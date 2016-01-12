# -*- coding: utf-8 -*-
import pandas as pd
import os
from quantdigger import locd
from quantdigger.datasource import import_data
from quantdigger.config import set_config



def import_contracts():
    """ 从文件导入合约到数据库""" 
    df = pd.read_csv('./work/contracts.txt')
    df['key'] = df['code'] + '.' + df['exchange']
    return df

print("import contracts info..")
contracts = import_contracts()

set_config({ 'source': 'csv'})
locd.import_contracts(contracts)
print("import bars..")
fpaths = []
for path, dirs, files in os.walk('./work'):
    for file in files:
        filepath = path + os.sep + file
        if filepath.endswith(".csv") or filepath.endswith(".CSV"):
            fpaths.append(filepath)
import_data(fpaths, locd)

set_config({ 'source': 'sqlite'})
locd.import_contracts(contracts)

print("import bars..")
fpaths = []
for path, dirs, files in os.walk('./work'):
    for file in files:
        filepath = path + os.sep + file
        if filepath.endswith(".csv") or filepath.endswith(".CSV"):
            fpaths.append(filepath)
import_data(fpaths, locd)
