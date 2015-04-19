import dependency
import util
import os
import re

result = os.popen('python setup.py install').readlines()
util.printCommandResult(result)


result = os.popen('pip -V').read()
reobj = re.compile("pip.+from.+", re.IGNORECASE)
if reobj.search(result):
	print('pip has be installed')
else:
	print('pip no install')
	dependency.pip_download_install()


dependency.handle_dependency()
