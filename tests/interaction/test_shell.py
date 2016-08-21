# -*- coding: utf-8 -*-
##
# @file test_shell.py
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
from quantdigger.event.eventengine import ZMQEventEngine


class TestShellCallWindowGate(object):
    """ WindowGate call backend """
    def __init__(self):
        self._engine = ZMQEventEngine('TestShell')
        self._engine.start()
        self.gate = EventRPCClient('TestShell', self._engine,
                                ConfigInteraction.ui_server_for_shell)


    def test_get_all_contracts(self):
        ret = self.gate.sync_call("get_all_contracts")
        print "***********" 
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
    t = TestShellCallWindowGate()
    t.test_get_all_contracts()
