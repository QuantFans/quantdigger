# encoding:utf-8

from quantdigger.engine.strategy import *
from quantdigger.config import settings
from quantdigger.configutil import ConfigUtil
from quantdigger.engine.series import NumberSeries, DateTimeSeries
from quantdigger.technicals.common import *
from quantdigger.util import rlogger, deprecated

__version__ = '0.6.1'


@deprecated
def set_config(cfg):
    """"""
    # from quantdigger.datasource.data import locd
    # if 'source' in cfg:
    #     cfg['source'] = cfg['source'].lower()
    #     assert(cfg['source'] in ['sqlite', 'csv', 'mongodb'])
    settings.update(cfg)
    # locd.set_source(settings)


# set_config(settings)
