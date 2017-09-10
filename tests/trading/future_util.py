#!/usr/bin/env python
# encoding: utf-8
import datetime

from quantdigger import settings

window_size = 0
capital = 20000000
OFFSET = 0.6
bt1 = datetime.datetime.strptime("09:01:00", "%H:%M:%S").time()
bt2 = datetime.datetime.strptime("09:02:00", "%H:%M:%S").time()
bt3 = datetime.datetime.strptime("09:03:00", "%H:%M:%S").time()
st1 = datetime.datetime.strptime("14:57:00", "%H:%M:%S").time()
st2 = datetime.datetime.strptime("14:58:00", "%H:%M:%S").time()
st3 = datetime.datetime.strptime("15:00:00", "%H:%M:%S").time()


def trade_closed_curbar(data, capital, long_margin, short_margin, volume_multiple, direction):
    """ 策略: 分钟线日内限价交易, 且当根bar成交
        买入点: [bt1, bt2, bt3]
        当天卖出点: [st1, st2]
        direction: 1表多头，-1表空头
        分别计算open, close两个时间点的可用资金和权益
    """
    unit = 1
    dts = []

    close_profit = 0
    equities = []
    cashes = []
    quantity = 0
    poscost = 0

    open_close_profit = 0
    open_equities = []
    open_cashes = []
    open_quantity = 0
    open_poscost = 0

    for dt, price in data.close.iteritems():
        open_price = data.open[dt]
        curtime = dt.time()
        if curtime in [bt1, bt2, bt3]:
            open_poscost = poscost
            open_quantity = quantity
            open_close_profit = close_profit
            poscost = (poscost * quantity + price *
                       (1 +direction * settings['future_commission']) * unit) / (quantity + unit)
            quantity += unit

        elif curtime == st1:
            assert(quantity == unit * 3)
            open_close_profit = close_profit
            open_quantity = quantity
            close_profit += direction * (price *
                                            (1 - direction * settings['future_commission']) -
                                            poscost) * 2 * unit * volume_multiple
            quantity -= 2 * unit
        elif curtime == st2:
            assert(quantity == unit * 1)
            open_close_profit = close_profit
            open_quantity = quantity
            close_profit += direction * (price *
                                            (1 - direction * settings['future_commission']) -
                                            poscost) * unit * volume_multiple
            quantity = 0
        else:
            # 非交易节点
            open_quantity = quantity
            open_poscost = poscost
            open_close_profit = close_profit

        if dt == data.index[-1]:
            # 强平现有持仓
            open_close_profit = close_profit
            open_quantity = quantity
            close_profit += direction * (price *
                                         (1 - direction * settings['future_commission']) -
                                         poscost) * quantity * volume_multiple
            quantity = 0

        margin = long_margin if direction == 1 else short_margin

        pos_profit = direction * (price - poscost) * volume_multiple * quantity  # 持仓盈亏
        posmargin = price * quantity * volume_multiple * margin
        equities.append(capital + close_profit + pos_profit)
        cashes.append(equities[-1] - posmargin)

        open_pos_profit = direction * (open_price - open_poscost) * volume_multiple * open_quantity
        open_posmargin = open_price * open_quantity * volume_multiple * margin
        open_equities.append(capital + open_close_profit + open_pos_profit)
        open_cashes.append(open_equities[-1] - open_posmargin)

        dts.append(dt)
    return equities, cashes, open_equities, open_cashes, dts


def entries_maked_nextbar(data):
    """ 寻找交易点，使交易在改点的下一根能成交(延迟成交) """
    buy_entries = []
    sell_entries = []
    short_entries = []
    cover_entries = []
    prehigh = data.high[0]
    predt = data.index[0]
    prelow = data.low[0]

    for dt, low in data.low.iteritems():
        if dt.date() == predt.date() and dt.time() < st1 and prelow - OFFSET >= low:
            buy_entries.append(predt)
        prelow = low
        predt = dt

    for dt, high in data.high.iteritems():
        if dt.date() == predt.date() and dt.time() < st1 and high - prehigh >= OFFSET:
            short_entries.append(predt)
        prehigh = high
        predt = dt

    for dt, high in data.high.iteritems():
        if dt.time() > bt3 and high - prehigh >= OFFSET:
            sell_entries.append(predt)
        prehigh = high
        predt = dt

    for dt, low in data.low.iteritems():
        if dt.time() > bt3 and prelow - low >= OFFSET:
            cover_entries.append(predt)
        prelow = low
        predt = dt
    return buy_entries, sell_entries, short_entries, cover_entries


def in_closed_nextbar(data, buy_entries, capital, long_margin, short_margin, volume_multiple, direction):
    """ 策略: 多头限价开仓且下一根bar成交
        买入点：[相关bar的最低点减去OFFSET]
        当天卖出点：st1
        假设：close那个时间点价格到达可成交位置。

              182  183  184
              下单 成交 正常
        open   o   s    o
        close  s   o    o
    """
    close_profit = 0    # 累计平仓盈亏
    equities = []
    dts = []
    cashes = []
    prelow = data.low[0]
    prehigh = data.high[0]
    trans_entries = list(map(lambda x: x + datetime.timedelta(minutes=1), buy_entries))
    quantity = 0
    poscost = 0
    UNIT = 1
    margin = long_margin if direction == 1 else short_margin

    open_poscost = 0
    open_quantity = 0
    pending_order_quantity = 0
    open_price = []
    open_close_profit = 0
    open_equities = []
    open_cashes = []
    num = 0
    for dt, low in data.low.iteritems():
        curtime = dt.time()
        close = data.close[dt]
        open_price = data.open[dt]
        if direction == 1:
            price = prelow - OFFSET
        else:
            price = prehigh + OFFSET
        if dt in trans_entries:
            # 开仓成交时间点
            open_poscost = poscost
            open_quantity = quantity
            open_close_profit = close_profit
            poscost = (poscost * quantity + price *
                       (1 + direction * settings['future_commission']) * UNIT) / (quantity + UNIT)
            quantity += UNIT
            pending_order_quantity = 1

        elif curtime == st1 or dt == data.index[-1]:
            # 平仓成交时间点
            open_close_profit = close_profit
            open_quantity = quantity
            close_profit += direction * (close * (1 - direction *
                                         settings['future_commission']) - poscost) * quantity * volume_multiple
            quantity = 0
            pending_order_quantity = 0
        else:
            # 非交易节点
            open_quantity = quantity
            open_poscost = poscost
            open_close_profit = close_profit
            pending_order_quantity = 0

        pos_profit = direction * (close - poscost) * volume_multiple * quantity
        equities.append(close_profit + pos_profit + capital)
        posmargin = close * quantity * volume_multiple * margin
        cashes.append(equities[-1] - posmargin)

        open_pos_profit = direction * (open_price - open_poscost) * volume_multiple * open_quantity
        pending_order_margin = price * pending_order_quantity * volume_multiple * margin
        open_equities.append(capital + open_close_profit + open_pos_profit)
        open_posmargin = open_price * open_quantity * volume_multiple * margin
        # 183 open点特殊处理
        open_cashes.append(open_equities[-1] - open_posmargin - pending_order_margin)
        if dt in trans_entries:
            # 算上未成交单的资金占用, 修改成交点的上一个cash
            # 182 close点特殊处理
            cashes[-2] -= price * volume_multiple * margin
        dts.append(dt)
        prelow = low
        prehigh = data.high[dt]
        num += 1
    return equities, cashes, open_equities, open_cashes, dts


def out_closed_nextbar(data, cover_entries, capital,
                       long_margin, short_margin,
                       volume_multiple, direction):
    """ 策略: 空头限价平仓且下一根bar成交
        买入点：[相关bar的最低点减去OFFSET]
        当天卖出点：st1

              下单 成交 正常
        open   o   o    o
        close  o   o    o
    """
    close_profit = 0    # 累计平仓盈亏
    equities = []
    cashes = []
    dts = []
    trans_entries = list(map(lambda x: x + datetime.timedelta(minutes=1), cover_entries))
    poscost = 0
    prelow = data.low[0]
    prehigh = data.high[0]
    margin = long_margin if direction == 1 else short_margin
    quantity = 0
    open_quantity = 0
    open_close_profit = 0
    open_cashes = []
    open_equities = []
    num = 0
    for dt, low in data.low.iteritems():
        price = data.close[dt]
        open_price = data.open[dt]

        # 开仓
        if dt.time() == bt1:
            open_close_profit = close_profit
            open_poscost = poscost
            poscost = price * (1 + direction * settings['future_commission'])
            open_quantity = quantity
            quantity = 1

        # 平仓
        elif poscost and dt in trans_entries:
            if direction == 1:
                price = prehigh + OFFSET
            else:
                price = prelow - OFFSET
            open_close_profit = close_profit
            close_profit += direction * quantity * (price *
                                                    (1 - direction * settings['future_commission']) -
                                                    poscost) * volume_multiple
            open_poscost = poscost
            open_quantity = quantity
            poscost = 0
            quantity = 0

        # 最后一根或者隔日, 强平现有持仓
        elif dt == data.index[-1] or dt.time() == st3:
            if quantity:
                open_close_profit = close_profit
                close_profit += direction * (price *
                                             (1 - direction * settings['future_commission']) -
                                             poscost) * volume_multiple * quantity

            open_poscost = poscost
            open_quantity = quantity
            poscost = 0
            quantity = 0
        else:
            open_quantity = quantity
            open_close_profit = close_profit
            open_poscost = poscost

        open_pos_profit = direction * (open_price - open_poscost) * volume_multiple * open_quantity
        open_posmargin = open_price * volume_multiple * margin * open_quantity

        pos_profit = direction * (price - poscost) * volume_multiple * quantity
        posmargin = price * volume_multiple * margin * quantity

        equities.append(close_profit + pos_profit + capital)
        open_equities.append(open_close_profit + open_pos_profit + capital)

        cashes.append(equities[-1] - posmargin)
        open_cashes.append(open_equities[-1] - open_posmargin)

        dts.append(dt)
        prelow = low
        prehigh = data.high[dt]
        num += 1
    return equities, cashes, open_equities, open_cashes, dts


def market_trade_closed_curbar(data, capital, long_margin, short_margin,
                               volume_multiple):
    """ 策略: 多空市价开仓且当根bar成交
        买入点：[bt1, bt2, bt3]
        当天卖出点：[st1, st2]
    """
    close_profit = 0
    equities = []
    dts = []
    cashes = []
    lquantity = 0
    squantity = 0
    lposcost = 0
    sposcost = 0

    open_close_profit = 0
    open_lposcost = 0
    open_sposcost = 0
    open_cashes = []
    open_equities = []
    open_lquantity = 0
    open_squantity = 0
    num = 0
    for index, row in data.iterrows():
        close = row['close']
        open = row['open']
        dt = index
        high, low = row['high'], row['low']
        curtime = dt.time()
        if curtime in [bt1, bt2, bt3]:
            # 开仓
            open_close_profit = close_profit
            open_lposcost = lposcost
            open_sposcost = sposcost
            open_lquantity = lquantity
            open_squantity = squantity
            lposcost = (lposcost * lquantity + high *
                        (1 + settings['future_commission'])) / (lquantity + 1)
            sposcost = (sposcost * squantity + low *
                        (1 - settings['future_commission']) * 2) / (squantity + 2)
            lquantity += 1
            squantity += 2

        elif curtime == st1:
            # 平仓
            assert(lquantity == 3)
            open_close_profit = close_profit
            open_lquantity = lquantity
            open_squantity = squantity
            open_lposcost = lposcost
            open_sposcost = sposcost
            close_profit += (low * (1 - settings['future_commission']) -
                                lposcost) * 2 * volume_multiple
            lquantity = 1
            assert(squantity == 6)
            close_profit -= (high * (1 + settings['future_commission']) -
                                sposcost) * 4 * volume_multiple
            squantity = 2
        elif curtime == st2:
            # 平仓
            assert(lquantity == 1)
            open_close_profit = close_profit
            open_lquantity = lquantity
            open_squantity = squantity
            open_lposcost = lposcost
            open_sposcost = sposcost
            close_profit += (low * (1 - settings['future_commission']) -
                                lposcost) * volume_multiple
            lquantity = 0
            close_profit -= (high * (1 + settings['future_commission']) -
                                sposcost) * 2 * volume_multiple
            squantity = 0

        else:
            open_close_profit = close_profit
            open_lquantity = lquantity
            open_squantity = squantity
            open_lposcost = lposcost
            open_sposcost = sposcost

        if dt == data.index[-1]:
            # 强平现有持仓
            close_profit += (close * (1 - settings['future_commission']) -
                             sposcost) * lquantity * volume_multiple
            close_profit -= (close * (1 + settings['future_commission']) -
                             sposcost) * squantity * volume_multiple
            lquantity = 0
            squantity = 0
        pos_profit = (close - lposcost) * lquantity * volume_multiple
        pos_profit -= (close - sposcost) * squantity * volume_multiple
        posmargin = close * lquantity * long_margin * volume_multiple
        posmargin += close * squantity * short_margin * volume_multiple
        open_pos_profit = (open - open_lposcost) * open_lquantity * volume_multiple
        open_pos_profit -= (open - open_sposcost) * open_squantity * volume_multiple
        open_posmargin = open * open_lquantity * long_margin * volume_multiple
        open_posmargin += open * open_squantity * short_margin * volume_multiple
        equities.append(capital + close_profit + pos_profit)
        open_equities.append(capital + open_close_profit + open_pos_profit)
        cashes.append(equities[-1] - posmargin)
        open_cashes.append(open_equities[-1] - open_posmargin)
        dts.append(dt)
        num += 1
    return equities, cashes, open_equities, open_cashes, dts
