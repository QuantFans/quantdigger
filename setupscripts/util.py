def download(url,target):
    import sys
    if sys.version_info.major >= 3:
        import urllib.request,re,sys
        data = urllib.request.urlopen(url).read()
    else:
        import urllib2
        data = urllib2.urlopen(url).read()
    with open(target,"wb") as code:
        code.write(data)


def decompress(target,dist):
    import tarfile
    tar = tarfile.open(target)
    names = tar.getnames()
    for name in names:
        tar.extract(name,dist)
    #tar.extractall()
    tar.close()

def decompressZip(target,dist):
    import zipfile
    f= zipfile.ZipFile(target,'r')
    for file in f.namelist():
        f.extract(file,dist)
    f.close()

def printCommandResult(result):
    for line in result:
        print(line)
