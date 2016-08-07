# -*- coding: utf-8 -*-
##
# @file test_interactive.py
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

class TestBackend(unittest.TestCase):

    ui = EventRPCClient('test_ui', backend._engine,
                            ConfigInteraction.backend_server_for_ui)
    shell = EventRPCClient('test_shell', backend._engine,
                                ConfigInteraction.backend_server_for_shell)


    def test_get_all_contracts(self):
        ret = self.ui.sync_call("get_all_contracts")
        ret = self.shell.sync_call("get_all_contracts")
        print "***********" 
        print json.loads(ret)
        print "***********" 

    def test_get_pcontract(self):
        ret = self.ui.sync_call("get_pcontract", {
            'str_pcontract': 'BB.TEST-1.MINUTE'
            })
        ret = self.shell.sync_call("get_pcontract", {
            'str_pcontract': 'BB.TEST-1.MINUTE'
            })
        print json.loads(ret).keys()
        return



if __name__ == '__main__':
    unittest.main()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ## @BUG 如果异常退出，系统可能遗留连接，导致多次回调。
        backend.stop()
        sys.exit(0)
