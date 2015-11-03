# -*- coding: utf8 -*-
import codecs
import os
import sys
import util
import platform
from distutils.util import convert_path
from fnmatch import fnmatchcase
from setuptools import setup, find_packages


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()



standard_exclude = ["*.py", "*.pyc", "*$py.class", "*~", "*.bak"]
standard_exclude_directories = [
     "_darcs", "./build", "./dist", "EGG-INFO", "*.egg-info", "*.bak"
]

def find_package_data(
    where=".",
    package="",
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):

    out = {}
    stack = [(convert_path(where), "", package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, "__init__.py"))
                    and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + "." + name
                    stack.append((fn, "", package, False))
                else:
                    stack.append((fn, prefix + name + "/", package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out


PACKAGE = "quantdigger"
NAME = "QuantDigger"
DESCRIPTION = "量化交易PYTHON回测系统"
AUTHOR = "QuantFans"
AUTHOR_EMAIL = "dingjie.wang@foxmail.com"
URL = "https://github.com/QuantFans/quantdigger"
VERSION = "0.2.1" 


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("./README.rst").decode('utf-8'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=find_packages(),
    package_data=find_package_data(PACKAGE, only_in_packages=False),
    scripts=['util.py','dependency.py','install_pip.py','install.py','install_dependency.py'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)
