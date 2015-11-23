# -*- coding: utf8 -*-
from quantdigger.engine.series import NumberSeries, DateTimeSeries
from quantdigger.engine import series

class DataContext(object):
    def __init__(self, wrapper, window_size):
        """ window_size: 滚动窗口大小 """
        self.wrapper = wrapper
        self.window_size = window_size
        self.indicators = { }
        self.series = { }
        data = self.wrapper.data
        if window_size == 0:
            self.window_size =  len(data)
        self.open = NumberSeries(data.open.values, self.window_size, 'open')
        self.close = NumberSeries(data.close.values, self.window_size, 'close')
        self.high = NumberSeries(data.high.values, self.window_size, 'high')
        self.low = NumberSeries(data.low.values, self.window_size, 'low')
        self.volume = NumberSeries(data.volume.values, self.window_size, 'volume')
        self.datetime = DateTimeSeries(data.index, self.window_size, 'datetime')

    def rolling_foward(self):
        """""" 
        return self.wrapper.rolling_foward()

    def add_series(self, key, s):
        """ 添加on_init中初始化的序列变量    
        
        Args:
            key (str): 属性名
            s (Series): 序列变量 
        """
        s.reset_data([], self.window_size+series.g_window)
        self.series[key] = s
        return

    def add_indicator(self, key, indic):
        ## @todo 加上属性名到数据的字典，这样才能跨context引用到。
        self.indicators[key] = indic

    def __len__(self):
        return len(self.wrapper)

    def __getitem__(self, attr):
        try:
            return self.series[attr]
        except KeyError:
            return self.indicators[attr]


class Context(object):
    """ 上下文"""
    def __init__(self, ex):
        self.all_data = ex.data
        self.data_context = None
        self.curbar = 0

    def switch_to(self, pcon):
        self.data_context = self.all_data[pcon]

    def update_context(self, curbar):
        self.curbar = curbar
        # 为当天数据预留空间, 改变g_window或者一次性分配
        #self.data = np.append(data, tracker.container_day)
        self.open.update_curbar(self.curbar)
        self.close.update_curbar(self.curbar)
        self.high.update_curbar(self.curbar)
        self.low.update_curbar(self.curbar)
        self.volume.update_curbar(self.curbar)
        self.datetime.update_curbar(self.curbar)

        # 更新数据源
        if series.g_rolling:
            new_row = self.data_context.rolling_foward()
            self.datetime.update(new_row[0])
            self.open.update(new_row[1])
            self.close.update(new_row[2])
            self.high.update(new_row[3])
            self.low.update(new_row[4])
            self.volume.update(new_row[5])

        for key, s in self.data_context.series.iteritems():
            s.update_curbar(self.curbar)
            s.duplicate_last_element()

        for key, indic in self.data_context.indicators.iteritems():
            for s in indic.series:
                s.update_curbar(curbar)

    @property
    def open(self):
        return self.data_context.open

    @property
    def close(self):
        return self.data_context.close

    @property
    def high(self):
        return self.data_context.high

    @property
    def low(self):
        return self.data_context.low

    @property
    def volume(self):
        return self.data_context.volume
    
    @property
    def datetime(self):
        return self.data_context.datetime

    def __getitem__(self, strpcon):
        """ 获取跨品种合约 """
        self.all_data[strpcon]

    #def __setitem__(self, attr, value):
        #self.series[attr] = value
