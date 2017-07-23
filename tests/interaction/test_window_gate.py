# -*- coding: utf-8 -*-
##
# @file test_window_gate.py
# @brief
# @author wondereamer
# @version 0.1
# @date 2016-08-07

import six
import json
import time, sys
import unittest

from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.interaction.backend import Backend
from quantdigger.widgets.mplotwidgets.mainwindow import  mainwindow


backend = Backend()
class TestWindowGateCallBackend(object):
    """ WindowGate call backend """

    def __init__(self):
        self.engine = ZMQEventEngine('TestWindowGate')
        self.engine.start()
        self.gate = mainwindow._gate

    #def test_get_all_contracts(self):
        #ret = self.gate.sync_call("get_all_contracts")
        #six.print_("***********" )
        ##six.print_(json.loads(ret))
        #six.print_(ret)
        #six.print_("***********" )

    def test_get_all_contracts(self):
        ret = self.gate.get_all_contracts()
        six.print_("***********" )
        six.print_(ret)
        six.print_("***********" )

    def test_get_all_pcontracts(self):
        ret = self.gate.get_all_pcontracts()
        six.print_("***********" )
        six.print_(ret)
        six.print_("***********" )

    #def test_get_pcontract(self):
        #ret = self.shell.sync_call("get_pcontract", {
            #'str_pcontract': 'BB.TEST-1.MINUTE'
            #})
        #six.print_(json.loads(ret).keys())
        #return



if __name__ == '__main__':
    #unittest.main()
    #try:
        #while True:
            #time.sleep(1)
    #except KeyboardInterrupt:
        ### @BUG 如果异常退出，系统可能遗留连接，导致多次回调。
        #backend.stop()
        #sys.exit(0)
    t = TestWindowGateCallBackend()
    t.test_get_all_contracts()
    t.test_get_all_pcontracts()
