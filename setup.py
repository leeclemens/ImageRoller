#!/usr/bin/env python
# The MIT License (MIT)
#
# Copyright (c) 2015 Lee Clemens Computing Services, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import shutil

from setuptools import find_packages
from setuptools import setup

if not os.path.exists('build'):
    os.mkdir('build')
shutil.copyfile('imageroller/main.py', 'build/imageroller')

setup(
    name='imageroller',
    version='0.9.0',
    description='Rackspace Server Image Creator',
    long_description="""
    A simple backup utility utilizing saved images
     for Rackspace virtual machines.

    Allows for the configuration of multiple servers
     with varying retention specifications

    Can easily be scheduled via crond, etc to maintain a number
     of images/retention for your Rackspace hosted servers
    """,
    author='Lee Clemens Computing Services, LLC',
    author_email='github@lc-cs.com',
    url='https://lc-cs.com/',
    license='MIT',
    packages=find_packages(
        exclude=['tests', ]
    ),
    entry_points={
        'console_scripts': [
            'imageroller = imageroller.main:main_func',
        ],
    },
    setup_requires=[],
    install_requires=[
        'requests',
        'urllib3', ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: Utilities',
    ]
)
