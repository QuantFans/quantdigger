# -*- coding: utf8 -*-
from codecs import open

from setuptools import setup, find_packages

with open("README.rst", "r", "utf-8") as f:
    readme = f.read()

setup(

    name="QuantDigger",
    version="0.4.0",
    description="量化交易PYTHON回测系统",
    long_description=readme,
    author="QuantFans",
    author_email="dingjie.wang@foxmail.com",
    license="MIT",
    url="https://github.com/QuantFans/quantdigger",
    packages=find_packages(exclude=['tests', 'demo', "requirements", "images"]),
    include_package_data=True,
    install_requires=[
        "numpy>=1.10.4",
        "pandas>=1.17.0",
        "logbook>=0.12.5",
        "matplotlib>=1.5.1",
        "python-dateutil>=2.4.2",
        "ta-lib>=0.4.8"
    ],
    classifiers=[
        'Environment :: Finance',
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
    ],
    zip_safe=False,
)
