from quantdigger.datasource.source import DatasourceAbstract
from quantdigger.util import dlogger as logger
from quantdigger.infras.object import HashObject


class CachedDatasource(DatasourceAbstract):
    '''带缓存的数据源'''

    def __init__(self, datasource, cache):
        self.datasource = datasource
        self.cache = cache

    def get_bars(self, pcontract, dt_start, dt_end):
        try:
            logger.info('trying to load from cache')
            return self.cache.get_bars(pcontract, dt_start, dt_end)
        except LoadCacheException as e:
            logger.info('updating cache')
            missing_range = e.missing_range
            logger.info('missing range: {0}', missing_range)
            missing_data = []
            for start, end in missing_range:
                wrapper = self.datasource.get_bars(pcontract, start, end)
                missing_data.append(HashObject.new(data=wrapper.data,
                                                   start=start,
                                                   end=end))
            self.cache.save_data(missing_data, pcontract)
            logger.info('loading cache')
            return self.cache.get_bars(pcontract, dt_start, dt_end)

    def get_last_bars(self, pcontract, n):
        raise NotImplementedError

    def get_contracts(self):
        # TODO:
        return self.datasource.get_contracts()


class CacheAbstract(DatasourceAbstract):
    '''缓存抽象类'''

    def save_data(self, data, pcontract):
        raise NotImplementedError


class LoadCacheException(Exception):
    def __init__(self, missing_range, cached_data=None):
        assert(missing_range)
        self.cached_data = cached_data
        self.missing_range = missing_range

    def __str__(self):
        return str(self.missing_range)
