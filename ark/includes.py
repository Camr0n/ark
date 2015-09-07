# --------------------------------------------------------------------------
# Loads and processes strings from the site's inc directory.
# --------------------------------------------------------------------------

import os

from . import utils
from . import renderers
from . import site


# Stores rendered include strings.
_includes = None


# Returns a dictionary of rendered includes.
def includes():
    global _includes
    if _includes is None:
        _includes = {}
        if os.path.isdir(site.inc()):
            for finfo in utils.srcfiles(site.inc()):
                text, _ = utils.load(finfo.path)
                _includes[finfo.base] = renderers.render(text, finfo.ext)
    return _includes
