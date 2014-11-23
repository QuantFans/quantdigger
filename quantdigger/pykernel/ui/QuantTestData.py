# -*- coding: utf-8 -*-

__author__ = 'TeaEra'

################################################################################


class AllDataForTest(object):
    """
    All prepared data:
      - header info for 3 tabs;
      - model data for tab 0;
      - updated model data for tab 0;
    """

    @staticmethod
    def get_header_info0():
        return [
            "期初权益", "当前权益", "可用资金", "平仓盈亏",
            "持仓盈亏", "总盈亏", "持仓保证金", "资金风险率"
        ]

    @staticmethod
    def get_header_info1():
        return [
            "成交编号", "合约", "买卖", "开平", "成交价格",
            "成交手数", "成交时间", "报单编号", "成交类型", "投保", "交易所"
        ]

    @staticmethod
    def get_header_info2():
        return [
            "文华码", "合约名称", "涨幅%", "开盘", "最高", "最低",
            "最新", "涨跌", "买价", "买量", "卖价", "卖量", "现量",
            "增仓", "成交量", "持仓量", "日增仓", "结算", "昨结算", "昨收"
        ]

    @staticmethod
    def get_model_data0():
        return [
            ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8'],
            ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8'],
            ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'],
            ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8'],
            ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8'],
            ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8'],
            ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8'],
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'],
            ['i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8']
        ]

    @staticmethod
    def get_updated_model_data0():
        return [
            ['a1u', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8'],
            ['b1', 'b2u', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8'],
            ['c1', 'c2', 'c3u', 'c4', 'c5', 'c6', 'c7', 'c8'],
            ['d1', 'd2', 'd3', 'd4u', 'd5', 'd6', 'd7', 'd8'],
            ['e1', 'e2', 'e3', 'e4', 'e5u', 'e6', 'e7', 'e8'],
            ['f1', 'f2', 'f3', 'f4', 'f5', 'f6u', 'f7', 'f8'],
            ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7u', 'g8'],
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8u'],
            ['i1u', 'i2u', 'i3', 'i4u', 'i5', 'i6', 'i7', 'i8u']
        ]