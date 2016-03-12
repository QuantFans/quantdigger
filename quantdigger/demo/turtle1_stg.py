#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quantdigger.indicators.common import MA, BOLL
from quantdigger.engine.strategy import TradingStrategy
from quantdigger.engine.series import NumberSeries
import numpy as np
import fw


_IN1 = 20
_IN2 = 55
_OUT = 10
_ATR_DAYS = 20


class Signal(object):
    def __init__(self, price, desc):
        self.__price = price
        self.__desc = desc
    @property
    def price(self): return self.__price
    @property
    def desc(self): return self.__desc


class EntrySignal(Signal):
    def __init__(self, price, desc=''):
        super(EntrySignal, self).__init__(price, desc)

class ExitSignal(Signal):
    def __init__(self, price, desc=''):
        super(ExitSignal, self).__init__(price, desc)

class EntryAddSignal(Signal):
    def __init__(self, price, desc=''):
        super(EntryAddSignal, self).__init__(price, desc)


class Action(object):
    def __init__(self, action, price, real):
        self.__action = action
        self.__price = float(price)
        self.__real = real
    @property
    def action(self): return self.__action
    @property
    def price(self): return self.__price
    @property
    def real(self): return self.__real


class Donchian(object):
    def __init__(self, tracker):
        self.tracker = tracker
        self.status = 'out'
        self.last_profit = 0.0
        self.last_action = None

    @property
    def signal(self):
        return self.__signal

    def update(self):
        tracker = self.tracker
        close = float(tracker.close)
        # todo: 考虑停牌
        upper1 = max([tracker.close[i] for i in range(0, _IN1)]) \
                 if tracker.curbar > _IN1 else np.nan
        upper2 = max([tracker.close[i] for i in range(0, _IN2)]) \
                 if tracker.curbar > _IN2 else np.nan
        down = min([tracker.close[i] for i in range(0, _OUT)])
        self.__signal = None
        if self.status == 'out' and tracker.high >= upper1:
            self.status = 'in1'
            assert(self.last_action is None or self.last_action.action == 'sell')
            real = self.last_profit <= 0
            self.last_action = Action('buy', close, real)
            if real:
                self.__signal = EntrySignal(close, 'in1')
        elif self.status != 'in2' and tracker.high >= upper2:
            self.status = 'in2'
            assert(self.last_action.action == 'buy')
            if not self.last_action.real:
                self.last_action = Action('buy', close, True)
                self.__signal = EntrySignal(close, 'in2')
        elif self.status != 'out' and tracker.low <= down:
            self.status = 'out'
            assert(self.last_action.action == 'buy')
            real = self.last_action.real
            self.last_profit = close - self.last_action.price
            self.last_action = Action('sell', close, real)
            if real:
                self.__signal = ExitSignal(close, '')


class TurtleStrategy(TradingStrategy):
    '''忽略市场选择的海龟策略'''
    def __init__(self, exe):
        super(TurtleStrategy, self).__init__(exe)
        print 'start: ', self.datetime[0]
        self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')
        self.atr = []
        self.tr = []
        self.stop_price = 0.0
        self.donchian = Donchian(self)

    def __update_atr(self):
        tr = max(self.high-self.low, self.high-self.close, self.close-self.low)
        self.tr.append(tr)
        l = len(self.tr)
        daysm1 = _ATR_DAYS - 1
        if l == daysm1:
            atr = sum(self.tr) / _ATR_DAYS
        elif l > daysm1:
            atr = (daysm1 * self.atr[-1] + self.tr[-1]) / _ATR_DAYS
        else:
            atr = np.nan
        print 'atr:', atr
        self.atr.append(atr)

    def __get_position_size(self, price):
        P = 10  # 最少交易股数，这里假设是10
        atr = self.pre_atr
        if atr == 0 or np.isnan(atr): return 0
        q = 0.01 * self.cash() / atr
        quantity = int(q / P) * P
        max_quantity = int(self.cash() / price / P) * P
        print 'p.s 资金{:}, 价格{:}, 平均波动{:}, 规模确认{:}, 最大规模{:}'.format(
            self.cash(), price, atr, quantity, max_quantity)
        #return max_quantity
        if quantity > max_quantity:
            print '资金不足！全仓入场(规模确认%s，最大规模%s)' % (quantity, max_quantity)
            return max_quantity
        else:
            return quantity

    @property
    def pre_atr(self):
        return self.atr[-2]

    def on_bar(self):
        self.__update_atr()
        if self.volume == 0: return # 这天没有成交量，跳过
        self.donchian.update()
        signal = self.donchian.signal
        if isinstance(signal, EntrySignal):
            quantity = self.__get_position_size(signal.price)
            print '## buy signal', signal.price, quantity
            if quantity > 0:
                self.buy('long', signal.price, quantity)
                self.last_buy_price = signal.price
                self.stop_price = signal.price - 2 * self.pre_atr
                print 'buy', self.datetime[0].date(), signal.price, quantity, self.cash(), signal.desc
        elif isinstance(signal, ExitSignal):
            if self.position() > 0:
                self.sell('long', signal.price, self.position())
                self.stop_price = None
                print 'sel', self.datetime[0].date(), signal.price, self.position(), signal.desc
        elif self.stop_price is not None and self.low <= self.stop_price:
            if self.position() > 0:
                self.sell('long', self.close, self.position())
                self.stop_price = None
                print 'sel', self.datetime[0].date(), self.close, self.position(), 'stop'


if __name__ == '__main__':
    import sys
    code = sys.argv[1]
    fw.run(TurtleStrategy, code)
