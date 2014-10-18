"""
Malt: a static website generator in Python 3.

Usage:

    $ malt <source-dir> <dst-dir> <theme-dir>

License: This work has been placed in the public domain.

"""

__version__ = '0.6.1'


import sys


if sys.version_info < (3, 2):
    sys.exit('Error: Malt requires Python >= 3.2.')


try:
    import yaml
except ImportError:
    sys.exit('Error: Malt requires the PyYAML module.')


try:
    import markdown
except ImportError:
    sys.exit('Error: Malt requires the Markdown module.')


import argparse
import os

from . import build
from . import utils


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
