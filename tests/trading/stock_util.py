#!/usr/bin/env python
# encoding: utf-8

import datetime
import six
from quantdigger import settings
from copy import deepcopy

window_size = 0
OFFSET = 0.6
buy1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
buy2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
buy3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
sell1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
sell2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
sell3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()


def trade_closed_curbar(data, capital, long_margin, short_margin, volume_multiple, direction):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [buy1, buy2, buy3]
        当天卖出点: [sell1, sell2]

        保证不能当天卖。
    """
    assert(volume_multiple == 1 and long_margin == 1)
    UNIT = 1
    date_quantity= { }
    poscost = 0
    close_profit = 0
    equities = [] # 累计平仓盈亏
    dts = []
    cashes = []

    open_poscost = 0
    open_cashes = []
    open_equities = []
    open_close_profit = 0
    num = 0
    for curdt, curprice in data.close.iteritems():
        open_price = data.open[curdt]
        curtime = curdt.time()
        curdate = curdt.date()
        if curtime in [buy1, buy2, buy3]:
            # 开仓
            open_close_profit = close_profit
            open_quantity = sum(date_quantity.values())
            open_poscost = poscost

            date_quantity.setdefault(curdate, 0)
            quantity = sum(date_quantity.values())
            poscost = (poscost * quantity + curprice *
                       (1 + direction * settings['stock_commission'])*UNIT) / (quantity+UNIT)
            date_quantity[curdate] += UNIT
        elif curtime == sell1:
            for posdate, quantity in six.iteritems(date_quantity):
                if posdate < curdate and quantity > 0:
                    open_close_profit = close_profit
                    open_quantity = sum(date_quantity.values())
                    close_profit += direction * (curprice*(1 - direction * settings['stock_commission'])-poscost) *\
                                    2*UNIT * volume_multiple
                    date_quantity[posdate] -= 2*UNIT
                elif posdate > curdate:
                    assert(False)
        elif curtime == sell2:
            for posdate, quantity in six.iteritems(date_quantity):
                if posdate < curdate and quantity > 0:
                    open_close_profit = close_profit
                    open_quantity = sum(date_quantity.values())
                    close_profit += direction * (curprice*(1 - direction * settings['stock_commission'])-poscost) *\
                                    UNIT * volume_multiple
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
            close_profit += direction * (curprice*(1 - direction * settings['stock_commission'])-poscost) *\
                            quantity * volume_multiple
            date_quantity.clear()

        quantity = sum(date_quantity.values())
        pos_profit = direction * (curprice - poscost) * quantity * volume_multiple
        posmargin = curprice * quantity * volume_multiple * long_margin
        open_pos_profit = direction * (open_price - open_poscost) * open_quantity * volume_multiple
        open_posmargin = open_price * open_quantity * volume_multiple * long_margin

        equities.append(capital+close_profit+pos_profit)
        cashes.append(equities[-1]-posmargin)
        open_equities.append(capital + open_close_profit + open_pos_profit)
        open_cashes.append(open_equities[-1]-open_posmargin)
        dts.append(curdt)
        num += 1
    return equities, cashes, open_equities, open_cashes, dts


def buy_monday_sell_friday(data, capital, long_margin, volume_multiple):
    """ 策略: 多头限价开仓且当根bar成交
        买入点: [buy1, buy2, buy3]
        当天卖出点: [sell1, sell2]
    """
    assert(volume_multiple == 1 and long_margin == 1)
    UNIT = 1
    poscost = 0
    quantity = 0
    close_profit = 0
    equities = {} # 累计平仓盈亏
    dts = []
    cashes = { }
    for curdt, curprice in data.close.iteritems():
        pos_profit = 0
        weekday = curdt.weekday()
        if weekday == 0:
            poscost = (poscost * quantity + curprice*(1+settings['stock_commission'])*UNIT) / (quantity+UNIT)
            quantity += UNIT
        else:
            if weekday == 4 and quantity>0:
                close_profit += (curprice*(1-settings['stock_commission'])-poscost) *\
                                quantity * volume_multiple
                quantity = 0
        pos_profit += (curprice - poscost) * quantity * volume_multiple
        equities[curdt] = capital+close_profit+pos_profit
        posmargin = curprice * quantity * volume_multiple * long_margin
        cashes[curdt] = capital+close_profit+pos_profit -posmargin
        dts.append(curdt)
    return equities, cashes, dts
