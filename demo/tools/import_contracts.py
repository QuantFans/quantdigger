# -*- coding: utf-8 -*-
import six
import pandas as pd
from quantdigger import ConfigUtil
from quantdigger.datasource import ds_impl


def import_contracts(decode=False):
    """ 从文件导入合约到数据库 """
    df = pd.read_csv('./contracts.txt')
    contracts = []
    codes = set()
    for idx, row in df.iterrows():
        data = None
        if row['isStock']:
            if row['exchangeId'] == 'SZSE':
                row['exchangeId'] = 'SZ'
            else:
                row['exchangeId'] = 'SH'
            if decode:
                data = (row['code']+'.'+row['exchangeId'],
                        row['code'],
                        row['exchangeId'],
                        row['name'].decode('utf8'), row['pinyin'], 1, 1, 0, 1)
            else:
                data = (row['code']+'.'+row['exchangeId'],
                        row['code'],
                        row['exchangeId'],
                        row['name'], row['pinyin'], 1, 1, 0, 1)
            contracts.append(data)
        else:
            data = (row['code']+'.'+row['exchangeId'],
                    row['code'],
                    row['exchangeId'],
                    row['code'], row['code'], row['long_margin_ratio'],
                    row['short_margin_ratio'],
                    row['price_tick'],
                    row['volume_multiple'])
            contracts.append(data)
            # 修正ctp部分合约只有3位日期。
            if not row['code'][-4].isdigit():
                row['code'] = row['code'][0:-3] + '1' + row['code'][-3:]
                # 支持两种日期
                data = (row['code']+'.'+row['exchangeId'],
                        row['code'],
                        row['exchangeId'],
                        row['code'], row['code'], row['long_margin_ratio'],
                        row['short_margin_ratio'],
                        row['price_tick'],
                        row['volume_multiple'])
                contracts.append(data)
            # 无日期指定的期货合约
            code = row['code'][0:-4]
            if code not in codes:
                t = (code+'.'+row['exchangeId'], code, row['exchangeId'],
                     code, code, row['long_margin_ratio'],
                     row['short_margin_ratio'], row['price_tick'],
                     row['volume_multiple'])
                contracts.append(t)
                codes.add(code)
    contracts = zip(*contracts)
    rst = {
            'key': contracts[0],
            'code': contracts[1],
            'exchange': contracts[2],
            'name': contracts[3],
            'spell': contracts[4],
            'long_margin_ratio': contracts[5],
            'short_margin_ratio': contracts[6],
            'price_tick': contracts[7],
            'volume_multiple': contracts[8],
            }
    return rst

six.print_("import contracts..")
contracts = import_contracts()
csv_ds = ds_impl.csv_source.CsvSource('../data')
csv_ds.import_contracts(contracts)

contracts = import_contracts(True)
sqlite_ds = ds_impl.sqlite_source.SqliteSource('../data/digger.db')
sqlite_ds.import_contracts(contracts)
