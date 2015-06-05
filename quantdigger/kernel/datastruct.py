# -*- coding: utf8 -*-

#from flufl.enum import Enum
from quantdigger.errors import PeriodTypeError
from quantdigger import util

class TradeSide(object):
    """ 开平仓标志 

    :ivar BUY: 都头开仓， 1
    :ivar SHORT: 空头开仓， 2
    :ivar COVER: 空头平仓，3
    :ivar SELL: 多头平仓，4
    :ivar COVER_TODAY: 空头平今，5
    :ivar SELL_TODAY: 多头平今，6
    :ivar KAI: 开仓，7
    :ivar PING: 平仓，8
    """
    BUY = 1
    SHORT = 2
    COVER = 3
    SELL = 4
    COVER_TODAY = 5
    SELL_TODAY = 6
    KAI = 7
    PING = 8

    tdict = {
        'BUY': 1,
        'SHORT': 2,
        'COVER': 3,
        'SELL': 4,
        'COVER_TODAY': 5,
        'SELL_TODAY': 6,
        'KAI': 7,
        'PING': 8
    }

    @classmethod
    def arg_to_type(self, arg):
        """
        把用户输入参数转化为系统类型。
        """ 
        if type(arg) == str:
            return self.tdict[arg.upper()]
        else:
            return arg
            

class DealType(object):
    """ 下单类型 """
    LIMIT = 1
    MARKET = 2


class Direction(object):
    """
    多空方向。

    :ivar LONG: 多头，值1.
    :ivar SHORT: 空头，值2.
    """
    LONG = 1
    SHORT = 2
    tdict = {'LONG': LONG,
             'SHORT': SHORT 
    }

    @classmethod
    def arg_to_type(self, arg):
        """
        把用户输入参数转化为系统类型。
        """ 
        if type(arg) == str:
            return self.tdict[arg.upper()]
        else:
            return arg

        
class Transaction(object):
    """ 成交记录。
   
    :ivar id: 成交编号
    :vartype id: :class:`OrderID`

    :ivar contract: 合约。
    :vartype contract: :class:`Contract`

    :ivar direction: 多空方向。
    :vartype direction: :class:`Direction`

    :ivar price: 成交价格。
    :vartype price: float

    :ivar quantity: 成交数量。
    :vartype quantity: float

    :ivar kpp: 开平仓标志。
    :vartype kpp: :class:`TradeSide`

    :ivar datetime: 成交时间
    :vartype datetime: :class:`datetime`

    :ivar type: 下单类型。
    :vartype type: :class:`DealType`

    :ivar commission: 佣金百分比
    :vartype commission: float

    :ivar assure_ratio: 保证金比例。
    :vartype assure_ratio: float
    """
    def __init__(self, order=None):
        if order:
            self.id = order.id
            self.contract = order.contract
            self.direction = order.direction
            self.price = order.price
            self.quantity = order.quantity
            self.kpp = order.kpp
            self.datetime = order.datetime
            self.type = order.type
        self.commission = 0
        self.assure_ratio = 1

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.id)
            return self._hash

    def profit(self, new_price):
        """ 根据当前的价格计算盈亏。
        
           :param float new_price: 当前价格。
           :return: 盈亏数额。
           :rtype: float
        """
        profit = 0
        if self.direction == Direction.LONG:
            profit += (new_price - self.price) * self.quantity
        else:
            profit += (self.price - new_price) * self.quantity
        return profit

    def deposit(self, new_price):
        """ 根据当前价格计算这笔交易的保证金。
        
           :param float new_price: 当前价格。
           :return: 保证金。
           :rtype: float
        """
        return self.price * self.quantity * self.assure_ratio

    
class OrderID(object):
    """
    委托ID， 用来唯一的标识一个委托订单。
    """
    order_id = 0
    def __init__(self, id):
        self.id = id

    @classmethod
    def next_order_id(cls):
        """
        下个有效的委托ID编号。
        """ 
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
        

class Order(object):
    """ 订单 

        :ivar id: 成交编号
        :vartype id: :class:`OrderID`

        :ivar contract: 合约。
        :vartype contract: :class:`Contract`

        :ivar direction: 多空方向。
        :vartype direction: :class:`Direction`

        :ivar price: 成交价格。
        :vartype price: float

        :ivar quantity: 成交数量。
        :vartype quantity: float

        :ivar kpp: 开平仓标志。
        :vartype kpp: :class:`TradeSide`

        :ivar datetime: 成交时间
        :vartype datetime: :class:`datetime`

        :ivar type: 下单类型。
        :vartype type: :class:`DealType`
    """
    def __init__(self, dt, contract, type_, kpp, direction, price, quantity):
        self.id = OrderID.next_order_id()
        self.contract = contract
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.kpp = kpp
        self.datetime = dt
        self.type = type_

    def print_order(self):
        #print "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            #(self.symbol, self.order_type, self.quantity, self.direction)
        pass

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.id)
            return self._hash

    
class Contract(object):
    """ 合约。
   
    :ivar exch_type: 市场类型。
    :vartype exch_type: str

    :ivar code: 合约代码
    :vartype code: str
    """
    def __init__(self, str_contract):
        info = str_contract.split('.')
        if len(info) == 2:
            code = info[0]
            exchange = info[1]
        else:
            ## @todo 合约到市场的映射。
            assert False
        self.exch_type = exchange  # 用'stock'表示中国股市
        self.code = code

    def __str__(self):
        """""" 
        return "%s.%s" % (self.code, self.exch_type)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash


class Period(object):
    """ 周期 """
    #class Type(Enum):
        #MilliSeconds = "MilliSeconds" 
        #Seconds = "Seconds" 
        #Minutes = "Minutes" 
        #Hours = "Hours" 
        #Days = "Days" 
        #Months = "Months" 
        #Seasons = "Seasons" 
        #Years = "Years" 
    periods = ["MilliSecond", "Second", "Minute", "Hour",
               "Day", "Month", "Season", "Year"]    

    def __init__(self, str_period):
        period = str_period.split('.')
        if len(period) == 2:
            unit_count = int(period[0])
            time_unit = period[1]
        else:
            raise PeriodTypeError
        if time_unit not in self.periods:
            raise PeriodTypeError

        self._type = time_unit
        self._length = unit_count

    @property
    def type(self):
        """
        时间单位。
        """
        return self._type

    @property
    def length(self):
        """
        时间长度。
        """
        return self._length

    def __str__(self):
        return "%d.%s" % (self._length, self._type)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash


class PContract(object):
    """ 特定周期的合约。

    :ivar contract: 合约对象。
    :ivar period: 周期。
    """
    def __init__(self, contract, period):
        self.contract = contract
        self.period = period

    def __str__(self):
        """ return string like 'SHEF-IF000-Minutes-10'  """
        return "%s-%s" % (self.contract, self.period)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash

class Position(object):
    """ 单笔仓位信息。

    :ivar order: 委托单信息。
    :ivar transaction: 成交信息。
    :ivar quantity: 单笔数目。
    """
    def __init__(self, order, transaction):
        self.order = order
        self.transaction = transaction
        self.quantity = transaction.quantity

    @property
    def datetime(self):
        return self.transaction.datetime

    @property
    def price(self):
        """ 成交价格""" 
        return self.transaction.price

    @property
    def assure_ratio(self):
        """ 保证金比例 """ 
        return self.transaction.assure_ratio

    @property
    def direction(self):
        return self.transaction.direction

    #def order_time(self):
        #return self.order.datetime

    #def order_price(self):
        #pass

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(util.time2int(self.datetime))
            return self._hash

    def __str__(self):
        rst = """
                Position:
                   datetime - %s
                   price - %f
                   quantity - %d
               """ % (str(self.datetime), self.price, self.quantity)
        return rst


class Bar(object):
    """Bar数据。

    :ivar open: 开盘价。
    :vartype open: float

    :ivar close: 收盘价。
    :vartype close: float

    :ivar high: 最高价。
    :vartype high: float

    :ivar low: 最低价。
    :vartype low: float

    :ivar datetime: 开盘时间。
    :vartype datetime: datetime

    :ivar vol: 成交量。
    :vartype vol: float
    """
    def __init__(self, dt, open, close, high, low, vol):
        self.datetime = dt
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = vol
