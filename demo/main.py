# -*- coding: utf-8 -*-

from six.moves import input
import subprocess
import time
import os
from quantdigger.util import gen_log as log
from quantdigger.util import project_dir

ui_path = os.path.join(project_dir, "quantdigger", "widgets", "mplotwidgets", "mainwindow.py" )
shell_path = os.path.join(project_dir, "quantdigger", "interaction", "ipython_config.py")
backend_path = os.path.join(project_dir, "quantdigger", "interaction", "backend.py")

log.info("启动后台..")
backend = subprocess.Popen('python %s' % backend_path, shell=True)
time.sleep(1)

log.info("启动主窗口..")
#mainwindow = subprocess.Popen('python %s' % ui_path, shell=True)
mainwindow = subprocess.Popen('python %s > log' % ui_path, shell=True)
time.sleep(1)

log.info("启动ipython..")
shell = subprocess.call('ipython --config=%s' % shell_path, shell=True)
###notebook = subprocess.call('jupyter notebook --config=shell.py', shell=True)
###six.print_(mainwindow.pid)

input("Any key to quit quantdigger.")
subprocess.Popen.kill(mainwindow)
subprocess.Popen.kill(backend)
