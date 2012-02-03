# -*- coding: utf-8 -*-
"""This is setup
"""

from distutils.core import setup

setup(
    name='CommmunityDetection',
    version='0.1.0',
    author='June Andrews',
    author_email='astuteajax@gmail.com',
    packages=['implementation'],
    scripts=['bin/temp.py'],
    url='http://pypi.python.org/pypi/CommunityDetection/',
    license='LICENSE.txt',
    description='Library of Community Detection Algorithms and Analysis',
    long_description=open('README.txt').read()
)