#!/usr/bin/env python3
"""
Ark
===

Ark is a static website generator in Python. It transforms a directory of
text files into a self-contained website that can be viewed locally or
served remotely.

* `Documentation <http://mulholland.xyz/docs/ark/>`_
* `Sample Site <http://ark.mulholland.xyz>`_
* `Github Homepage <https://github.com/dmulholland/ark>`_

"""

import os
import re
import io

from setuptools import setup, find_packages


filepath = os.path.join(os.path.dirname(__file__), 'ark', 'meta.py')
with io.open(filepath, encoding='utf-8') as metafile:
    regex = r'''^__([a-z]+)__ = ["'](.*)["']'''
    meta = dict(re.findall(regex, metafile.read(), flags=re.MULTILINE))


setup(
    name = 'ark',
    version = meta['version'],
    packages =  find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'ark = ark.main:main',
        ],
    },
    install_requires = [
        'markdown',
        'pygments',
        'pyyaml',
        'syntex',
        'ibis',
        'shortcodes',
        'pyclio',
        'jinja2',
    ],
    author = 'Darren Mulholland',
    url='https://github.com/dmulholland/ark',
    license = 'Public Domain',
    description = 'A static website generator.',
    long_description = __doc__,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: Public Domain',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)
