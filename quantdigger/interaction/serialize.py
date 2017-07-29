##
# @file serialize.py
# @brief
# @author Wells
# @version 0.5
# @date 2016-08-07

from datetime import datetime
import pandas as pd
from quantdigger.datastruct import PContract, Contract

import json
from json import JSONEncoder


class DataStructCoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def serialize_pcontract_bars(str_pcontract, bars):
    data = {
        'pcontract': str_pcontract,
        'datetime': list(map(lambda x: str(x), bars.index)),
        'open': bars.open.tolist(),
        'close': bars.close.tolist(),
        'high': bars.high.tolist(),
        'low': bars.low.tolist(),
        'vol': bars.volume.tolist(),
    }
    return json.dumps(data)


def deserialize_pcontract_bars(data):
    data = json.loads(data)
    dt = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), data['datetime']))
    # datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f")
    pcon = data['pcontract']
    del data['pcontract']
    del data['datetime']
    return pcon, pd.DataFrame(data, index=dt)


def serialize_all_pcontracts(pcontracts):
    return [str(pcontract) for pcontract in pcontracts]


def serialize_all_contracts(contracts):
    return [str(contract) for contract in contracts]


def deserialize_all_pcontracts(pcontracts):
    return [PContract.from_string(strpcon) for strpcon in pcontracts]


def deserialize_all_contracts(contracts):
    return [Contract.from_string(strcon) for strcon in contracts]
