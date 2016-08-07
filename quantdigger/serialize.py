##
# @file serialize.py
# @brief 
# @author Wells
# @version 0.5
# @date 2016-08-07

import json

def serialize_pcontract_bars(str_pcontract, bars):
    data = {
        'pcontract': str_pcontract,
        'datetime': map(lambda x: str(x), bars.index),
        'open': bars.open.tolist(),
        'close': bars.close.tolist(),
        'high': bars.high.tolist(),
        'low': bars.low.tolist(),
        'volume': bars.volume.tolist(),
    }
    return json.dumps(data)

def deserialize_pcontract_bars(pcontract, bars):
    """ convert serialized pcontract to PContract """
    return


def serialize_all_pcontracts(all_pcontracts):
    return json.dumps(all_pcontracts)

def deserialize_all_pcontracts():
    """ convert serialized pcontract to PContract """
    return


