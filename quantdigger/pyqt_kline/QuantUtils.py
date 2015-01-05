# -*- coding: utf-8 -*-

__author__ = 'TeaEra'

from PyQt4 import QtGui
from PyQt4 import QtCore
import os
import pandas as pd
import random

################################################################################
# Already copied;


try:
    from_utf8 = QtCore.QString.fromUtf8
except AttributeError:
    def from_utf8(s):
        return s


try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


################################################################################


def csv2frame(file_name):
    """
    读取CSV文件到DataFrame
    """
    try:
        print "*******", file_name
        data = pd.read_csv(file_name, index_col=0, parse_dates=True)
        data['islong'] = False if file_name.endswith("_.csv") else True
        assert data.index.is_unique
    except Exception, e:
        print u"**Warning: File \"%s\" doesn't exist!" % file_name
        data = None
    return data


def get_k_line_data_by_path(path):
    """
    Get the k-line data by file-path;

    :param path:
    :return:
    """
    return csv2frame(unicode(path))


def get_min_and_max_price(k_line_data):
    """
    Get minimum & maximum of price for y-axis;

    :param k_line_data:
    :return:
    """
    if len(k_line_data) <= 0:
        return 0, 0
    first_entry = k_line_data.ix[k_line_data.index[0]]
    first_list = list()
    first_list.append(float(first_entry['open']))
    first_list.append(float(first_entry['close']))
    first_list.append(float(first_entry['high']))
    first_list.append(float(first_entry['low']))
    the_min = min(first_list)
    the_max = max(first_list)
    for eachIndex in range(len(k_line_data)):
        each_entry = k_line_data.ix[eachIndex]
        temp_list = list()
        temp_list.append(float(each_entry['open']))
        temp_list.append(float(each_entry['close']))
        temp_list.append(float(each_entry['high']))
        temp_list.append(float(each_entry['low']))
        temp_min = min(temp_list)
        temp_max = max(temp_list)
        if temp_min < the_min:
            the_min = temp_min
        if temp_max > the_max:
            the_max = temp_max
    return the_min, the_max


def get_random_series_from(data_frame):
    #
    size = len(data_frame)
    random_idx = random.randint(0, size-1)
    #
    return data_frame.ix[random_idx]


def get_random_series_list_from(data_frame):
    #
    size = len(data_frame)
    random_idx = random.randint(0, size-1)
    #
    return data_frame[random_idx:random_idx+1]
