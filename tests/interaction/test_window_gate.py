# -*- coding: utf-8 -*-
##
# @file test_window_gate.py
# @brief 
# @author wondereamer
# @version 0.1
# @date 2016-08-07

import json
import time, sys
import unittest

from quantdigger.config import ConfigInteraction
from quantdigger.event.rpc import EventRPCClient
from quantdigger.interaction.backend import backend
from quantdigger.widgets.mplotwidgets.mainwindow import  mainwindow


class TestWindowGate(object):
    gate = EventRPCClient('test_window_gate', mainwindow._gate._engine,
                            ConfigInteraction.ui_server_for_shell)


    def test_get_all_contracts(self):
        ret = self.gate.sync_call("get_all_contracts")
        print "***********" 
        #print json.loads(ret)
        print ret
        print "***********" 

    #def test_get_pcontract(self):
        #ret = self.shell.sync_call("get_pcontract", {
            #'str_pcontract': 'BB.TEST-1.MINUTE'
            #})
        #print json.loads(ret).keys()
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
    t = TestWindowGate()
    t.test_get_all_contracts()
