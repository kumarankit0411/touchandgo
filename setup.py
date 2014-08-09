#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Touchandgo',
    version='0.3.3',
    author='Felipe Lerena',
    description='A python app and library to watch series magically',
    author_email='felipelerena@gmail.com',
    packages=['touchandgo'],
    scripts=[],
    url='http://github.com/felipelerena/touchandgo/',
    license='LICENSE.txt',
    long_description=open('README.rst').read(),
    install_requires=['TorrentMediaSearcher',
                      'subliminal',
                      'netifaces',
                      'flask',
                      'simplejson',
                      'python-daemon'],
    entry_points={
        'console_scripts': ['touchandgo = touchandgo.touchandgo:main',
                            'tsproxy = touchandgo.server:serve']
    },
)
