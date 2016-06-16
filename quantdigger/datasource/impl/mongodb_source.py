# -*- coding: utf-8 -*-

import pandas as pd
import pymongo
from pymongo import MongoClient

from quantdigger.datasource import datautil
from quantdigger.datasource.dsutil import *
from quantdigger.datasource.source import SourceWrapper, DatasourceAbstract


@register_datasource('mongodb', 'address', 'port', 'dbname')
class MongoDBSource(DatasourceAbstract):
    '''MongoDBs数据源'''

    def __init__(self, address, port, dbname):
        # TODO address, port
        self._client = MongoClient()
        self._db = self._client([dbname])

    def _get_collection_name(self, period, exchange, code):
        return '{period}.{exchange}.{code}'.format(
            period=str(period).replace('.', ''),
            exchange=exchange,
            code=code)

    def get_bars(self, pcontract, dt_start, dt_end):
        id_start, _ = datautil.encode2id(pcontract.period, dt_start)
        id_end, _ = datautil.encode2id(pcontract.period, dt_end)
        colname = self._get_collection_name(
            pcontract.period,
            pcontract.contract.exchange,
            pcontract.contract.code)
        cursor = self._db[colname].find({
            'id': {
                '$gt': id_start,
                '$lt': id_end
            }
        }).sort('id', pymongo.ASCENDING)
        data = pd.DataFrame(list(cursor)).set_index('datetime')
        return SourceWrapper(pcontract, data, len(data))

    def get_last_bars(self, pcontract, n):
        raise NotImplementedError

    def get_contracts(self):
        colname = 'contract'
        cursor = self.db[colname].find()
        return pd.DataFrame(list(cursor))
