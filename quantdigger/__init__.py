# encoding:utf-8


from quantdigger.engine.qd import *
from quantdigger.config import settings
from quantdigger.engine.series import NumberSeries, DateTimeSeries
from quantdigger.technicals.common import *
from quantdigger.datasource import locd

__version__ = '0.4.0'

def set_config(cfg):
    """""" 
    from quantdigger.datasource.data import locd
    if 'source' in cfg:
        cfg['source'] = cfg['source'].lower()
        assert(cfg['source'] in ['sqlite', 'csv']) 
    settings.update(cfg)
    locd.set_source(settings)

set_config(settings)
