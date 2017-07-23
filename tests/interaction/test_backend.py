# -*- coding: utf-8 -*-
##
# @file test_interactive.py
# @brief
# @author wondereamer
# @version 0.1
# @date 2016-08-07

import six
import json
import time, sys
import unittest

from quantdigger.event.rpc import EventRPCClient
from quantdigger.interaction.backend import Backend

backend = Backend()

class TestBackend(unittest.TestCase):

    ui = EventRPCClient('test_ui', backend._engine,
                            backend.SERVER_FOR_UI)
    shell = EventRPCClient('test_shell', backend._engine,
                                backend.SERVER_FOR_SHELL)


    def test_get_all_contracts(self):
        ret = self.ui.sync_call("get_all_contracts")
        ret = self.shell.sync_call("get_all_contracts")
        six.print_("***********" )
        six.print_(ret)
        six.print_("***********" )

    def test_get_pcontract(self):
        ret = self.ui.sync_call("get_pcontract", {
            'str_pcontract': 'BB.TEST-1.MINUTE'
            })
        ret = self.shell.sync_call("get_pcontract", {
            'str_pcontract': 'BB.TEST-1.MINUTE'
            })
        six.print_(json.loads(ret).keys())
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
