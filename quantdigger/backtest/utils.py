__author__ = 'Wenwei Huang'


from PyQt4 import QtCore
import os, sys

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


def sysopen(filename):
    if os.name == 'nt':
        os.startfile(filename)
    elif sys.platform.startswith('darwin'):
        os.system('open %s' % filename)
    elif os.name == 'posix':
        os.system('xdg-open %s' % filename)
