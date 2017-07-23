# -*- coding: utf-8 -*-
import six
# from flufl.enum import Enum
from datetime import timedelta
from quantdigger.errors import PeriodTypeError
from quantdigger.config import settings
from quantdigger.util import dlogger as logger


class TradeSide(object):
    """ 开平仓标志

    :ivar BUY: 多头开仓， 1
    :ivar SHORT: 空头开仓， 2
    :ivar COVER: 空头平仓，3
    :ivar SELL: 多头平仓，4
    :ivar COVER_TODAY: 空头平今，5
    :ivar SELL_TODAY: 多头平今，6
    :ivar KAI: 开仓，7
    :ivar PING: 平仓，8
    :ivar CANCEL: 撤单，9
    """
    BUY = 1
    SHORT = 2
    COVER = 3
    SELL = 4
    COVER_TODAY = 5
    SELL_TODAY = 6
    KAI = 7
    PING = 8
    CANCEL = 9

    @classmethod
    def arg_to_type(cls, arg):
        """
        把用户输入参数转化为系统类型。
        """
        tdict = {
            'BUY': 1,
            'SHORT': 2,
            'COVER': 3,
            'SELL': 4,
            'COVER_TODAY': 5,
            'SELL_TODAY': 6,
            'KAI': 7,
            'PING': 8,
            'CANCEL': 9
        }
        if isinstance(arg, str):
            return tdict[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(cls, type_):
        type2str = {
            cls.BUY: '多头开仓',
            cls.SHORT: '空头开仓',
            cls.COVER: '空头平仓',
            cls.SELL: '多头平仓',
            cls.COVER_TODAY: '空头平今',
            cls.SELL_TODAY: '多头平今',
            cls.KAI: '开仓',
            cls.PING: '平仓',
            cls.CANCEL: '撤单',
        }
        return type2str[type_]


class Captial(object):
    """ 账号资金

    :ivar broker_id: 经纪商
    :ivar account_id: 交易账号
    :ivar margin: 保证金占用
    :ivar position_profit: 持仓盈亏
    :ivar close_profit: 平仓盈亏
    :ivar trading_day: 交易日
    :ivar equity: 当前权益
    :ivar cash: 可用资金
    """
    def __init__(self, dt, contract, type_, side, direction, price, quantity):
        self.broker_id = None
        self.account_id = None
        self.margin = None
        self.position_profit = None
        self.close_profit = None
        self.trading_day = None
        self.cash = None
        self.equity = None


class PriceType(object):
    """ 下单类型

    :ivar MKT: 市价单 - 1.
    :ivar LMT: 限价单 - 2.
    """
    MKT = 1
    LMT = 2

    @classmethod
    def arg_to_type(cls, arg):
        """
        把用户输入参数转化为系统类型。
        """
        tdict = {
            'LMT': cls.LMT,
            'MKT': cls.MKT
        }
        if isinstance(arg, str):
            return tdict[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(cls, type):
        type2str = {
            cls.LMT: 'LMT',
            cls.MKT: 'MKT'
        }
        return type2str[type]


class HedgeType(object):
    """ 下单类型

    :ivar SPEC: 投机 - 1.
    :ivar HEDG: 套保 - 2.
    """
    SPEC = 1
    HEDG = 2

    @classmethod
    def arg_to_type(cls, arg):
        """
        把用户输入参数转化为系统类型。
        """
        tdict = {
            'SPEC': cls.SPEC,
            'HEDG': cls.HEDG
        }
        if isinstance(arg, str):
            return tdict[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(cls, type):
        type2str = {cls.SPEC: 'SPEC',
                    cls.HEDG: 'HEDG'}

        return type2str[type]


class Direction(object):
    """
    多空方向。

    :ivar LONG: 多头 - 1.
    :ivar SHORT: 空头 - 2.
    """
    LONG = 1
    SHORT = 2

    @classmethod
    def arg_to_type(cls, arg):
        """
        把用户输入参数转化为系统类型。
        """
        arg2type = {
            'LONG': cls.LONG,
            'SHORT': cls.SHORT
        }
        if isinstance(arg, str):
            return arg2type[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(cls, type_):
        type2str = {
            cls.LONG: 'long',
            cls.SHORT: 'short'
        }
        return type2str[type_]


class Transaction(object):
    """ 成交记录。

    :ivar id: 成交编号
    :ivar contract: 合约。
    :ivar direction: 多空方向。
    :ivar price: 成交价格。
    :ivar quantity: 成交数量。
    :ivar side: 开平仓标志。
    :ivar datetime: 成交时间
    :ivar price_type: 下单类型。
    :ivar hedge_type: 交易类型。
    """
    def __init__(self, order=None):
        if order:
            self.id = order.id
            self.contract = order.contract
            self.direction = order.direction
            self.price = order.price
            self.quantity = order.quantity
            self.side = order.side
            self.datetime = order.datetime
            self.price_type = order.price_type
            self.hedge_type = order.hedge_type
            self.order = order
        self.volume_multiple = order.volume_multiple
        self.compute_commission()
        #six.print_("********************" )
        #six.print_(self.datetime, self.price, self.quantity, self.volume_multiple, ratio)
        #six.print_("********************" )
        #assert False

    def compute_commission(self):
        ratio = settings['stock_commission'] if self.contract.is_stock else\
            settings['future_commission']
        self.commission = self.price * self.quantity * \
            self.volume_multiple * ratio

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.id)
            return self._hash

    def __eq__(self, r):
        try:
            return self._hash == r._hash
        except AttributeError:
            return hash(self) == hash(r)

    def __str__(self):
        rst = " id: %s\n contract: %s\n direction: %s\n price: %f\n quantity: %d\n side: %s\n datetime: %s\n price_type: %s\n hedge_type: %s" % \
            (self.id, self.contract, Direction.type_to_str(self.direction),
             self.price, self.quantity, TradeSide.type_to_str(self.side),
             self.datetime, PriceType.type_to_str(self.price_type),
             HedgeType.type_to_str(self.hedge_type))
        return rst


class OrderID(object):
    """ 委托ID， 用来唯一的标识一个委托订单。 """
    order_id = 0

    def __init__(self, id):
        self.id = id
        # self.ref = OrderID.next_order_id()

    @classmethod
    def next_order_id(cls):
        """ 下个有效的委托ID编号。 """
        cls.order_id += 1
        return OrderID(cls.order_id)

    def __eq__(self, v):
        return self.id == v.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __str__(self):
        return str(self.id)

    def __hash__(self):
        return hash(self.id)


class Order(object):
    """ 订单

        :ivar id: 报单编号
        :ivar contract: 合约。
        :ivar direction: 多空方向。
        :ivar price: 成交价格。
        :ivar quantity: 成交数量。
        :ivar side: 开平仓标志。
        :ivar datetime: 成交时间
        :ivar price_type: 下单类型。
        :ivar hedge_type: 交易类型。
    """
    def __init__(self, dt, contract, type_, side, direction,
                 price, quantity, hedge=HedgeType.SPEC, id=None):
        self.id = id if id else OrderID.next_order_id()
        self.contract = contract
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.side = side
        self.datetime = dt
        self.price_type = type_
        self.hedge_type = hedge
        if self.direction == Direction.LONG:
            self._margin_ratio = Contract.long_margin_ratio(str(self.contract))
        else:
            self._margin_ratio = Contract.short_margin_ratio(
                str(self.contract))
        self.volume_multiple = Contract.volume_multiple(str(self.contract))

    def order_margin(self, new_price):
        """ 计算这笔限价交易的保证金。

        Args:
            new_price (float): 最新价格。

        Returns:
            float. 保证金占用
        """
        price = self.price if self.contract.is_stock else new_price
        return price * self.quantity * self._margin_ratio * \
            self.volume_multiple

    def print_order(self):
        #six.print_("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % (self.symbol, self.order_type, self.quantity, self.direction))
        pass

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.id)
            return self._hash

    def __str__(self):
        rst = " id: %s\n contract: %s\n direction: %s\n price: %f\n quantity: %d\n side: %s\n datetime: %s\n price_type: %s\n hedge_type: %s\n long_margin_ratio: %f" % \
            (self.id, self.contract, Direction.type_to_str(self.direction),
             self.price, self.quantity, TradeSide.type_to_str(self.side),
             self.datetime, PriceType.type_to_str(self.price_type),
             HedgeType.type_to_str(self.hedge_type), self.long_margin_ratio)
        return rst

    def __eq__(self, r):
        return self._hash == r._hash


class Contract(object):
    """ 合约。

    :ivar exchange: 市场类型。
    :ivar code: 合约代码
    :ivar is_stock: 是否是股票
    :ivar margin_ratio: 保证金比例。
    :ivar volume_multiple: 合约乘数。
    """
    info = None

    def __init__(self, str_contract):
        ## @TODO 修改参数为（code, exchange)
        info = str_contract.split('.')
        if len(info) == 2:
            code = info[0].upper()
            exchange = info[1].upper()
        else:
            logger.error('错误的合约格式: %s' % str_contract)
            logger.exception()
        self.exchange = exchange
        self.code = code
        if self.exchange == 'SZ' or self.exchange == 'SH':
            self.is_stock = True
        elif self.exchange == 'SHFE':
            self.is_stock = False
        elif self.exchange == 'TEST' and self.code == 'STOCK':
            self.is_stock = True
        elif self.exchange == 'TEST':
            self.is_stock = False
        else:
            logger.error('Unknown exchange: {0}', self.exchange)
            assert(False)
    
    @classmethod
    def from_string(cls, strcontract):
        return cls(strcontract)

    def __str__(self):
        """"""
        return "%s.%s" % (self.code, self.exchange)

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.__str__())
            return self._hash

    def __eq__(self, r):
        try:
            return self._hash == r._hash
        except AttributeError:
            return hash(self) == hash(r)

    def __cmp__(self, r):
        return str(self) < str(r)

    @classmethod
    def trading_interval(cls, contract):
        """ 获取合约的交易时段。"""
        pass

    @classmethod
    def long_margin_ratio(cls, strcontract):
        try:
            ## @todo 确保CONTRACTS.csv里面没有重复的项，否则有可能返回数组．
            return cls.info.loc[strcontract.upper(), 'long_margin_ratio']
        except KeyError:
            logger.warn("Can't not find contract: %s" % strcontract)
            return 1
            # assert(False)

    @classmethod
    def short_margin_ratio(cls, strcontract):
        try:
            return cls.info.loc[strcontract.upper(), 'short_margin_ratio']
        except KeyError:
            logger.warn("Can't not find contract: %s" % strcontract)
            return 1
            # assert(False)

    @classmethod
    def volume_multiple(cls, strcontract):
        try:
            return cls.info.loc[strcontract.upper(), 'volume_multiple']
        except KeyError:
            logger.warn("Can't not find contract: %s" % strcontract)
            return 1
            # assert(False)


class Period(object):
    """ 周期

    :ivar unit: 时间单位
    :ivar count: 数值
    """
    #class Type(Enum):
        #MilliSeconds = "MilliSeconds" 
        #Seconds = "Seconds" 
        #Minutes = "Minutes" 
        #Hours = "Hours" 
        #Days = "Days" 
        #Months = "Months" 
        #Seasons = "Seasons" 
        #Years = "Years" 
    periods = {
        "MILLISECOND": 0, 
        "SECOND" : 1,
        "MINUTE": 2,
        "HOUR": 3,
        "DAY": 4,
        "MONTH": 5,
        "SEASON": 6,
        "YEAR": 7
    }

    def __init__(self, strperiod):
        period = strperiod.split('.')
        if len(period) == 2:
            unit_count = int(period[0])
            time_unit = period[1].upper()
        else:
            raise PeriodTypeError
        if time_unit not in self.periods.keys():
            raise PeriodTypeError(period=time_unit)
        self.unit = time_unit
        self.count = unit_count

    def __str__(self):
        return "%d.%s" % (self.count, self.unit)

    def to_timedelta(self):
        m = {
            'DAY': 'days',
            'HOUR': 'hours',
            'MINUTE': 'minutes',
            'SECOND': 'seconds',
            'MILLISECOND': 'milliseconds',
        }
        try:
            u = m[self.unit]
            kwargs = {u: self.count}
            return timedelta(**kwargs)
        except KeyError:
            raise Exception('unit "%s" is not supported' % self.unit)

    def __cmp__(self, r):
        cmp_unit = Period.periods[self.unit]
        cmp_unit_r = Period.periods[r.unit]
        if cmp_unit < cmp_unit_r:
            return -1
        elif cmp_unit > cmp_unit_r:
            return 1
        else:
            if self.count < r.count:
                return -1
            elif self.count > r.count:
                return 1
            else:
                return 0

class PContract(object):
    """ 特定周期的合约。

    :ivar contract: 合约对象。
    :ivar period: 周期。
    """
    def __init__(self, contract, period):
        self.contract = contract
        self.period = period

    #def __str__(self):
        #""" return string like 'IF000.SHEF-10.Minutes'  """
        #return "%s-%s" % (self.contract, self.period)

    @classmethod
    def from_string(cls, strpcon):
        t = strpcon.split('-')
        return cls(Contract(t[0]), Period(t[1]))

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.__str__())
            return self._hash

    def __eq__(self, r):
        try:
            return self._hash == r._hash
        except AttributeError:
            return hash(self) == hash(r)

    def __str__(self):
        return '%s-%s' % (str(self.contract), str(self.period))

    def __cmp__(self, r):
        if self.period < r.period:
            return -1 
        elif self.period > r.period:
            return 1
        else:
            if self.contract < r.contract:
                return -1 
            elif self.contract > r.contract:
                return 1
            else:
                return 0

class PositionKey(object):
    def __init__(self, contract, direction):
        self.contract = contract
        self.direction = direction

    def __str__(self):
        return "%s_%s" % (self.contract, str(self.direction))

    @property
    def is_stock(self):
        return self.contract.is_stock

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash = hash((self.contract, self.direction))
            return self._hash

    def __eq__(self, r):
        try:
            return self._hash == r._hash
        except AttributeError:
            return hash(self) == hash(r)


class Position(object):
    """ 单笔仓位信息。

    :ivar contract: 合约。
    :ivar quantity: 数目。
    :ivar closable: 可平数目。
    :ivar today: 当天开仓数目。
    :ivar cost: 成本价。
    :ivar direction: 开仓方向。
    """
    def __init__(self, trans):
        self.contract = trans.contract
        self.quantity = 0
        self.closable = 0
        self.today = 0
        self.cost = 0
        self.direction = trans.direction
        strcon = str(self.contract)
        if self.direction == Direction.LONG:
            self._margin_ratio = Contract.long_margin_ratio(strcon)
        else:
            self._margin_ratio = Contract.short_margin_ratio(strcon)
        self._volume_multiple = Contract.volume_multiple(strcon)
        self.symbol = str(trans.contract)

    def profit(self, new_price):
        """ 根据最新价格计算持仓盈亏。

        Args:
            new_price (float): 最新价格。

        Returns:
            float. 盈亏数额
        """
        profit = 0
        if self.direction == Direction.LONG:
            profit += (new_price - self.cost) * self.quantity * \
                self._volume_multiple
        else:
            profit -= (new_price - self.cost) * self.quantity * \
                self._volume_multiple
        return profit

    @property
    def pre_margin(self):
        """ 昨日保证金占用 """
        pass

    def position_margin(self, new_price):
        """ 根据当前价格计算这保证金占用。

        Args:
            new_price (float): 最新价格。

        Returns:
            float. 证金占用/市值
        """
        return new_price * self.quantity * self._margin_ratio * \
            self._volume_multiple

    def __str__(self):
        rst = " contract: %s\n direction: %s\n cost: %f\n quantity: %d\n closeable: %d\n" % \
                (self.contract, Direction.type_to_str(self.direction),
                 self.cost, self.quantity, self.closable)
        return rst


class Bar(object):
    """Bar数据。

    :ivar datetime: 开盘时间。
    :ivar open: 开盘价。
    :ivar close: 收盘价。
    :ivar high: 最高价。
    :ivar low: 最低价。
    :ivar volume: 成交量。
    """
    def __init__(self, dt, open, close, high, low, vol):
        self.datetime = dt
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = vol


class OneDeal(object):
    """ 每笔交易（一开，一平)

    :ivar open_datetime: 开仓时间
    :ivar close_datetime: 平仓时间
    :ivar open_price: 开仓价格
    :ivar close_price: 平仓价格
    :ivar direction: 开仓方向
    """
    def __init__(self, buy_trans, sell_trans, quantity):
        self.open = buy_trans
        self.close = sell_trans
        self.quantity = quantity

    def profit(self):
        """ 盈亏额  """
        direction = self.open.direction
        if direction == Direction.LONG:
            return (self.close.price - self.open.price) * self.open.quantity *\
                    self.open.order.volume_multiple
        else:
            return (self.open.price - self.close.price) * self.open.quantity *\
                    self.open.order.volume_multiple

    def __str__(self):
        return "direction: %s\nentry_datetime: %s\nentry_price: %s\nexit_datetime: %s\nexit_price: %s\n" %(Direction.type_to_str(self.direction), self.open_datetime, self.open_price, self.close_datetime, self.close_price)

    @property
    def open_datetime(self):
        return self.open.datetime

    @property
    def open_price(self):
        return self.open.price

    @property
    def close_datetime(self):
        return self.close.datetime

    @property
    def close_price(self):
        return self.close.price

    @property
    def direction(self):
        return self.open.direction
