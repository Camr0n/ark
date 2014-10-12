"""
Malt: a static website generator in Python 3.

Usage:

    $ malt <source-dir> <dst-dir> <theme-dir>

License: This work has been placed in the public domain.

"""

import argparse
import os
import sys

from . import build
from . import utils


try:
    import yaml
except ImportError:
    sys.exit('Error: Malt requires PyYAML.')


__version__ = '0.5.0'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('source',
        help = 'source directory',
        type = os.path.abspath,
    )
    parser.add_argument('destination',
        help = 'destination directory',
        type = os.path.abspath,
    )
    parser.add_argument('theme',
        help = 'theme directory or name of bundled theme',
    )
    parser.add_argument('-V', '--version',
        action='version',
        version=__version__,
    )
    parser.add_argument('-c', '--clear',
        action = 'store_true',
        help = 'clear the destination directory before building',
    )
    args = parser.parse_args()
    themes = os.path.join(os.path.dirname(__file__), 'themes')
    if args.theme in os.listdir(themes):
        args.theme = os.path.join(themes, args.theme)
    elif os.path.isdir(args.theme):
        args.theme = os.path.abspath(args.theme)
    else:
        parser.error('theme directory does not exist')
    if not os.path.isdir(args.source):
        parser.error('source directory does not exist')
    return args


def main():
    args = parse_args()
    if args.clear:
        utils.clear_directory(args.destination)
    build.build(args.source, args.destination, args.theme)
