import dependency
import util
import os
import re

# install quantdigger
print("----------- install QuantDigger --------------" )
result = os.popen('python setup.py install').readlines()
util.printCommandResult(result)


print("----------- install pip --------------" )
result = os.popen('pip -V').read()
reobj = re.compile("pip.+from.+", re.IGNORECASE)
if reobj.search(result):
	print('pip has be installed')
else:
	print('pip no install')
	dependency.pip_download_install()

print("----------- install dpendencies --------------" )
dependency.handle_dependency()

