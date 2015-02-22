"""
Ark: a static website generator in Python 3.

Ark transforms a directory of text files in Syntex or Markdown format into
a static website that can be viewed locally or served remotely.

License: This work has been placed in the public domain.

"""

import sys


if sys.version_info < (3, 2):
    sys.exit('Error: Ark requires Python >= 3.2.')


try:
    import yaml
except ImportError:
    sys.exit('Error: Ark requires the PyYAML module.')


try:
    import markdown
except ImportError:
    sys.exit('Error: Ark requires the Markdown module.')


try:
    import syntex
except ImportError:
    sys.exit('Error: Ark requires the Syntex module.')


try:
    import ibis
except ImportError:
    sys.exit('Error: Ark requires the Ibis module.')


try:
    import click
except ImportError:
    sys.exit('Error: Ark requires the Click module.')


try:
    import pygments
except ImportError:
    sys.exit('Error: Ark requires the Pygments module.')


from . import main
from . import hooks
from . import cli
from . import pages
from . import records
from . import site
from . import tags
from . import utils
from . import meta
