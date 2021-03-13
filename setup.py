#!/usr/bin/env python

from os import path

from setuptools import setup, find_namespace_packages


# Fetch the README contents
rootdir = path.abspath(path.dirname(__file__))
with open(path.join(rootdir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="calf",
    version="0.0.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["calf.*"]),
    entry_points={
        "console_scripts": [
            "calflex = calf.lexer:main",
            "calfp = calf.parser:main",
            "calfr = calf.reader:main",
            "calffmt = calf.fmt:main",
            "calf = calf.server:main",
        ]
    },
)
