# --------------------------------------------------------------------------
# Ark: a static website generator in Python 3.
#
# Ark transforms a directory of text files written in Syntex or Markdown
# into a static website that can be viewed locally or served remotely.
#
# Author: Darren Mulholland <dmulholland@outlook.ie>
# License: Public Domain
# --------------------------------------------------------------------------

import sys


# Ark requires at least Python 3.2.
if sys.version_info < (3, 2):
    sys.exit('Error: Ark requires Python >= 3.2.')


# Template for error messages informing the user of any missing libraries.
error = """Error: Ark requires the %s library. Try:

    $ pip install %s"""


# Check that all the application's dependencies are available.
try:
    import yaml
except ImportError:
    sys.exit(error % ('PyYaml', 'pyyaml'))


try:
    import markdown
except ImportError:
    sys.exit(error % ('Markdown', 'markdown'))


try:
    import syntex
except ImportError:
    sys.exit(error % ('Syntex', 'syntex'))


try:
    import ibis
except ImportError:
    sys.exit(error % ('Ibis', 'ibis'))


try:
    import pygments
except ImportError:
    sys.exit(error % ('Pygments', 'pygments'))


try:
    import clio
except ImportError:
    sys.exit(error % ('Clio', 'pyclio'))


try:
    import shortcodes
except ImportError:
    sys.exit(error % ('Shortcodes', 'shortcodes'))


try:
    import jinja2
except ImportError:
    sys.exit(error % ('Jinja', 'jinja2'))


# We import the package's modules so users can access 'ark.foo' via a simple
# 'import ark' statement. Otherwise the user would have to import each module
# individually as 'import ark.foo'.
from . import main
from . import hooks
from . import pages
from . import records
from . import site
from . import utils
from . import meta
from . import templates
from . import renderers
from . import hashes
from . import extensions
