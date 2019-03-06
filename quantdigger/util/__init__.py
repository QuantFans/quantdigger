# -*- coding: utf8 -*-

import six
import datetime
import os
import time
import sys

from .log import gen_log as log
MAX_DATETIME = datetime.datetime(2100, 1, 1)

project_dir = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
source_dir = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


if sys.version_info >= (3,):
    py = 3
else:
    py = 2

def deprecated(f):
    def ff(*args, **kwargs):
        six.print_('{0} is deprecated!'.format(str(f)))
        return f(*args, **kwargs)
    return ff

#def api(method):
    #def wrapper(*args, **kwargs):
        #rst = method(*args, **kwargs)
        #return rst
    #return wrapper


def time2int(t):
    """ datetime转化为unix毫秒时间。 """
    epoch = int(time.mktime(t.timetuple()) * 1000)
    return epoch


def int2time(tf):
    return datetime.datetime.fromtimestamp(float(tf) / 1000)
