# --------------------------------------------------------------------------
# Finds and loads extensions.
# --------------------------------------------------------------------------

import os
import sys
import importlib

from . import site


# Loads any Python modules found in the extensions directories.
def load():
    dirs = [os.path.join(os.path.dirname(__file__), 'ext')]
    if os.path.isdir(site.home('ext')):
        dirs.append(site.home('ext'))
    for dirpath in dirs:
        sys.path.insert(0, dirpath)
        names = [
            os.path.splitext(name)[0]
                for name in os.listdir(dirpath)
                    if not name[0] in '_.'
        ]
        for name in names:
            extension = importlib.import_module(name)
        sys.path.pop(0)
