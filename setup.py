#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='calf',
    version='0.0.0',
    package_dir={'': 'src/python'},
    packages=find_packages(where='src/python'),
)
