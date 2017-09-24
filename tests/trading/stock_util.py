#!/usr/bin/env python
# encoding: utf-8

import datetime
import six
from quantdigger import settings

window_size = 0
OFFSET = 0.6
capital = 20000000
bt1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
bt2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
bt3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
st1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
st2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
st3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()


def trade_closed_curbar(data, capital, long_margin, short_margin, volume_multiple, direction):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [bt1, bt2, bt3]
        当天卖出点: [st1, st2]

        保证不能当天卖。
    """
    assert(volume_multiple == 1 and long_margin == 1)
    UNIT = 1
    date_quantity= {}
    poscost = 0
    close_profit = 0
    equities = []
    dts = []
    cashes = []

    open_poscost = 0
    open_cashes = []
    open_equities = []
    open_close_profit = 0
    open_quantity = 0
    num = 0
    for curdt, curprice in data.close.iteritems():
        open_price = data.open[curdt]
        curtime = curdt.time()
        curdate = curdt.date()
        if curtime in [bt1, bt2, bt3]:
            # 开仓
            open_close_profit = close_profit
            open_quantity = sum(date_quantity.values())
            open_poscost = poscost

            date_quantity.setdefault(curdate, 0)
            quantity = sum(date_quantity.values())
            poscost = (poscost * quantity + curprice *
                       (1 + direction * settings['stock_commission']) * UNIT) / (quantity + UNIT)
            date_quantity[curdate] += UNIT
        elif curtime == st1:
            for posdate, quantity in six.iteritems(date_quantity):
                if posdate < curdate and quantity > 0:  # 隔日交易
                    open_close_profit = close_profit
                    open_quantity = sum(date_quantity.values())
                    close_profit += direction * (curprice * (1 - direction *
                                    settings['stock_commission']) - poscost) * 2 * UNIT * volume_multiple
                    date_quantity[posdate] -= 2 * UNIT
                elif posdate > curdate:
                    assert(False)
        elif curtime == st2:
            for posdate, quantity in six.iteritems(date_quantity):
                if posdate < curdate and quantity > 0:
                    open_close_profit = close_profit
                    open_quantity = sum(date_quantity.values())
                    close_profit += direction * (curprice * (1 - direction *
                                        settings['stock_commission']) - poscost) * UNIT * volume_multiple
                    date_quantity[posdate] -= UNIT
                    assert(date_quantity[posdate] == 0)
                elif posdate > curdate:
                    assert(False)
        else:
            open_quantity = sum(date_quantity.values())
            open_poscost = poscost
            open_close_profit = close_profit

        if curdt == data.index[-1]:
            # 强平现有持仓
            open_close_profit = close_profit
            open_quantity = sum(date_quantity.values())
            quantity = sum(date_quantity.values())
            close_profit += direction * (curprice * (1 - direction * settings['stock_commission']) -
                                         poscost) * quantity * volume_multiple
            date_quantity.clear()

        quantity = sum(date_quantity.values())
        pos_profit = direction * (curprice - poscost) * quantity * volume_multiple
        posmargin = curprice * quantity * volume_multiple * long_margin
        open_pos_profit = direction * (open_price - open_poscost) * open_quantity * volume_multiple
        open_posmargin = open_price * open_quantity * volume_multiple * long_margin

        equities.append(capital + close_profit + pos_profit)
        cashes.append(equities[-1] - posmargin)
        open_equities.append(capital + open_close_profit + open_pos_profit)
        open_cashes.append(open_equities[-1] - open_posmargin)
        dts.append(curdt)
        num += 1
    return equities, cashes, open_equities, open_cashes, dts


def buy_monday_sell_friday(data, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        周一买，周五卖
    """
    assert(volume_multiple == 1 and long_margin == 1)
    UNIT = 1
    poscost = 0
    quantity = 0
    close_profit = 0
    equities = {}
    dts = []
    cashes = {}

    open_poscost = 0
    open_cashes = {}
    open_equities = {}
    open_close_profit = 0
    open_quantity = 0
    num = 0
    for curdt, curprice in data.close.iteritems():
        pos_profit = 0
        open_price = data.open[curdt]
        weekday = curdt.weekday()
        if weekday == 0:
            open_poscost = poscost
            open_quantity = quantity
            open_close_profit = close_profit
            poscost = (poscost * quantity + curprice * (1 + settings['stock_commission']) * UNIT)\
                / (quantity + UNIT)
            quantity += UNIT
        elif weekday == 4 and quantity > 0:
            open_close_profit = close_profit
            open_quantity = quantity
            close_profit += (curprice * (1 - settings['stock_commission']) - poscost) * quantity * volume_multiple
            quantity = 0
        else:
            open_close_profit = close_profit
            open_poscost = poscost
            open_quantity = quantity

        pos_profit = (curprice - poscost) * quantity * volume_multiple
        equities[curdt] = capital + close_profit + pos_profit
        posmargin = curprice * quantity * volume_multiple * long_margin
        cashes[curdt] = capital + close_profit + pos_profit - posmargin
        dts.append(curdt)

        open_pos_profit = (open_price - open_poscost) * open_quantity * volume_multiple
        open_equities[curdt] = capital + open_close_profit + open_pos_profit

        open_posmargin = open_price * open_quantity * volume_multiple * long_margin
        open_cashes[curdt] = capital + open_close_profit + open_pos_profit - open_posmargin
        num += 1
    return equities, cashes, open_equities, open_cashes, dts
