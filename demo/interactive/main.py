# -*- coding: utf-8 -*-
import subprocess
import time

print("启动后台..")
gate = subprocess.Popen('python backend.py', shell=True)
time.sleep(1)
print("启动主窗口..")
mainwindow = subprocess.Popen('python mainwindow.py', shell=True)
time.sleep(1)
print("启动ipython..")
ipython = subprocess.call('ipython --config=shell.py', shell=True)
#notebook = subprocess.call('jupyter notebook --config=shell.py', shell=True)
#print mainwindow.pid
raw_input("Any key to quit.")
subprocess.Popen.kill(mainwindow)
subprocess.Popen.kill(gate)
#subprocess.Popen.kill(ipython)
