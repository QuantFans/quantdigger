# -*- coding: utf-8 -*-
##
# @file test_shell.py
# @brief
# @author wondereamer
# @version 0.1
# @date 2016-08-07

import six
import sys
import unittest

from quantdigger.interaction.backend import Backend
from quantdigger.interaction.shell import shell


backend = Backend()
class TestShell(object):
    """ WindowGate call backend """
    def __init__(self):
        pass
        #self._engine = ZMQEventEngine('TestShell')
        #self._engine.start()
        #self._gate = EventRPCClient('TestShell', self._engine,
                                #ConfigInteraction.ui_server_for_shell)
        #self._backend = EventRPCClient('TestShell', self._engine,
                                #ConfigInteraction.backend_server_for_shell)


    def test_get_all_contracts(self):
        six.print_(shell.get_all_contracts())



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
    import time
    t = TestShell()
    t.test_get_all_contracts()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ## @BUG 如果异常退出，系统可能遗留连接，导致多次回调。
        backend.stop()
        sys.exit(0)
