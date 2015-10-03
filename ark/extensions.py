# --------------------------------------------------------------------------
# Finds and loads extensions.
# --------------------------------------------------------------------------

import os
import sys
import importlib

from . import site


# Stores a dictionary of loaded extension modules.
_loaded = {}


# Loads any Python modules found in the extensions directories.
def load():
    dirs = []

    # Default extensions bundled with Ark.
    dirs.append(os.path.join(os.path.dirname(__file__), 'ext'))

    # Global extensions directory.
    if os.getenv('ARK_EXTENSIONS') and os.path.isdir(os.getenv('ARK_EXTENSIONS')):
        dirs.append(os.getenv('ARK_EXTENSIONS'))

    # Site-specific extensions.
    if os.path.isdir(site.ext()):
        dirs.append(site.ext())

    # Load extensions.
    for dirpath in dirs:
        sys.path.insert(0, dirpath)
        for name in os.listdir(dirpath):
            base = os.path.splitext(name)[0]
            if not base[0] in '_.':
                _loaded[base] = importlib.import_module(base)
        sys.path.pop(0)


# Returns the dictionary of loaded extension modules.
def loaded():
    return _loaded
