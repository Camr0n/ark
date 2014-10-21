#!/usr/bin/env python3
"""
Malt
====

Malt is a static website generator in Python 3. It transforms a directory
of text files written in Syntex or Markdown into a self-contained website
that can be viewed locally or served remotely.

Malt is under active development and is not yet ready for production use.

"""

import os
import re
import io

from setuptools import setup, find_packages


filepath = os.path.join(os.path.dirname(__file__), 'malt', 'meta.py')
with io.open(filepath, encoding='utf-8') as metafile:
    regex = r'''^__([a-z]+)__ = ["'](.*)["']'''
    meta = dict(re.findall(regex, metafile.read(), flags=re.MULTILINE))


setup(
    name = 'malt',
    version = meta['version'],
    packages =  find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'malt = malt.cli:cli',
        ],
    },
    install_requires = [
        'Click',
        'Markdown',
        'Pygments',
        'PyYAML',
        'syntex',
    ],
    author = 'Darren Mulholland',
    license = 'Public Domain',
    description = (
        'Static website generator.'
    ),
    long_description = __doc__,
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'License :: Public Domain',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)
