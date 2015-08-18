# -*- coding: utf8 -*-

#from flufl.enum import Enum
from quantdigger.errors import PeriodTypeError
from quantdigger import util

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


class Captial(object):
    """ 账号资金 """
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

    :ivar LMT: 限价单，值0.
    :ivar MKT: 市价单，值1.
    """
    LMT = 0
    MKT = 1 
    tdict = {'LMT': LMT,
             'MKT': MKT
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

class HedgeType(object):
    """ 下单类型 

    :ivar SPEC: 投机，值0.
    :ivar HEDG: 套保，值1.
    """
    SPEC = 0
    HEDG = 1
    tdict = {'SPEC': SPEC,
             'HEDG': HEDG
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

class Direction(object):
    """
    多空方向。

    :ivar LONG: 多头，值1.
    :ivar SHORT: 空头，值2.
    """
    LONG = 1
    SHORT = 2
    arg2type = {'LONG': LONG,
             'SHORT': SHORT 
    }

    type2str = { LONG: 'LONG',
                 SHORT: 'SHORT', 
    }

    @classmethod
    def arg_to_type(self, arg):
        """
        把用户输入参数转化为系统类型。
        """ 
        if type(arg) == str:
            return self.arg2type[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(self, type):
        return self.type2str[type]

        
class Transaction(object):
    """ 成交记录。

    :ivar ref: 本地编号
    :vartype ref: int
   
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

    :ivar side: 开平仓标志。
    :vartype side: :class:`TradeSide`

    :ivar datetime: 成交时间
    :vartype datetime: :class:`datetime`

    :ivar price_type: 下单类型。
    :vartype price_type: :class:`PriceType`

    :ivar commission: 佣金百分比
    :vartype commission: float

    :ivar margin_ratio: 保证金比例。
    :vartype margin_ratio: float

    :ivar hedge_type: 交易类型。
    :vartype hedge_type: :class:`PriceType`
    """
    def __init__(self, order=None):
        if order:
            self.id = order.id
            self.ref = order.ref
            self.contract = order.contract
            self.direction = order.direction
            self.price = order.price
            self.quantity = order.quantity
            self.side = order.side
            self.datetime = order.datetime
            self.price_type = order.price_type
            self.hedge_type = order.hedge_type
        self.commission = 0
        self.margin_ratio = 1

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.id)
            return self._hash


    
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

        :ivar ref: 本地编号
        :vartype ref: int

        :ivar id: 报单编号
        :vartype id: :class:`OrderID`

        :ivar contract: 合约。
        :vartype contract: :class:`Contract`

        :ivar direction: 多空方向。
        :vartype direction: :class:`Direction`

        :ivar price: 成交价格。
        :vartype price: float

        :ivar quantity: 成交数量。
        :vartype quantity: float

        :ivar side: 开平仓标志。
        :vartype side: :class:`TradeSide`

        :ivar datetime: 成交时间
        :vartype datetime: :class:`datetime`

        :ivar price_type: 下单类型。
        :vartype price_type: :class:`PriceType`

        :ivar hedge_type: 交易类型。
        :vartype hedge_type: :class:`HedgeType`
    """
    def __init__(self, dt, contract, type_, side, direction, price, quantity, hedge = HedgeType.SPEC):
        self.ref = OrderID.next_order_id()
        self.id = OrderID.next_order_id()
        self.contract = contract
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.side = side
        self.datetime = dt
        self.price_type = type_
        self.hedge_type = hedge
        self.margin_ratio = 1

    def order_margin(self):
        """ 计算这笔限价交易的保证金。
        
           :param float new_price: 当前价格。
           :return: 保证金。
           :rtype: float
        """
        return self.price * self.quantity * self.margin_ratio

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
        self._is_stock = True if exchange == 'stock' else False

    def __str__(self):
        """""" 
        return "%s.%s" % (self.code, self.exch_type)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash

    @property
    def is_stock(self):
        """ 是否是股票""" 
        return self._is_stock

    @classmethod
    def get_trading_interval(self, contract):
        """ 获取合约的交易时段。""" 
        pass

    @classmethod
    def get_margin_ratio(self, contract):
        """ 获取合约的交易时段。""" 
        return 1


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

    :ivar contract: 合约。
    :ivar quantity: 数目。
    :ivar cost: 成本价。
    :ivar direction: 开仓方向。
    :ivar margin_ratio: 保证金比例。
    """
    def __init__(self, trans):
        self.contract = trans.contract
        self.quantity = 0;
        self.cost = 0;
        self.direction = trans.direction
        self.margin_ratio = trans.margin_ratio

    def profit(self, new_price):
        """ 根据当前的价格计算盈亏。
        
           :param float new_price: 当前价格。
           :return: 盈亏数额。
           :rtype: float
        """
        profit = 0
        if self.direction == Direction.LONG:
            profit += (new_price - self.cost) * self.quantity
        else:
            profit += (self.cost - new_price) * self.quantity
        return profit

    @property
    def pre_margin(self):
        """ 昨日保证金占用 """
        pass

    def position_margin(self, new_price):
        """ 根据当前价格计算这笔交易的保证金。
        
           :param float new_price: 当前价格。
           :return: 保证金。
           :rtype: float
        """
        price = self.cost if self.contract.is_stock else new_price
        return price * self.quantity * self.margin_ratio

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.contract)
            return self._hash

    def __str__(self):
        rst = """
                Position:
                   cost - %f
                   quantity - %d
               """ % (self.cost, self.quantity)
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
