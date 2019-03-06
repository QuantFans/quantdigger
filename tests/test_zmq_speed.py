# -*- coding: utf-8 -*-
##
# @file test_interactive.py
# @brief
# @author wondereamer
# @version 0.1
# @date 2016-08-07


import subprocess
import os
import time
from timeit import timeit

from quantdigger.util import gen_log as log
from quantdigger.util import project_dir
from quantdigger.event.rpc import EventRPCClient
from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.interaction.backend import Backend


backend_path = os.path.join(project_dir, "quantdigger", "interaction", "backend.py")

log.info("启动后台..")
backend = subprocess.Popen('python %s' % backend_path, shell=True)
time.sleep(1)


engine = ZMQEventEngine('WindowGate')
engine.start()
shell = EventRPCClient('test_shell', engine, Backend.SERVER_FOR_SHELL)


def func():
    shell.sync_call("test_speed")
    return


t = timeit('func()', 'from __main__ import func', number=100)
print(t)

subprocess.Popen.kill(backend)
a = raw_input("Any key to quit quantdigger.")
