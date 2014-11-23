__author__ = 'Wenwei Huang'


from PyQt4 import QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

fromUtf8 = _fromUtf8

class WindowSize(object):
    ONEDAY = 'ONEDAY'
    FIVEDAY = 'FIVEDAY'
    ONEMONTH = 'ONEMONTH'
    THREEMONTH = 'THREEMONTH'
    SIXMONTH = 'SIXMONTH'
    ONEYEAR = 'ONEYEAR'
    TWOYEAR = 'TWOYEAR'
    FIVEYEAR = 'FIVEYEAR'
    MAX = 'MAX'

