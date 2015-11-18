import os
import platform
import util
def install_talib_for_windows():
	#url = 'http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-msvc.zip'
	#target = 'ta-lib-0.4.0-msvc.zip'
	#util.download(url,target)
	#util.decompressZip(target,'C:\\')
        cmd = 'pip install quantdigger\lib\TA_Lib-0.4.9-cp27-none-win_amd64.whl'
        result = os.popen(cmd).readlines()
        util.printCommandResult(result)

def install_talib_for_linux():
	url = 'http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz'
	target = 'ta-lib-0.4.0-src.tar.gz'
	util.download(url,target)
	util.decompress(target,'.')
	os.chdir('ta-lib')
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

def install_talib_for_Darwin():
	result = os.popen('brew install ta-lib').readlines()
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

def create_dependencies(platform):
    requirements = ''
    libs = [ ('numpy', 'numpy'),
             ('pandas', 'pandas'),
             ('dateutil', 'python-dateutil'),
             ('matplotlib', 'matplotlib'),
             ('logbook', 'logbook')
#             ('talib' , 'TA-Lib == 0.4.8') 
    ]
    if platform != 'Windows':
        libs.append(('talib', 'TA-Lib == 0.4.8'))
    for lib in libs:
        try:
            __import__(lib[0])
            print lib[0], "already installed!"
        except ImportError:
            requirements += '%s\n' % lib[1]
    if requirements:
        file = open('requirements.txt','w')
        file.write(requirements)
        file.close()
    return requirements

def handle_dependency():
    """docstring for fn""" 
    platform_name = platform.system()
    try:
        if platform_name == 'Windows':
            install_talib_for_windows() 
        elif platform_name == 'Linux':
            install_talib_for_linux() 
        elif platform_name == 'Darwin':
            install_talib_for_Darwin() 
        else:
            print('Failed to install ta-lib!')
    except Exception, e:
        print('Failed to install ta-lib!')
        print(e)

    dependencies = create_dependencies(platform_name)
    if dependencies:
        print('pip install -r requirements.txt')
        print(dependencies)
        result = os.popen('pip install -r requirements.txt').readlines()
        util.printCommandResult(result)
