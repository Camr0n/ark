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
    dirs = [os.path.join(os.path.dirname(__file__), 'ext')]
    if os.path.isdir(site.ext()):
        dirs.append(site.ext())
    for dirpath in dirs:
        sys.path.insert(0, dirpath)
        names = [
            os.path.splitext(name)[0]
                for name in os.listdir(dirpath)
                    if not name[0] in '_.'
        ]
        for name in names:
            _loaded[name] = importlib.import_module(name)
        sys.path.pop(0)


# Returns the dictionary of loaded extension modules.
def loaded():
    return _loaded
