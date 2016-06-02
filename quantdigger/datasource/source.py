class SourceWrapper(object):
    """ 数据源包装器，使相关数据源支持逐步读取操作 """

    def __init__(self, pcontract, data,  max_length):
        self.data = data
        self._max_length = max_length
        self.curbar = -1
        self.pcontract = pcontract

    def __len__(self):
        return self._max_length

    def rolling_forward(self):
        """ 读取下一个数据"""
        self.curbar += 1
        if self.curbar == self._max_length:
            return False, self.curbar
        else:
            return True, self.curbar


class DataSourceAbstract(object):
    '''数据源抽象基类'''

    def get_bars(self, pcontract, dt_start, dt_end):
        raise NotImplementedError

    def get_last_bars(self, pcontract, n):
        raise NotImplementedError

    def get_contracts(self):
        raise NotImplementedError
