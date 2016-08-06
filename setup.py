#!/usr/bin/env python3
from setuptools import setup

def readme():
  with open('README.md') as rm:
    return rm.read()

setup(
    name='track-stuff',
    version='0.0.1',
    description='A library for keeping track of quantities of stuff',
    long_description=readme(),
    url='http://github.com/zstewar1/stuff',
    author='Zachary Stewart',
    author_email='zachary@zstewart.com',
    packages=['stuff'],
    test_suite='stuff.tests',
)
