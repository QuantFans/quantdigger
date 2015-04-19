import os
import platform
import util
def do_windows_dependency():
	url = 'http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-msvc.zip'
	target = 'ta-lib-0.4.0-msvc.zip'
	util.download(url,target)
	util.decompressZip(target,'C:\\')

def do_linux_dependency():
	url = 'http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz'
	target = 'ta-lib-0.4.0-src.tar.gz'
	util.download(url,target)
	util.decompress(target,'.')
	os.chdir('ta-lib-0.4.0-src')
	print('==========configure ta-lib============')
	result = os.popen('./configure').readlines()
	util.printCommandResult(result)
	print('==========configure end   ============')
	print('==========make ta-lib ================')
	result = os.popen('make').readlines()
	util.printCommandResult(result)
	print('==========make ta-lib end ============')
	print('==========make install tab-lib =======')
	result = os.popen('make install').readlines()
	util.printCommandResult(result)
	print('==========make install tab-lib end =======')

def do_darwin_dependency():
	result = os.popen('brew install ta-lib').readlines()
	util.printCommandResult(result)

def create_dependencies():
	requirements = 'numpy == 1.8.0\npandas == 0.14.1\npython-dateutil == 1.5\nmatplotlib == 1.1.0\nTA-Lib == 0.4.8'
	file = open('requirements.txt','w')
	file.write(requirements)
	file.close()
	
def handle_dependency():
	platform_name = platform.system()
	if (platform_name == "Windows"):
		do_windows_dependency()
	elif (platform_name == "Linux"):
		do_linux_dependency()
	elif (platform_name == "Darwin"):
		do_darwin_dependency()
	else:
		print('unknown platform')
	print('pip install -r requirements.txt')
	create_dependencies()
	result = os.popen('pip install -r requirements.txt').readlines()
	util.printCommandResult(result)

def pip_download_install():
        url = 'https://pypi.python.org/packages/source/p/pip/pip-6.0.8.tar.gz'
        target = 'pip-6.0.8.tar.gz'
        targetdir = 'pip-6.0.8'
        print('============ downloading ' + target + ' from:' + url)
        util.download(url,target)
        print('============ extracting ' + target)
        util.decompress(target,'.')
        os.chdir(targetdir)
        print('============ installing pip')
        cmdResult = os.popen('python setup.py install').readlines()
        util.printCommandResult(cmdResult)
        print('============ installed,plese add pip to your path')
