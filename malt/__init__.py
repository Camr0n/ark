"""
Malt: a static website generator in Python 3.

Usage:

    $ malt <source-dir> <dst-dir> <theme-dir>

License: This work has been placed in the public domain.

"""

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


try:
    import syntex
except ImportError:
    sys.exit('Error: Malt requires the Syntex module.')


try:
    import flock
except ImportError:
    sys.exit('Error: Malt requires the Flock module.')


try:
    import click
except ImportError:
    sys.exit('Error: Malt requires the Click module.')


from . import main
from . import hooks
from . import cli
from . import pages
from . import records
from . import site
from . import tags
from . import utils
from . import meta
