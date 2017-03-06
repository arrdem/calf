#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='calf',
    version='0.0.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'six>=1.10.0'
    ]
)
