# -*- coding: utf8 -*-

import six
import datetime
import logbook
import os
import time
import sys

from .log import gen_log

logbook.StreamHandler(sys.stdout).push_application()
elogger = logbook.Logger('engine')
dlogger = logbook.Logger('data')
mlogger = gen_log
gen_logger = logbook.Logger('general')
rlogger = logbook.Logger('runtime')


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

gen_logger.level = logbook.INFO

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
