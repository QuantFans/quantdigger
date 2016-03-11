# -*- coding: utf-8 -*-


class QError(Exception):
    msg = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.message = str(self)

    def __str__(self):
        msg = self.msg.format(**self.kwargs)
        return msg

    __unicode__ = __str__
    __repr__ = __str__


class TradingError(QError):
    """
    """
    msg = "交易警告：{err}"


class DataFormatError(QError):
    """
    """
    msg = "{type}--错误的数据格式！"


class DataFieldError(QError):
    """
    """
    msg = "错误的数据字段: {error_fields}\n正确的字段为: {right_fields} "


class FileDoesNotExist(QError):
    """
    当本地文件不存在的时候触发。
    """
    msg = "不存在文件:{file}"


class PeriodTypeError(QError):
    msg = "不存在该周期！ -- {period}"


class DataAlignError(QError):
    msg = "数据没有对齐！"


class SeriesIndexError(QError):
    msg = "序列变量索引越界！"


class BreakConstError(QError):
    msg = "不能对常量赋值！"


class ArgumentError(QError):
    msg = "参数错误！"


class WrongDataForTransform(QError):
    """
    Raised whenever a rolling transform is called on an event that
    does not have the necessary properties.
    """
    msg = "{transform} requires {fields}. Event cannot be processed."


class UnsupportedSlippageModel(QError):
    """
    Raised if a user script calls the override_slippage magic
    with a slipage object that isn't a VolumeShareSlippage or
    FixedSlipapge
    """
    msg = """
You attempted to override slippage with an unsupported class. \
Please use VolumeShareSlippage or FixedSlippage.
""".strip()


class OverrideSlippagePostInit(QError):
    # Raised if a users script calls override_slippage magic
    # after the initialize method has returned.
    msg = """
You attempted to override slippage outside of `initialize`. \
You may only call override_slippage in your initialize method.
""".strip()


class RegisterTradingControlPostInit(QError):
    # Raised if a user's script register's a trading control after initialize
    # has been run.
    msg = """
You attempted to set a trading control outside of `initialize`. \
Trading controls may only be set in your initialize method.
""".strip()


class UnsupportedCommissionModel(QError):
    """
    Raised if a user script calls the override_commission magic
    with a commission object that isn't a PerShare, PerTrade or
    PerDollar commission
    """
    msg = """
You attempted to override commission with an unsupported class. \
Please use PerShare or PerTrade.
""".strip()


class OverrideCommissionPostInit(QError):
    """
    Raised if a users script calls override_commission magic
    after the initialize method has returned.
    """
    msg = """
You attempted to override commission outside of `initialize`. \
You may only call override_commission in your initialize method.
""".strip()


class TransactionWithNoVolume(QError):
    """
    Raised if a transact call returns a transaction with zero volume.
    """
    msg = """
Transaction {txn} has a volume of zero.
""".strip()


class TransactionWithWrongDirection(QError):
    """
    Raised if a transact call returns a transaction with a direction that
    does not match the order.
    """
    msg = """
Transaction {txn} not in same direction as corresponding order {order}.
""".strip()


class TransactionWithNoAmount(QError):
    """
    Raised if a transact call returns a transaction with zero amount.
    """
    msg = """
Transaction {txn} has an amount of zero.
""".strip()


class TransactionVolumeExceedsOrder(QError):
    """
    Raised if a transact call returns a transaction with a volume greater than
the corresponding order.
    """
    msg = """
Transaction volume of {txn} exceeds the order volume of {order}.
""".strip()


class UnsupportedOrderParameters(QError):
    """
    Raised if a set of mutually exclusive parameters are passed to an order
    call.
    """
    msg = "{msg}"


class BadOrderParameters(QError):
    """
    Raised if any impossible parameters (nan, negative limit/stop)
    are passed to an order call.
    """
    msg = "{msg}"


class OrderDuringInitialize(QError):
    """
    Raised if order is called during initialize()
    """
    msg = "{msg}"


class TradingControlViolation(QError):
    """
    Raised if an order would violate a constraint set by a TradingControl.
    """
    msg = """
Order for {amount} shares of {sid} violates trading constraint {constraint}.
""".strip()


class IncompatibleHistoryFrequency(QError):
    """
    Raised when a frequency is given to history which is not supported.
    At least, not yet.
    """
    msg = """
Requested history at frequency '{frequency}' cannot be created with data
at frequency '{data_frequency}'.
""".strip()
