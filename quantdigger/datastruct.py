# -*- coding: utf8 -*-

#from flufl.enum import Enum
from quantdigger.errors import PeriodTypeError

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
    CANCEL = 9

    @classmethod
    def arg_to_type(self, arg):
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
        if type(arg) == str:
            return tdict[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(self, type):
        type2str = { 
            self.BUY: '多头开仓',
            self.SHORT: '空头开仓',
            self.COVER: '空头平仓',
            self.SELL: '多头平仓',
            self.COVER_TODAY: '空头平今',
            self.SELL_TODAY: '多头平今',
            self.KAI: '开仓',
            self.PING: '平仓',
            self.CANCEL: '撤单',
        }
        return type2str[type]


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

    :ivar LMT: 限价单 - 1.
    :ivar MKT: 市价单 - 0.
    """
    LMT = 1
    MKT = 0 

    @classmethod
    def arg_to_type(self, arg):
        """
        把用户输入参数转化为系统类型。
        """ 
        tdict = {'LMT': self.LMT,
                 'MKT': self.MKT
        }
        if type(arg) == str:
            return tdict[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(self, type):
        type2str = { self.LMT: 'LMT',
                     self.MKT: 'MKT'}
        return type2str[type]

class HedgeType(object):
    """ 下单类型 

    :ivar SPEC: 投机 - 0.
    :ivar HEDG: 套保 - 1.
    """
    SPEC = 0
    HEDG = 1

    @classmethod
    def arg_to_type(self, arg):
        """
        把用户输入参数转化为系统类型。
        """ 
        tdict = {'SPEC': self.SPEC,
                 'HEDG': self.HEDG }
        if type(arg) == str:
            return tdict[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(self, type):
        type2str = { self.SPEC: 'SPEC',
                     self.HEDG: 'HEDG'}
    
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
    def arg_to_type(self, arg):
        """
        把用户输入参数转化为系统类型。
        """ 
        arg2type = {'LONG': self.LONG,
                 'SHORT': self.SHORT 
        }
        if type(arg) == str:
            return arg2type[arg.upper()]
        else:
            return arg

    @classmethod
    def type_to_str(self, type):
        type2str = { self.LONG: 'long',
                     self.SHORT: 'short'}
    
        return type2str[type]

        
class Transaction(object):
    """ 成交记录。

    :ivar ref: 本地编号
    :ivar id: 成交编号
    :ivar contract: 合约。
    :ivar direction: 多空方向。
    :ivar price: 成交价格。
    :ivar quantity: 成交数量。
    :ivar side: 开平仓标志。
    :ivar datetime: 成交时间
    :ivar price_type: 下单类型。
    :ivar commission: 佣金百分比
    :ivar margin_ratio: 保证金比例。
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
        self.commission = 0
        self.margin_ratio = 1

    def __hash__(self):
        try:
            return self._hash    
        except AttributeError:
            self._hash =  hash(self.id)
            return self._hash

    def __eq__(self, r):
        return self._hash == r._hash

    def __str__(self):
        rst = " id: %s\n contract: %s\n direction: %s\n price: %f\n quantity: %d\n side: %s\n datetime: %s\n price_type: %s\n hedge_type: %s\n margin_ratio: %f" % \
        (self.id, self.contract, Direction.type_to_str(self.direction),
        self.price, self.quantity, TradeSide.type_to_str(self.side),
        self.datetime, PriceType.type_to_str(self.price_type),
        HedgeType.type_to_str(self.hedge_type), self.margin_ratio)
        return rst


    
class OrderID(object):
    """
    委托ID， 用来唯一的标识一个委托订单。
    """
    order_id = 0
    def __init__(self, id):
        self.id = id
        #self.ref = OrderID.next_order_id()

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

    def __str__(self):
        return str(self.id)

    def __hash__(self):
        return hash(self.id)
        

class Order(object):
    """ 订单 

        :ivar ref: 本地编号
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
        self.contract = contract
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.side = side
        self.datetime = dt
        self.price_type = type_
        self.hedge_type = hedge
        self.margin_ratio = 1
        self.id = id if id else OrderID.next_order_id()

    def order_margin(self, new_price):
        """ 计算这笔限价交易的保证金。

        Args:
            new_price (float): 最新价格。
        
        Returns:
            float. 保证金占用
        """
        return self.price * self.quantity * self.margin_ratio

    def print_order(self):
        #print "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            #(self.symbol, self.order_type, self.quantity, self.direction)
        pass

    def __hash__(self):
        try:
            return self._hash    
        except AttributeError:
            self._hash =  hash(self.id)
            return self._hash

    def __str__(self):
        rst = " id: %s\n contract: %s\n direction: %s\n price: %f\n quantity: %d\n side: %s\n datetime: %s\n price_type: %s\n hedge_type: %s\n margin_ratio: %f" % \
        (self.id, self.contract, Direction.type_to_str(self.direction),
        self.price, self.quantity, TradeSide.type_to_str(self.side),
        self.datetime, PriceType.type_to_str(self.price_type),
        HedgeType.type_to_str(self.hedge_type), self.margin_ratio)
        return rst

    def __eq__(self, r):
        return self._hash == r._hash

    
class Contract(object):
    """ 合约。
   
    :ivar exch_type: 市场类型。
    :ivar code: 合约代码
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
        ## @TODO 从代码中计算
        self.is_stock = True if exchange == 'stock' else False

    def __str__(self):
        """""" 
        return "%s.%s" % (self.code, self.exch_type)

    def __hash__(self):
        try:
            return self._hash    
        except AttributeError:
            self._hash =  hash(self.__str__())
            return self._hash

    def __eq__(self, r):
        return self._hash == r._hash

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


class PContract(object):
    """ 特定周期的合约。

    :ivar contract: 合约对象。
    :ivar period: 周期。
    """
    def __init__(self, contract, period):
        self.contract = contract
        self.period = period

    def __str__(self):
        """ return string like 'IF000.SHEF-10.Minutes'  """
        return "%s-%s" % (self.contract, self.period)

    @classmethod
    def from_string(self, strpcon):
        t = strpcon.split('-')
        return PContract(Contract(t[0]), Period(t[1]))

    def __hash__(self):
        try:
            return self._hash    
        except AttributeError:
            self._hash =  hash(self.__str__())
            return self._hash

    def __eq__(self, r):
        return self._hash == r._hash


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
            self._hash =  hash((self.contract, self.direction))
            return self._hash

    def __eq__(self, r):
        return self._hash == r._hash


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
        self.quantity = 0
        self.closable = 0 # 可平数量
        self.today = 0    # 当天数量
        self.cost = 0
        self.direction = trans.direction
        self.margin_ratio = trans.margin_ratio

    def profit(self, new_price):
        """ 根据最新价格计算持仓盈亏。
        
        Args:
            new_price (float): 最新价格。
        
        Returns:
            float. 盈亏数额
        """

        profit = 0
        if self.direction == Direction.LONG:
            profit += (new_price - self.cost) * self.quantity
        else:
            profit -= (new_price - self.cost) * self.quantity
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
            float. 保证金占用
        """
        price = self.cost if self.contract.is_stock else new_price
        return price * self.quantity * self.margin_ratio

    def __str__(self):
        rst = " contract: %s\n direction: %s\n cost: %f\n quantity: %d\n " % \
                (self.contract, Direction.type_to_str(self.direction),
                       self.cost, self.quantity)
        return rst


class Bar(object):
    """Bar数据。

    :ivar open: 开盘价。
    :ivar close: 收盘价。
    :ivar high: 最高价。
    :ivar low: 最低价。
    :ivar datetime: 开盘时间。
    :ivar vol: 成交量。
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
        
        :ivar open: 开仓价
        :vartype open: float
        :ivar close: 平仓价
        :vartype close: float
    """


    def __init__(self, buy_trans, sell_trans, quantity):
        self.open = buy_trans
        self.close = sell_trans
        self._quantity = quantity;

    def profit(self):
        """ 盈亏额  """
        direction = self.open.direction
        if direction == Direction.LONG:
            return (self.close.price - self.open.price) * self.open.quantity
        else:
            return (self.open.price - self.close.price) * self.open.quantity

    @property
    def quantity(self):
        """ 成交量 """
        return self._quantity

    @property
    def open_datetime(self):
        """ 开仓时间 """
        return self.open.datetime

    @property
    def open_price(self):
        """ 开仓价格 """
        return self.open.price

    @property
    def close_datetime(self):
        """ 平仓时间 """
        return self.close.datetime

    @property
    def close_price(self):
        """ 平仓价格 """
        return self.close.price

    @property
    def direction(self):
        """ 空头还是多头 """
        return self.open.direction

